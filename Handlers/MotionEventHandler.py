from threading import Thread, Semaphore


class MotionEventHandler:
    def handle(self, event: list):
        """
        Handles movement.
        :param event: List of frames in which there has been movement.
        """
        pass


class DiskStoreMotionHandler(MotionEventHandler):
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
        self._frames = [[]]
        self._frames_ready = Semaphore(0)
        self._done = False
        self._storing_path = storing_path
        self._buffer_size = buffer_size

        thread = Thread(target=self._store, args=())
        thread.start()

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

    def _store(self):
        """
        Waits for frames to be ready and stores them on disk.
        """
        while not self._done:
            self._frames_ready.acquire()

            frames = self._frames.pop(0)

            for frame in frames:
                frame.store(self._storing_path)
