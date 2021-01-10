from kivy.uix.screenmanager import Screen
from GUI.Image import KivyCV
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from Constants import FRAMERATE


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

    def schedule_update(self):
        self._scheduled_update = True
        self._update_event = Clock.schedule_interval(self._update_images, 1.0 / FRAMERATE)

    def unschedule_update(self):
        self._scheduled_update = False
        self._update_event.cancel()

    def display(self):
        self.schedule_update()

    def hide(self):
        self.unschedule_update()

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
        super().display()

        for image in self._images:
            self._layout.add_widget(image)

    def hide(self):
        super().hide()

        for image in self._images:
            image: KivyCV
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
        super().display()
        self._layout.add_widget(self._images[0])

    def hide(self):
        super().hide()
        self._layout.remove_widget(self._images[0])