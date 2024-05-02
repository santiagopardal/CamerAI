import unittest
from unittest.mock import MagicMock
from src.cameras.camera import Camera
from src.handlers import FrameHandler
from src.retrieval_strategy import LiveRetrievalStrategy
from time import sleep


class CameraUnitTest(unittest.TestCase):
    def setUp(self) -> None:
        self.frame_handler = FrameHandler()
        self.camera = Camera(
            id=1,
            ip="192.168.0.130",
            port=80,
            frame_width=1080,
            frame_height=1920,
            video_url='https://video.url',
            name="Camera 1",
            frame_rate=30,
            frames_handler=self.frame_handler
        )
        self.retrieval_strategy = LiveRetrievalStrategy(self.camera)
        self.camera.retrieval_strategy = self.retrieval_strategy

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
        """
        Tests that the screenshot method returs the correct value, that receive updates that value and send that frame
        to the frame handler, and finally that if we stop receiving video, the correct procedure is executed.
        """
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
        """
        Tests that the correct procedure is executed when we start and stop recording.
        """
        self.frame_handler.add_motion_handler = MagicMock()
        self.frame_handler.start = MagicMock()
        self.frame_handler.stop = MagicMock()
        self.frame_handler.set_motion_handlers = MagicMock()

        self.camera.record()
        self.camera.stop_recording()

        self.frame_handler.add_motion_handler.assert_called_once()
        self.frame_handler.start.assert_called_once()
        self.frame_handler.add_motion_handler.assert_called_once()
        self.frame_handler.stop.assert_called_once()

    def test_receive_frame_does_not_crash_on_exception_thrown_by_strategy_or_frame_handler(self):
        """
        Tests that if retrieve crashes, the retrieval of frames will not crash.
        """
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
        """
        Test that __equal__ works as expected when two cameras are equal.
        """
        camera_2 = Camera(
            id=1,
            ip="192.168.0.130",
            port=80,
            frame_width=1080,
            frame_height=1920,
            video_url='https://video.url',
            name="Camera 1",
            frame_rate=30,
            frames_handler=self.frame_handler
        )
        self.assertEqual(self.camera, camera_2)

    def test_cameras_not_equal(self):
        """
        Test that __equal__ works as expected when two cameras are not equal.
        """
        camera_2 = Camera(
            id=1,
            ip="192.168.0.133",
            port=80,
            frame_width=1080,
            frame_height=1920,
            video_url="http://camera1.screenshot.local",
            name="Camera 1",
            frame_rate=30,
            frames_handler=self.frame_handler
        )
        self.assertNotEqual(self.camera, camera_2)

    def test_setters(self):
        """
        Tests that the setters and getters work as expected.
        """
        self.camera.ip = "123.456.789.101"
        self.camera.port = 9999
        self.assertEqual(self.camera.ip, "123.456.789.101")
        self.assertEqual(self.camera.port, 9999)

    def test_camera_is_hashable(self):
        """
        Tests that the camera is hashable by adding it to a dictionary.
        """
        my_map = {}
        my_map[self.camera] = self.camera.name
        self.assertEqual(self.camera.name, my_map[self.camera])


if __name__ == '__main__':
    unittest.main()
