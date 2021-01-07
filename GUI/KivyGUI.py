from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from GUI.Image import KivyCV


class CamerAI(App):
    def __init__(self, system, cameras: list, **kwargs):
        super().__init__(**kwargs)

        self.images = [KivyCV(camera=camera) for camera in cameras]
        self._system = system

    def build(self):
        grid = GridLayout()
        grid.cols = 2

        for image in self.images:
            grid.add_widget(image)

        return grid

    def on_stop(self):
        self._system.terminate()

        super().on_stop()
