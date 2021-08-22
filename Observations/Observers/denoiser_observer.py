from movement_detection_observer import MovementDetectionObserver
from Cameras.frame import Frame


class DenoiserObserver(MovementDetectionObserver):
    """
    DenoiserObserver does the same as MovementDetectionObserver but denoises the frames before analysing.
    This observer is more useful for cameras with low image quality.
    """
    def _frame_manipulation(self, frame: Frame) -> Frame:
        return frame.get_denoised_frame()
