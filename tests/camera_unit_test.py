import unittest
from unittest.mock import MagicMock
from src.cameras.camera import Camera
from src.handlers.frame_handler import FrameHandler
from src.cameras.retrieval_strategy.live_retrieval_strategy import LiveRetrievalStrategy
from time import sleep


class CameraUnitTest(unittest.TestCase):
    def setUp(self) -> None:
        self.frame_handler = FrameHandler()
        self.retrieval_strategy = LiveRetrievalStrategy("rtsp://camera1.com/live_video", 30, 1920, 1080)
        self.camera = Camera(1, "192.168.0.130", 80, "Camera 1", 30, self.retrieval_strategy, self.frame_handler)

    def test_construction_and_getters(self):
        """
        Tests that the construction of the Camera object is successful and correct.
        """
        self.assertEqual(1, self.camera.id)
        self.assertEqual("192.168.0.130", self.camera.ip)
        self.assertEqual(80, self.camera.port)
        self.assertEqual(30, self.camera.frame_rate)

    def test_set_frame_handler(self):
        """
        Tests that we can set a frames handler-
        :return:
        """
        frame_handler_2 = FrameHandler()

        self.frame_handler.stop = MagicMock()
        frame_handler_2.start = MagicMock()
        self.camera.frame_handler = frame_handler_2
        self.frame_handler.stop.assert_called_once()
        frame_handler_2.start.assert_called_once()
        self.assertEqual(frame_handler_2, self.camera.frame_handler)

    def test_screenshot_receive_and_stop_video(self):
        self.assertIsNone(self.camera.screenshot())

        self.retrieval_strategy.connect = MagicMock()
        self.retrieval_strategy.retrieve = MagicMock()
        self.retrieval_strategy.disconnect = MagicMock()
        self.frame_handler.handle = MagicMock()
        self.frame_handler.stop = MagicMock()
        image = [[0] * 1080] * 1920
        self.retrieval_strategy.retrieve.return_value = image

        self.camera.receive_video()
        sleep(0.01)
        self.camera.stop_receiving_video()
        sleep(0.01)

        self.assertEqual(image, self.camera.screenshot())
        self.retrieval_strategy.connect.assert_called_once()
        self.retrieval_strategy.retrieve.assert_called()
        self.frame_handler.handle.assert_called_with(image)
        self.retrieval_strategy.disconnect.assert_called_once()
        self.frame_handler.stop.assert_called_once()

    def test_record_and_stop_recording(self):
        self.frame_handler.set_observer = MagicMock()
        self.frame_handler.add_motion_handler = MagicMock()
        self.frame_handler.start = MagicMock()
        self.frame_handler.stop = MagicMock()
        self.frame_handler.set_observer = MagicMock()
        self.frame_handler.set_motion_handlers = MagicMock()

        self.camera.record()
        self.camera.stop_recording()

        self.frame_handler.set_observer.assert_called()
        self.frame_handler.add_motion_handler.assert_called_once()
        self.frame_handler.start.assert_called_once()
        self.frame_handler.add_motion_handler.assert_called_once()
        self.frame_handler.stop.assert_called_once()

    def test_receive_frame_does_not_crash_on_exception_thrown_by_strategy_or_frame_handler(self):
        self.retrieval_strategy.connect = MagicMock()
        self.retrieval_strategy.retrieve = MagicMock()
        self.retrieval_strategy.retrieve.side_effect = Exception("Error retrieving frames")
        self.retrieval_strategy.disconnect = MagicMock()
        self.frame_handler.handle = MagicMock()
        self.frame_handler.stop = MagicMock()

        self.camera.receive_video()
        sleep(0.1)
        self.camera.stop_receiving_video()
        sleep(0.1)

        self.retrieval_strategy.connect.assert_called_once()
        self.retrieval_strategy.retrieve.assert_called()
        self.retrieval_strategy.disconnect.assert_called_once()
        self.frame_handler.stop.assert_called_once()

    def test_cameras_equal(self):
        camera_2 = Camera(1, "192.168.0.130", 80, "Camera 1", "http://camera1.screenshot.local", 30)
        self.assertEqual(self.camera, camera_2)

    def test_cameras_not_equal(self):
        camera_2 = Camera(1, "192.168.0.133", 80, "Camera 1", "http://camera1.screenshot.local", 30)
        self.assertNotEqual(self.camera, camera_2)

    def test_setters(self):
        self.camera.ip = "123.456.789.101"
        self.camera.port = 9999
        self.assertEqual(self.camera.ip, "123.456.789.101")
        self.assertEqual(self.camera.port, 9999)

    def test_camera_is_hashable(self):
        my_map = {}
        my_map[self.camera] = self.camera.name
        self.assertEqual(self.camera.name, my_map[self.camera])

    def test_from_json(self):
        json = {
            "id": 1,
            "ip": "192.168.0.133",
            "http_port": 80,
            "name": "Camera 2",
            "frame_rate": 30,
            "retrieval_strategy": self.retrieval_strategy
        }
        camera = Camera.from_json(json)
        self.assertEqual(camera.id, json["id"])
        self.assertEqual(camera.port, json["http_port"])
        self.assertEqual(camera.name, json["name"])
        self.assertEqual(camera.ip, json["ip"])
        self.assertEqual(camera.ip, json["ip"])


if __name__ == '__main__':
    unittest.main()
