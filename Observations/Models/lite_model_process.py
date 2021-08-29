from multiprocessing import Semaphore, Value, Queue
from Observations.Models.TFLiteMovementDetector import TFLiteModelDetector


def process(frames_ready: Semaphore, results_ready: Semaphore, frame_batches: Queue, results: Queue, done: Value):
    model = TFLiteModelDetector()

    while not done.value:
        frames_ready.acquire()

        frames = frame_batches.get()

        movement = model.predict_on_batch(frames)
        results.put(movement)

        results_ready.release()
