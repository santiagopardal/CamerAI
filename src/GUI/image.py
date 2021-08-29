from kivy.uix.image import Image
from kivy.graphics.texture import Texture
import cv2
from kivy.uix.button import ButtonBehavior
from Cameras.camera import Camera
from kivy.clock import Clock
from src.Observer.observer import Subscriber


class KivyCV(ButtonBehavior, Image, Subscriber):
    """
    GUI's representation of a camera, it displays live video.
    """
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
        """
        Hides the camera.
        """
        self._my_state.hide()

    def display(self):
        """
        Displays the camera.
        """
        self._my_state.display()

    def notify(self):
        """
        Calls the state to notify that a new frame is ready to be displayed.
        """
        self._my_state.notify()

    def update(self, dt):
        """
        Updates the current image to the most recent one.
        """
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
        """
        Reacts to the camera being touched or clicked by the user.
        """
        pass

    def notify(self):
        """
        Reacts to the arrival of a new frame to be displayed.
        """
        pass

    def hide(self):
        """
        Hides the camera if needed.
        """

    def display(self):
        """
        Displays the camera if needed.
        """
        pass


class OnMainScreenState(State):
    """
    State representing the camera being on main screen.
    """

    def __init__(self, gui, image: KivyCV):
        super().__init__(gui, image)
        self._trigger = Clock.create_trigger(image.update)

    def touch(self):
        """
        Tells the GUI to display only this camera and changes it's state.
        """
        self._gui.open_camera(self._image)

        self._image.displaying_state = DisplayingState(self._gui, self._image)
        del self

    def notify(self):
        """
        Updates the camera's frame.
        """
        self._trigger()

    def hide(self):
        """
        Hides the camera and changes it's state.
        """
        self._image.displaying_state = HiddenState(self._gui, self._image)
        del self


class DisplayingState(State):
    """
    State representing the camera being the only one displayed.
    """

    def __init__(self, gui, image: KivyCV):
        super().__init__(gui, image)
        self._trigger = Clock.create_trigger(image.update)

    def touch(self):
        """
        Tells the GUI to go back to main screen and changes the camera's state.
        """
        self._gui.go_to_main()

        self._image.displaying_state = OnMainScreenState(self._gui, self._image)
        del self

    def notify(self):
        """
        Updates the camera's frame.
        """
        self._trigger()

    def hide(self):
        """
        Hides the camera and changes it's state.
        """
        self._image.displaying_state = HiddenState(self._gui, self._image)
        del self


class HiddenState(State):
    """
    State that represents the camera being hidden.
    """

    def __init__(self, gui, image: KivyCV):
        super().__init__(gui, image)

    def display(self):
        """
        Displays the camera and changes it's state.
        """
        self._image.displaying_state = OnMainScreenState(self._gui, self._image)
        del self