from kivy.uix.image import Image
from kivy.graphics.texture import Texture
import cv2
from kivy.uix.button import ButtonBehavior
from Cameras.Camera import Camera
from kivy.clock import Clock
from Cameras.Camera import Subscriber


class KivyCV(ButtonBehavior, Image, Subscriber):
    def __init__(self, camera, gui, **kwargs):
        super().__init__(**kwargs)

        self.nocache = True

        self._camera = camera
        self._camera.subscribe(self)
        self._my_state = OnMainScreenState(gui, self)

    @property
    def camera(self) -> Camera:
        return self._camera

    @property
    def displaying_state(self):
        return self._my_state

    @displaying_state.setter
    def displaying_state(self, state):
        self._my_state = state

    def hide(self):
        self._my_state.hide()

    def display(self):
        self._my_state.display()

    def notify(self):
        self._my_state.notify()

    def update(self, dt):
        frame = self._camera.last_frame

        frm = cv2.flip(frame, 0)
        buf = frm.tostring()
        image_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

        self.texture = image_texture

    def on_press(self):
        super().on_press()

        self._my_state.touch()


class State:
    def __init__(self, gui, image: KivyCV):
        self._gui = gui
        self._image = image

    def touch(self):
        pass

    def notify(self):
        pass

    def hide(self):
        self._image.displaying_state = HiddenState(self._gui, self._image)
        del self

    def display(self):
        pass


class OnMainScreenState(State):
    def __init__(self, gui, image: KivyCV):
        super().__init__(gui, image)
        self._trigger = Clock.create_trigger(image.update)

    def touch(self):
        self._gui.open_camera(self._image)

        self._image.displaying_state = DisplayingState(self._gui, self._image)
        del self

    def notify(self):
        self._trigger()


class DisplayingState(State):
    def __init__(self, gui, image: KivyCV):
        super().__init__(gui, image)
        self._trigger = Clock.create_trigger(image.update)

    def touch(self):
        self._gui.go_to_main()

        self._image.displaying_state = OnMainScreenState(self._gui, self._image)
        del self

    def notify(self):
        self._trigger()


class HiddenState(State):
    def __init__(self, gui, image: KivyCV):
        super().__init__(gui, image)

    def display(self):
        self._image.displaying_state = OnMainScreenState(self._gui, self._image)
        del self
