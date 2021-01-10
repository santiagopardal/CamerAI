from threading import Thread, Semaphore
from Observations.Observers import Observer, MovementDetectionObserver
import datetime
import Constants
import time
from Cameras.Frame import Frame


class Handler:
    def handle(self, event):
        """
        Handles movement.
        :param event: List of frames in which there has been movement.
        """
        pass

    def stop(self):
        """
        Cleans the handler only if needed.
        """
        pass


class MotionHandler(Handler):
    def handle(self, event: list):
        pass


class DiskStoreMotionHandler(MotionHandler):
    """
    Handles motion storing the frames on disk.
    """
    def __init__(self, storing_path, buffer_size=None):
        """
        Initializes the handler.
        :param storing_path: Folder name to which store the frames.
        :param buffer_size: If set, the frames will be stored as soon as the buffer reaches this number of frames,
        if not set, the frames will be stored as soon as they arrive to the handler.
        """
        self._frames = []

        if buffer_size:
            self._frames.append([])

        self._frames_ready = Semaphore(0)
        self._done = False
        self._storing_path = storing_path
        self._buffer_size = buffer_size

        self._background_thread = Thread(target=self._store, args=())
        self._background_thread.start()

        super().__init__()

    def handle(self, event: list):
        """
        Receives the frames and once the handler is ready stores them.
        :param event: List of frames in which there has been movement.
        """
        if event:
            if self._buffer_size:
                self._frames[0] = self._frames[0] + event

                if len(self._frames[0]) >= self._buffer_size:
                    self._frames.append([])
                    self._frames_ready.release()
            else:
                self._frames.append(event)
                self._frames_ready.release()

    def stop(self):
        """
        Stops the background thread running _store.
        """
        self._done = True
        self._frames_ready.release()
        self._background_thread.join()

    def _store(self):
        """
        Waits for frames to be ready and stores them on disk.
        """
        while not self._done:
            self._frames_ready.acquire()

            if self._frames:
                frames = self._frames.pop(0)

                for frame in frames:
                    frame.store(self._storing_path)

        while self._frames:
            frames = self._frames.pop(0)

            for frame in frames:
                frame.store(self._storing_path)


class FrameHandler(Handler):
    def __init__(self, camera, observer=None, motion_handlers=None):
        super().__init__()

        self._observer = Observer() if observer is None else observer
        self._motion_handlers = [] if motion_handlers is None else motion_handlers
        self._camera = camera
        self._thread = None
        self._kill_thread = False
        self._observe_semaphore = None
        self._frames_to_observe = []
        self._current_buffer = []
        self._current_buffer_started_receiving = None

    def start(self):
        self._observe_semaphore = Semaphore(0)
        self._current_buffer_started_receiving = time.time()
        self._thread = Thread(target=self._check_movement, args=())
        self._thread.start()

    def stop(self):
        self._kill_thread = True
        self._frames_to_observe = []
        if self._observe_semaphore is not None:
            self._observe_semaphore.release()

        if self._thread is not None:
            self._thread.join()

        for handler in self._motion_handlers:
            handler.stop()

    def set_observer(self, observer):
        if observer:
            self._observer = observer

    def handle(self, frame):
        self._current_buffer.append(frame)

        if len(self._current_buffer) >= Constants.DBS:
            end = time.time()
            true_framerate = len(self._current_buffer) / (end - self._current_buffer_started_receiving)
            self._frames_to_observe.append((self._current_buffer, true_framerate))
            self._observe_semaphore.release()
            self._current_buffer = []
            self._current_buffer_started_receiving = end

    @property
    def place(self):
        return self._camera.place

    @staticmethod
    def _calculate_time_taken(tme, frame_rate, i):
        """
        Approximates the time a frame was taken using the last time an image was received and the framerate.
        :param tme: Last time an image was received.
        :param frame_rate: Frame rate.
        :return: Time the frame was taken approximately.
        """
        return tme + datetime.timedelta(seconds=(1 / frame_rate) * i)

    def _check_movement(self):
        """
        Waits for images to be ready and tells the observer to take a look at them.
        """
        last_frame = None
        last_time_stored = None

        while not self._kill_thread:
            self._observe_semaphore.acquire()

            if self._frames_to_observe:
                """
                Create frames and calculate the time they were taken, this is done here because obtaining the time
                takes a lot of CPU time and it's not worth doing while receiving the frames from the camera. Note that
                the first frame will be the same as the last of the previous batch, so we add the previous frame so as
                to not calculate everything again, including everything needed by the observer, so the last frame
                won't be analysed by the observer until the next batch arrives and will be the first frame of that
                batch. This does not occur on the first run, in which all the frames will be analysed and the last one
                will be analysed twice, on the first run and on the second one, but will be stored only once if needed.
                """
                frames, frame_rate = self._frames_to_observe.pop(0)

                if not last_time_stored:
                    last_time_stored = datetime.datetime.now() - datetime.timedelta(
                        seconds=(Constants.DBS + 1) * (1 / frame_rate))

                frames = [Frame(frame, self._calculate_time_taken(last_time_stored, frame_rate, i+1).time())
                          for i, frame in enumerate(frames)]

                last_time_stored = self._calculate_time_taken(last_time_stored, frame_rate, len(frames))

                lf = frames[len(frames) - 1]

                if last_frame:
                    frames = [last_frame] + frames[:len(frames) - 1]

                movement = self._observer.observe(frames=frames)                       # Pass the frames to the observer

                for handler in self._motion_handlers:                                  # Handler, manage movement
                    handler.handle(movement)

                last_frame = lf                                                        # update last frame.

                del frames
                del movement


class MotionDetectorFrameHandler(FrameHandler):
    def __init__(self, camera):
        super().__init__(camera, MovementDetectionObserver(self), [DiskStoreMotionHandler(camera.place)])