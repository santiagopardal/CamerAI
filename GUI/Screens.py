from kivy.uix.screenmanager import Screen
from GUI.Image import KivyCV
from kivy.uix.gridlayout import GridLayout


class CamerAIScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def display(self):
        """
        Displays screen.
        """
        pass

    def hide(self):
        """
        Hides screen.
        """
        pass


class ScreenWithCameras(Screen):
    def __init__(self, images: list, **kwargs):
        super().__init__(**kwargs)

        self._images = images

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
        """
        Displays screen.
        """
        for image in self._images:
            image: KivyCV
            image.display()
            self._layout.add_widget(image)

    def hide(self):
        """
        Hides screen.
        """
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
        self._images.clear()
        self._images.append(image)

    def display(self):
        """
        Displays the screen.
        """
        self._layout.add_widget(self._images[0])

    def hide(self):
        """
        Hides the screen.
        """
        self._layout.remove_widget(self._images[0])