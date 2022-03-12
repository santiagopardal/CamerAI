import unittest
import src.cameras.serializer as serializer
from src.cameras.foscam.FI9803PV3 import FI9803PV3
from src.cameras.foscam.FI89182 import FI89182


class SerializerUnitTest(unittest.TestCase):
    def test_deserialization_to_FI89182(self):
        camera = serializer.deserialize({
            "id": 1,
            "ip": "192.168.0.130",
            "http_port": 80,
            "name": "Camera 1",
            "user": "admin",
            "password": "admin12345",
            "model": "FI89182"
        })
        self.assertIsInstance(camera, FI89182)
        self.assertEqual(camera.id, 1)
        self.assertEqual(camera.ip, "192.168.0.130")
        self.assertEqual(camera.port, 80)
        self.assertEqual(camera.name, "Camera 1")

    def test_deserialization_to_FI9803PV3(self):
        camera = serializer.deserialize({
            "id": 1,
            "ip": "192.168.0.130",
            "http_port": 80,
            "streaming_port": 554,
            "name": "Camera 1",
            "user": "admin",
            "password": "admin12345",
            "model": "FI9803PV3"
        })
        self.assertIsInstance(camera, FI9803PV3)
        self.assertEqual(camera.id, 1)
        self.assertEqual(camera.ip, "192.168.0.130")
        self.assertEqual(camera.port, 80)
        self.assertEqual(camera.name, "Camera 1")


if __name__ == '__main__':
    unittest.main()
