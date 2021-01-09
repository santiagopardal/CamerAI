from kivy.uix.screenmanager import Screen, ScreenManager
from GUI.Image import KivyCV
from kivy.uix.gridlayout import GridLayout


class CamerAIScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def display(self):
        pass

    def hide(self):
        pass


class MainScreen(CamerAIScreen):
    def __init__(self, images: list, **kwargs):
        super().__init__(name="CamerAI", **kwargs)

        self._images = images
        self._layout = GridLayout()
        self._layout.cols = int(len(images)/2)

        for image in self._images:
            self._layout.add_widget(image)

        self.add_widget(self._layout)

    def display(self):
        for image in self._images:
            image: KivyCV
            image.schedule_frame_receival()
            self._layout.add_widget(image)

    def hide(self):
        for image in self._images:
            image: KivyCV
            image.stop_frame_receival()
            self._layout.remove_widget(image)


class CameraScreen(CamerAIScreen):
    def __init__(self, image: KivyCV, **kwargs):
        super().__init__(name="Camera screen", **kwargs)

        self._image = image

        self._layout = GridLayout()
        self._layout.cols = 1

        if not image.parent:
            self._layout.add_widget(self._image)

        self.add_widget(self._layout)

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, image):
        self._image = image

    def display(self):
        self._image.schedule_frame_receival()
        self._layout.add_widget(self._image)

    def hide(self):
        self._layout.remove_widget(self._image)