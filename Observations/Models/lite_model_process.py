from multiprocessing import Semaphore
from collections import deque
from Observations.Models.TFLiteMovementDetector import TFLiteModelDetector


def process(frames_ready: Semaphore, results_ready: Semaphore, frame_batches: deque, results: deque, done: bool):
    model = TFLiteModelDetector()

    while not done:
        frames_ready.acquire()

        frames = frame_batches.popleft()

        movement = model.predict_on_batch(frames)
        results.append(movement)

        results_ready.release()
