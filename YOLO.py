import numpy as np
import os
import cv2
from Constants import YOLO_V3_CONFIGS, YOLO_V3_TINY_CONFIGS, YOLO_V3_WEIGHTS, YOLO_V3_TINY_WEIGHTS
from Constants import YOLO_V4_CONFIGS, YOLO_V4_TINY_CONFIGS, YOLO_V4_WEIGHTS, YOLO_V4_TINY_WEIGHTS
from Constants import YOLO_V4_RESOLUTION, YOLO_V4_TINY_RESOLUTION, YOLO_V3_RESOLUTION, YOLO_V3_TINY_RESOLUTION


class YOLO:
    def __init__(self, yolo, resolution):
        self._configsThreshold = 0.5
        self._nmsThreshold = 0.6
        self._classes = []
        self._resolution = resolution

        classesFile = "./YOLO v4/coco.names"

        with open(classesFile, "rt") as file:
            self._classes = file.read().rstrip("\n").split("\n")

        self._yolo = yolo

    def _get_outputs_names(self):
        names = self._yolo.getLayerNames()

        return [names[i[0] - 1] for i in self._yolo.getUnconnectedOutLayers()]

    def _postprocess(self, outputs):
        classes_ids = []
        confidences = []

        for out in outputs:
            for detection in out:
                scores = detection[5:]

                class_id = np.argmax(scores)

                confidence = scores[class_id]

                if confidence > self._configsThreshold:
                    classes_ids.append(class_id)
                    confidences.append(confidence)

        return classes_ids, confidences

    def detect(self, frame) -> tuple:
        blob = cv2.dnn.blobFromImage(frame, 1.0 / 255, (self._resolution, self._resolution),
                                     [0, 0, 0, 0], 1, crop=False)

        self._yolo.setInput(blob)

        outputs = self._yolo.forward(self._get_outputs_names())

        classesIds, confidences = self._postprocess(outputs)
        clssIds = [self._classes[classesIds[i]] for i in range(len(classesIds))]

        return clssIds, confidences

    def there_is(self, clss: str, frame) -> bool:
        classes_ids, _ = self.detect(frame)
        return clss in classes_ids

    def find_all(self, classes_to_find: list, path: str) -> list:
        res = []

        if os.path.isdir(path):
            images = sorted(os.listdir(path))
            for image in images:
                img = cv2.imread(os.path.join(path, image))

                classes_found, _ = self.detect(img)

                i = 0
                found = False
                while i < len(classes_found) and not found:
                    clss = classes_found[i]
                    if clss in classes_to_find:
                        res.append(os.path.join(path, image))
                        found = True
                    i = i + 1
        else:
            if path.endswith(".jpeg"):
                img = cv2.imread(path)
                classes_found, confidences = self.detect(img)

                i = 0
                found = False
                while i < len(classes_found) and not found:
                    clss = classes_found[i]
                    if clss in classes_to_find:
                        res.append(path)
                        found = True
                    i = i + 1

        return res


class YOLOv4(YOLO):
    def __init__(self):
        yolo = cv2.dnn.readNet(YOLO_V4_WEIGHTS, YOLO_V4_CONFIGS, "darknet")
        yolo.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        yolo.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

        super().__init__(yolo, YOLO_V4_RESOLUTION)


class YOLOv4Tiny(YOLO):
    def __init__(self):
        yolo = cv2.dnn.readNet(YOLO_V4_TINY_WEIGHTS, YOLO_V4_TINY_CONFIGS, "darknet")
        yolo.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        yolo.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

        super().__init__(yolo, YOLO_V4_TINY_RESOLUTION)


class YOLOv3(YOLO):
    def __init__(self):
        yolo = cv2.dnn.readNetFromDarknet(YOLO_V3_CONFIGS, YOLO_V3_WEIGHTS)
        yolo.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        yolo.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

        super().__init__(yolo, YOLO_V3_RESOLUTION)


class YOLOv3Tiny(YOLO):
    def __init__(self):
        yolo = cv2.dnn.readNetFromDarknet(YOLO_V3_TINY_CONFIGS, YOLO_V3_TINY_WEIGHTS)
        yolo.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        yolo.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

        super().__init__(yolo, YOLO_V3_TINY_RESOLUTION)
