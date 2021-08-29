from kivy.app import App
from src.GUI.image import KivyCV
from src.GUI.Screens import CameraScreen, MainScreen
from src.GUI.factories import CamerAIScreenManagerFactory, CamerAILayoutFactory


class CamerAI(App):
    """
    GUI for CamerAI.
    """

    def __init__(self, system, cameras: list, **kwargs):
        super().__init__(**kwargs)

        self._system = system
        self._images = [KivyCV(camera=camera, gui=self) for camera in cameras]

        self._main_screen = MainScreen(self._images)
        self._single_camera_screen = CameraScreen(self._images[0])

        self._current_screen = self._main_screen
        self._sm = None

    def build(self):
        factory = CamerAIScreenManagerFactory([self._main_screen, self._single_camera_screen])
        self._sm = factory.create()

        factory = CamerAILayoutFactory(self._sm, self, self._system)

        return factory.create()

    def on_stop(self):
        self._system.terminate()

        super().on_stop()

    def on_pause(self):
        for image in self._images:
            image.hide()

        super().on_pause()

        return True

    def on_resume(self):
        self.go_to_main()

        super().on_resume()

    def open_camera(self, camera: KivyCV):
        """
        Changes the view to only display one camera.
        :param camera: Camera to display.
        """
        self._current_screen.hide()

        self._single_camera_screen.image = camera
        self._single_camera_screen.display()
        self._sm.switch_to(self._single_camera_screen, direction="left")
        self._current_screen = self._single_camera_screen

    def go_to_main(self):
        """
        Goes back to the main screen displaying all cameras.
        """
        self._current_screen.hide()

        screen = self._main_screen
        screen.display()
        self._sm.switch_to(screen, direction="right")
        self._current_screen = screen

    def freeze(self):
        """
        Stops updating all cameras images.
        """
        for camera in self._images:
            camera.hide()

    def unfreeze(self):
        """
        Starts updating all cameras images.
        """
        for camera in self._images:
            camera.display()
