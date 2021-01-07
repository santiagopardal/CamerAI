from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from GUI.Image import KivyCV
import Constants
from threading import Thread
import time
from kivy.clock import Clock


class Layout(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.cols = 2
        self.img = KivyCV()
        self.add_widget(self.img)

    def update(self, frame):
        print("updating")
        self.img.update(frame)


class MyApp(App):
    def __init__(self, system, **kwargs):
        super().__init__(**kwargs)

        self._layout = Layout()
        self._system = system
        Clock.schedule_interval(callback=self._inner_update, timeout=0.5)

    def build(self):
        return self._layout

    def _inner_update(self, dt):
        print("Hell yea")
        if self._system and self._layout:
            self._system.update_gui()

    def update(self, frame):
        self._layout.update(frame)


#PongApp().run()