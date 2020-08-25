# CamerAI

## What is CameraAI?
CameraAI is a program wich can retrieve images from CCTV cameras, display them, recognize movement, detect faces and objects.

## How does it detect movement?
There is a convolutional neural network wich is fed with the difference between two frames and returns a probability, that probability will be the number that determines whether
there's been movement or not. The sensitivity can be modified in the Constants.py file, generally with a sensitivity of 0.8 (the CNN will be at least 80% sure that
there's been movement) there will be no missing frames nor false positives, with a sensitivity of 0.5 (the CNN is 50% sure that there has been movement) there may be false positives
but no missing frames at all.

# What's the architecture of the CNN?
It's composed of:
- Convolutional layer 
    - 64 filters
    - 5x5 kernel size
    - Activation: ReLU

- MaxPool layer:
    - Pool size of 3
    - Stride of 2

- Batch Normalization

- Convolutional layer 
    - 64 filters
    - 5x5 kernel size
    - Activation: ReLU

- MaxPool layer:
    - Pool size of 3
    - Stride of 2

- Batch Normalization

- Convolutional layer 
    - 128 filters
    - 5x5 kernel size
    - Activation: ReLU

- MaxPool layer:
    - Pool size of 3
    - Stride of 2

- Batch Normalization

- Convolutional layer 
    - 256 filters
    - 5x5 kernel size
    - Activation: ReLU

- MaxPool layer:
    - Pool size of 2
    - Stride of 2

- Flattenning

- 0.5 Dropout

- Dense layer:
    - 512 neurons
    - Activation: ReLU

- Dense layer:
    - 1 neuron
    - Activation: Sigmoid

## How do we detect objects?
Objects are detected by YOLO v4, it's a pretrained
Convolutional neural network designed to detect a variety
of objects. See YOLOv4/coco.names to get the full list.

## What about the requirements?
The program can run on any OS, RAM usage can be quite large
depending on the quality of the CCTV cameras you are using,
there is a trade-off between CPU performance and RAM usage,
since in order to make the program lighter on the CPU in case
you don't have a GPU to run it modifications have been made
so as to not load the CPU too much, these modifications come at
the expense of a greater RAM usage. If you want to play with the
performance you can do so by increasing or decrasing the detection batch size
on Constants.py. Note that the DBS must be greater than 0.

# I have a GPU can I use it?
Yes, of course! Just install the requirements (requirements.txt)
and you are ready to go, maybe you will benefit from decreasing
the detection batch size.