import unittest
from unittest.mock import MagicMock
from src.cameras.camera import Camera
from src.handlers.frame_handler import FrameHandler


class CameraUnitTest(unittest.TestCase):
    def setUp(self) -> None:
        self.frames_handler = FrameHandler()
        self.camera = Camera(1, "192.168.0.130", 80, "Camera 1", "http://camera1.screenshot.local", 30, self.frames_handler)

    def test_set_frames_handler(self):
        frames_handler_2 = FrameHandler()

        self.frames_handler.stop = MagicMock()
        frames_handler_2.start = MagicMock()
        self.camera.set_frames_handler(frames_handler_2)
        self.frames_handler.stop.assert_called_once()
        frames_handler_2.start.assert_called_once()

    def test_record(self):
        self.frames_handler.set_observer = MagicMock()
        self.frames_handler.add_motion_handler = MagicMock()
        self.frames_handler.start = MagicMock()

        self.camera.record()

        self.frames_handler.set_observer.assert_called_once()
        self.frames_handler.add_motion_handler.assert_called_once()
        self.frames_handler.start.assert_called_once()

    def test_cameras_equal(self):
        camera_2 = Camera(1, "192.168.0.130", 80, "Camera 1", "http://camera1.screenshot.local", 30)
        self.assertEqual(self.camera, camera_2)

    def test_cameras_not_equal(self):
        camera_2 = Camera(1, "192.168.0.133", 80, "Camera 1", "http://camera1.screenshot.local", 30)
        self.assertNotEqual(self.camera, camera_2)


if __name__ == '__main__':
    unittest.main()
