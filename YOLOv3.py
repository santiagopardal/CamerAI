import cv2
import numpy as np
import os

configsThreshold = 0.2
nmsThreshold = 0.4
resolution = 352
version = 3

classesFile = "./YOLO v{}/coco.names".format(str(version))
classes = []
modelConfigs = "./YOLO v{}/{}/yolov{}.cfg".format(str(version), str(resolution), str(version))
modelWeights = "./YOLO v{}/{}/yolov{}.weights".format(str(version), str(resolution), str(version))

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

    print(classesIds)
    print(confidences)

    return classesIds, confidences


def detect(frame) -> tuple:
    blob = cv2.dnn.blobFromImage(frame, 1/255, (resolution, resolution), [0, 0, 0, 0], 1,  crop=False)

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