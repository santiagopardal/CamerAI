import cv2
from src.media import Frame
from src import constants
import numpy as np
from src.media.frame_editor import resize_frame, black_and_white


class Observer:
    def __init__(self, model_factory):
        self._model = model_factory.create_model()

    def observe(self, frames: list) -> list:
        pass

    def frames_to_buffer(self) -> int:
        pass

    def _frame_manipulation(self, frame: Frame) -> Frame:
        return frame

    def _prepare_for_cnn(self, pf: Frame, frm: Frame) -> np.ndarray:
        p_frame = self._frame_manipulation(pf)
        p_frame = black_and_white(resize_frame(p_frame.frame, constants.RESOLUTION))

        frm = self._frame_manipulation(frm)
        frm = black_and_white(resize_frame(frm.frame, constants.RESOLUTION))

        return np.array(cv2.absdiff(p_frame, frm) / 255, dtype="float32").reshape(constants.CNN_INPUT_SHAPE)

    def _batch_movement_check(self, frames: list) -> list:
        images = [self._prepare_for_cnn(pf, frm) for pf, frm in frames]
        movements = self._model.predict_on_batch(images)
        return [movement >= constants.MOVEMENT_SENSITIVITY for movement in movements]

    def _movement(self, previous_frame: Frame, frame: Frame) -> bool:
        image = self._prepare_for_cnn(previous_frame, frame)
        return self._model.predict(image) >= constants.MOVEMENT_SENSITIVITY
