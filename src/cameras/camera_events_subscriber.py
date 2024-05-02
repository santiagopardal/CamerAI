from src.cameras import Camera


class CameraEventsSubscriber:
    def on_recording_status_switched(self, camera: Camera, recording: bool):
        ...

    def on_sensitivity_update(self, camera: Camera, sensitivity: float):
        ...

