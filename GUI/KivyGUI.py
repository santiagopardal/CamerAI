from kivy.app import App
from GUI.Image import KivyCV
from GUI.Screens import CameraScreen, MainScreen
from GUI.Factories import CamerAIScreenManagerFactory, CamerAILayoutFactory


class CamerAI(App):
    def __init__(self, system, cameras: list, **kwargs):
        super().__init__(**kwargs)

        self._system = system
        self._images = [KivyCV(camera=camera, gui=self) for camera in cameras]

        self._main_screen = MainScreen(self._images)
        self._single_camera_screen = CameraScreen(self._images[0])

        self._current_screen = self._main_screen
        self._sm = None
        self._layout = None

    def build(self):
        factory = CamerAIScreenManagerFactory([self._main_screen, self._single_camera_screen])
        self._sm = factory.create()

        factory = CamerAILayoutFactory(self._sm, self, self._system)
        self._layout = factory.create()

        return self._layout

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
        self._current_screen.hide()

        self._single_camera_screen.image = camera
        self._single_camera_screen.display()
        self._sm.switch_to(self._single_camera_screen, direction="left")
        self._current_screen = self._single_camera_screen

    def go_to_main(self):
        self._current_screen.hide()

        screen = self._main_screen
        screen.display()
        self._sm.switch_to(screen, direction="right")
        self._current_screen = screen

    def freeze(self):
        for camera in self._images:
            camera.hide()

    def unfreeze(self):
        for camera in self._images:
            camera.display()
