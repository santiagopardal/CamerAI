from kivy.app import App
from GUI.Image import KivyCV
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager
from GUI.Screens import CameraScreen, MainScreen
from kivy.uix.button import Button


class RecordButton(Button):
    def __init__(self, system, **kwargs):
        super().__init__(**kwargs)

        self.text = "Record"
        self._recording = False
        self._system = system

    def on_press(self):
        super().on_press()

        if self._recording:
            self._system.stop_recording()
            self._recording = False
            self.text = "Record"
        else:
            self._system.record()
            self._recording = True
            self.text = "Stop recording"


class DoNotUpdateGUIButton(Button):
    def __init__(self, gui, **kwargs):
        super().__init__(**kwargs)
        self._gui = gui
        self._updating = True
        self.text = "Stop updating images"

    def on_press(self):
        super().on_press()

        if self._updating:
            self._gui.freeze()
            self._updating = False
            self.text = "Update images"
        else:
            self._gui.unfreeze()
            self._updating = True
            self.text = "Stop updating images"


class ShowStatisticsButton(Button):
    def __init__(self, system, **kwargs):
        super().__init__(**kwargs)
        self._system = system
        self.text = "Show statistics"

    def on_press(self):
        super().on_press()

        self._system.create_statistics()
        self._system.show_statistics()


class CamerAI(App):
    def __init__(self, system, cameras: list, **kwargs):
        super().__init__(**kwargs)

        self._layout = BoxLayout(orientation="vertical")
        self._sm = ScreenManager()
        self._system = system

        self._images = [KivyCV(camera=camera, gui=self) for camera in cameras]

        self._main_screen = MainScreen(self._images)
        self._sm.add_widget(self._main_screen)
        self._current_screen = self._main_screen

        self._single_camera_screen = CameraScreen(self._images[0])
        self._sm.add_widget(self._single_camera_screen)

        button_layout = BoxLayout(orientation="horizontal")
        button_layout.size_hint_x = 1
        button_layout.size_hint_y = 0.1
        button_layout.orientation = "horizontal"

        record = RecordButton(system=system)
        update = DoNotUpdateGUIButton(self)
        statistics = ShowStatisticsButton(system)
        button_layout.add_widget(record)
        button_layout.add_widget(update)
        button_layout.add_widget(statistics)

        self._layout.add_widget(button_layout)
        self._layout.add_widget(self._sm)

    def build(self):
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
