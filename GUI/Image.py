from kivy.uix.image import Image
from kivy.graphics.texture import Texture
import cv2
from kivy.uix.button import ButtonBehavior
from Cameras.Camera import Camera


class KivyCV(ButtonBehavior, Image):
    def __init__(self, camera, gui, **kwargs):
        super().__init__(**kwargs)

        self.nocache = True

        self._camera = camera
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

    def update(self):
        frame = self._camera.last_frame

        if frame is not None:
            frm = cv2.flip(frame, 0)
            buf = frm.tostring()
            image_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

            self.texture = image_texture

    def on_press(self):
        super().on_press()

        self._my_state.change_screen()

    def __hash__(self):
        return self._camera.__hash__()


class State:
    def change_screen(self):
        pass


class OnMainScreenState(State):
    def __init__(self, gui, image: KivyCV):
        self._gui = gui
        self._image = image

    def change_screen(self):
        self._gui.open_camera(self._image)

        ns = DisplayingState(self._gui, self._image)
        self._image.displaying_state = ns
        del self


class DisplayingState(State):
    def __init__(self, gui, image: KivyCV):
        self._gui = gui
        self._image = image

    def change_screen(self):
        self._gui.go_to_main()

        ns = OnMainScreenState(self._gui, self._image)
        self._image.displaying_state = ns
        del self
