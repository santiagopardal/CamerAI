import unittest
from unittest.mock import patch, MagicMock, call
from src.cameras.retrieval_strategy.live_retrieval_strategy import LiveRetrievalStrategy


def create(*args):
    if not LiveRetrievalUnitTest.mock:
        LiveRetrievalUnitTest.mock = MagicMock()
        LiveRetrievalUnitTest.mock.read = MagicMock()
        LiveRetrievalUnitTest.mock.read.return_value = True, [[0] * 3] * 4
    return LiveRetrievalUnitTest.mock


def effect(*args):
    yield Exception("Error")
    while True:
        yield None


class LiveRetrievalUnitTest(unittest.TestCase):
    mock = None

    def setUp(self) -> None:
        self.strategy = LiveRetrievalStrategy("http://camera.local/live_video", 30, 1920, 1080)

    @patch("cv2.VideoCapture.__new__", create)
    def test_connect_and_retrieve(self):
        self.strategy.connect()
        retrieved = self.strategy.retrieve()
        self.assertEqual(retrieved, [[0] * 3] * 4)

    @patch("cv2.VideoCapture.__new__", create)
    def test_retrieve_raises_exception(self):
        self.strategy.connect()
        LiveRetrievalUnitTest.mock.read.side_effect = Exception("Error")
        with self.assertRaises(Exception):
            self.strategy.retrieve()

    @patch("cv2.VideoCapture.__new__", create)
    def test_retrieve_does_not_grab_the_first_time_and_retries(self):
        self.strategy.connect()
        LiveRetrievalUnitTest.mock.read.side_effect = [(False, None), (True, [[0] * 3] * 4)]
        retrieved = self.strategy.retrieve()
        LiveRetrievalUnitTest.mock.read.assert_has_calls([call(), call()])
        self.assertEqual([[0] * 3] * 4, retrieved)

    @patch("cv2.VideoCapture.__new__", create)
    def test_disconnect(self):
        self.strategy.connect()
        LiveRetrievalUnitTest.mock.release = MagicMock()
        self.strategy.disconnect()
        LiveRetrievalUnitTest.mock.release.assert_called_once()

    @patch("cv2.VideoCapture.__new__", create)
    def test_construction_throws_exception(self):
        create()
        LiveRetrievalUnitTest.mock.set = MagicMock()
        LiveRetrievalUnitTest.mock.set.side_effect = effect()
        self.strategy.connect()


if __name__ == '__main__':
    unittest.main()
