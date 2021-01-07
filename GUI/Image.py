from kivy.uix.image import Image
from kivy.graphics.texture import Texture
import cv2


class KivyCV(Image):
    def __init__(self, frame=None, **kwargs):
        super().__init__(**kwargs)

        if frame is not None:
            self.update(frame)

    def update(self, frame):
        buf1 = cv2.flip(frame, 0)
        buf = buf1.tostring()
        self.texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        self.texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        print("Updated texture")