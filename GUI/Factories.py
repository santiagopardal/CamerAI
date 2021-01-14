from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager


class Factory:
    def create(self) -> Widget:
        pass


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


class MenuLayoutFactory(Factory):
    def __init__(self, gui, system):
        self._gui = gui
        self._system = system

    def create(self) -> Widget:
        button_layout = BoxLayout(orientation="horizontal")
        button_layout.size_hint_x = 1
        button_layout.size_hint_y = 0.1
        button_layout.orientation = "horizontal"

        record = RecordButton(system=self._system)
        update = DoNotUpdateGUIButton(self._gui)
        statistics = ShowStatisticsButton(self._system)

        button_layout.add_widget(record)
        button_layout.add_widget(update)
        button_layout.add_widget(statistics)

        return button_layout


class CamerAIScreenManagerFactory(Factory):
    def __init__(self, screens: list):
        self._screens = screens

    def create(self) -> Widget:
        sm = ScreenManager()

        for screen in self._screens:
            sm.add_widget(screen)

        return sm


class CamerAILayoutFactory(Factory):
    def __init__(self, screen_manager, gui, system):
        self._screen_manager = screen_manager
        self._gui = gui
        self._system = system

    def create(self) -> Widget:
        layout = BoxLayout(orientation="vertical")

        factory = MenuLayoutFactory(self._gui, self._system)
        layout.add_widget(factory.create())

        layout.add_widget(self._screen_manager)

        return layout
