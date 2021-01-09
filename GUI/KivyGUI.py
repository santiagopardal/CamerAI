from kivy.app import App
from GUI.Image import KivyCV
from kivy.uix.screenmanager import ScreenManager
from GUI.Screens import CameraScreen, MainScreen


class CamerAI(App):
    def __init__(self, system, cameras: list, **kwargs):
        super().__init__(**kwargs)

        self._sm = ScreenManager()
        self._system = system

        self._images = [KivyCV(camera=camera, gui=self) for camera in cameras]

        self._main_screen = MainScreen(self._images)
        self._sm.add_widget(self._main_screen)
        self._main_screen.schedule_update()
        self._current_screen = self._main_screen

        self._single_camera_screen = CameraScreen(self._images[0])
        self._sm.add_widget(self._single_camera_screen)

    def build(self):
        return self._sm

    def on_stop(self):
        self._system.terminate()

        super().on_stop()

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
