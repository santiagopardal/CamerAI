import numpy as np
import os
import cv2

configsThreshold = 0.5
nmsThreshold = 0.6
resolution = 416

classesFile = "./YOLO v4/coco.names"
classes = []
modelConfigs = "./YOLO v4/{}/yolov4.cfg".format(str(resolution))
modelWeights = "./YOLO v4/{}/yolov4.weights".format(str(resolution))

with open(classesFile, "rt") as file:
    classes = file.read().rstrip("\n").split("\n")

yolo = cv2.dnn.readNet(modelWeights, modelConfigs, "darknet")
yolo.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
yolo.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)


def getOutputsNames(model):
    names = model.getLayerNames()

    return [names[i[0] - 1] for i in model.getUnconnectedOutLayers()]


def postprocess(outputs):
    classesIds = []
    confidences = []

    for out in outputs:
        for detection in out:
            scores = detection[5:]

            classId = np.argmax(scores)

            confidence = scores[classId]

            if confidence > configsThreshold:
                classesIds.append(classId)
                confidences.append(confidence)

    return classesIds, confidences


def detect(frame) -> tuple:
    blob = cv2.dnn.blobFromImage(frame, 1.0 / 255, (resolution, resolution), [0, 0, 0, 0], 1, crop=False)

    yolo.setInput(blob)

    outputs = yolo.forward(getOutputsNames(yolo))
    
    classesIds, confidences = postprocess(outputs)
    clssIds = [classes[classesIds[i]] for i in range(len(classesIds))]

    return clssIds, confidences


def there_is(clss: str, frame) -> bool:
    classesIds, confidences = detect(frame)
    return clss in classesIds


def find_all(classes_to_find: list, path: str):
    res = []

    if os.path.isdir(path):
        images = sorted(os.listdir(path))
        for image in images:
            img = cv2.imread(os.path.join(path, image))

            classes_found, confidences = detect(img)

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
            classes_found, confidences = detect(img)

            i = 0
            found = False
            while i < len(classes_found) and not found:
                clss = classes_found[i]
                if clss in classes_to_find:
                    res.append(path)
                    found = True
                i = i + 1

    return res