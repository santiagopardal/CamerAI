from kivy.uix.image import Image
from kivy.graphics.texture import Texture
import cv2
from kivy.clock import Clock


class KivyCV(Image):
    def __init__(self, camera, **kwargs):
        super().__init__(**kwargs)
        self.nocache = True
        self._camera = camera
        Clock.schedule_interval(self.update, 1/self._camera.framerate)

    def update(self, dt):
        frame = self._camera.last_frame

        if frame is not None:
            frm = cv2.flip(frame, 0)
            buf = frm.tostring()
            image_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

            self.texture = image_texture
