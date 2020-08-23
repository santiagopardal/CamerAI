# CamerAI

## What is CameraAI?
CameraAI is a program wich can retrieve images from CCTV cameras, display them, recognize movement, detect faces and objects.

## How does it detect movement?
There is a convolutional neural network wich is fed with the difference between two frames and returns a probability, that probability will be the number that determines whether
there's been movement or not. The sensitivity can be modified in the Constants.py file, generally with a sensitivity of 0.8 (the CNN will be at least 80% sure that
there's been movement) there will be no missing frames nor false positives, with a sensitivity of 0.5 (the CNN is 50% sure that there has been movement) there may be false positives
but no missing frames at all.

# What's the architecture of the CNN?
