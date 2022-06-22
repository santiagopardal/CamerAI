from src.observations.models.model import Model
from src.observations.models.tatiana import Tatiana
from src.observations.models.tflite_movement_detector import TFLiteModelDetector


# FIXME Add Tatiana lite model
def create_model() -> Model:
    try:
        import tensorflow as tf
        return Tatiana() if tf.config.list_physical_devices('GPU') else TFLiteModelDetector()
    except:
        return TFLiteModelDetector()
