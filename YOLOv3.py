import cv2
import numpy as np
import os

configsThreshold = 0.75
nsmThreshold = 0.4

classesFile = "./YOLO v3/coco.names"
classes = []
modelConfigs = "./YOLO v3/yolov3.cfg"
modelWeights = "./YOLO v3/yolov3.weights"

with open(classesFile, "rt") as file:
    classes = file.read().rstrip("\n").split("\n")

yolo = cv2.dnn.readNetFromDarknet(modelConfigs, modelWeights)
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


def detect(frame):
    blob = cv2.dnn.blobFromImage(frame, 1/255, (416, 416), [0, 0, 0, 0], 1,  crop=False)

    yolo.setInput(blob)

    outputs = yolo.forward(getOutputsNames(yolo))

    classesIds, confidences = postprocess(outputs)
    clssIds = [classes[classesIds[i]] for i in range(len(classesIds))]

    return clssIds, confidences


def find_all(classes_to_find: list, path: str):
    res = []

    if os.path.isdir(path):
        images = sorted(os.listdir(path))
        for image in images:
            img = cv2.imread(os.path.join(path, image))

            classes_found, confidences = detect(img)

            found = False
            i = 0
            while i < len(classes_found) and not found:
                clss = classes_found[i]
                if clss in classes_to_find:
                    res.append(image)
                i = i + 1
    else:
        if path.endswith(".jpeg"):
            img = cv2.imread(path)
            classes_found, confidences = detect(img)

            for clss in classes_found:
                if clss in classes_to_find:
                    res.append(path)

    return res