from kivy.uix.screenmanager import Screen
from GUI.Image import KivyCV
from kivy.uix.gridlayout import GridLayout


class CamerAIScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def display(self):
        pass

    def hide(self):
        pass


class ScreenWithCameras(Screen):
    def __init__(self, images: list, **kwargs):
        super().__init__(**kwargs)

        self._images = images
        self._scheduled_update = False
        self._update_event = None

    def _update_images(self, dt):
        for image in self._images:
            image.update()


class MainScreen(ScreenWithCameras):
    def __init__(self, images: list, **kwargs):
        super().__init__(images=images, name="CamerAI", **kwargs)

        self._layout = GridLayout()
        self._layout.cols = int(len(images)/2)

        for image in self._images:
            self._layout.add_widget(image)

        self.add_widget(self._layout)

    def display(self):
        for image in self._images:
            image: KivyCV
            image.display()
            self._layout.add_widget(image)

    def hide(self):
        for image in self._images:
            image: KivyCV
            image.hide()
            self._layout.remove_widget(image)


class CameraScreen(ScreenWithCameras):
    def __init__(self, image: KivyCV, **kwargs):
        super().__init__(images=[image], name="Camera screen", **kwargs)

        self._layout = GridLayout()
        self._layout.cols = 1

        if not image.parent:
            self._layout.add_widget(self._image)

        self.add_widget(self._layout)

    @property
    def image(self):
        return self._images[0]

    @image.setter
    def image(self, image):
        del self._images
        self._images = [image]

    def display(self):
        self._layout.add_widget(self._images[0])

    def hide(self):
        self._layout.remove_widget(self._images[0])