from src.observations.models.model import Model
from src.observations.models.v3_model_motion_detector import V3MotionDetector
from src.observations.models.tflite_movement_detector import TFLiteModelDetector


def create_model() -> Model:
    try:
        import tensorflow as tf
        return V3MotionDetector() if tf.config.list_physical_devices('GPU') else TFLiteModelDetector()
    except:
        return TFLiteModelDetector()
