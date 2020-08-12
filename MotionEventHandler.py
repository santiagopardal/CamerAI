import time
from YOLO import YOLOv4Tiny


class MotionEventHandler:
    def __init__(self):
        pass
    
    def handle(self, event):
        pass


class NightMotionEventHandler(MotionEventHandler):
    def __init__(self):
        super(NightMotionEventHandler, self).__init__()

        self._motion_frames = {}

    def handle(self, event):
        yolo = YOLOv4Tiny()

        if yolo.there_is("person", event):
            if len(self._motion_frames) >= 1:
                times = list(self._motion_frames.values())
                motion_start = times[0]

                if time.perf_counter() - motion_start <= 10:
                    self._send_email()
                else:
                    tme = time.perf_counter()
                    i = 0
                    should_send = False
                    while i < len(times) and not should_send:
                        motion_start = times[i]

                        if tme - motion_start <= 10:
                            should_send = True
                        else:
                            self._motion_frames.pop(list(self._motion_frames.keys())[i])

                        i = i + 1

                    if should_send:
                        self._send_email()
                    else:
                        self._motion_frames[event] = time.perf_counter()
            else:
                self._motion_frames[event] = time.perf_counter()

    def _send_email(self):
        print("Sending email")