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

# How do we detect objects?
Objects are detected by YOLO v4, it's a pretrained
Convolutional neural network designed to detect a variety
of objects. See YOLOv4/coco.names to get the full list.

# What about the requirements?
The program can run on any OS, RAM usage can be quite large
depending on the quality of the CCTV cameras you are using,
there is a trade-off between CPU performance and RAM usage,
in order to make the program lighter on the CPU (in case
you don't have a GPU). To run it modifications have been made
so as to not load the CPU too much, these modifications come at
the expense of a greater RAM usage. If you want to play with the
performance you can do so by increasing or decreasing the detection batch size
(DBS) on Constants.py. Note that the DBS must be greater than 0.

## How's the optimization process?
Instead of checking frame by frame whether there has been movement or not, we look for movement every
DBS(s) frames, the default value is 100 DBS but you can modify it. Once
we have DBSs frames we won't be checking frame by frame, instead we will jump
so as not to check all of them. In the worst case scenario we will be looking

![alt text](https://github.com/santiagopardal/CamerAI/blob/master/Docs%20images/Math%20functions%20for%20CamerAI/Cost%20function.png)

times for movement, where n is the DBS and b is the number of frames we will be skipping, b will be determined by the
following function:

![alt text](https://github.com/santiagopardal/CamerAI/blob/master/Docs%20images/Math%20functions%20for%20CamerAI/Cost%20function%20derivative%20with%20respect%20to%20b.png)

in which we want the function to be equal to 0 to find the value b for the minimum cost.
As a rule of thumb for any DBS >= 13, b must be 4, for DBS < 13 you must use the function to aproximate b.
You can clearly see that 4 is the selected number because the derivative of the Cost function is aproximately 0
when b is 4 (4.11 aproximately), so we find a minimum cost for the number of checks we will have to do in the batch.

Some visual explanations of what's happening when using b=4:

- We find movement in two images in a row, we store all the images, from the first one (0) to the last one (6):

![alt text](https://github.com/santiagopardal/CamerAI/blob/master/Docs%20images/GIFS/M-M.gif)

- We find movement in the first pair of images but on the next one there is no movement, we look in the middle,
there is movement and we store all the images but the last one (6).

![alt text](https://github.com/santiagopardal/CamerAI/blob/master/Docs%20images/GIFS/M-NM-M.gif)

- We find movement in the first pair of images but on the next one there is no movement, we look in the middle,
there is no movement and we store the first two images (0 and 1) and the image next to the last of our first images (2).

![alt text](https://github.com/santiagopardal/CamerAI/blob/master/Docs%20images/GIFS/M-NM-NM.gif)

- We find no movement in the first pair of images but on the next one there is movement, we look in the middle,
there is movement, then we look between the two pairs and find out there is movement between the two pairs, so we
store the images between them and the last pair.

![alt text](https://github.com/santiagopardal/CamerAI/blob/master/Docs%20images/GIFS/NM-M-M.gif)

- We find no movement in the first pair of images but on the next one there is movement, we look in the middle,
there is no movement, so we store the last pair and the last image before it.

![alt text](https://github.com/santiagopardal/CamerAI/blob/master/Docs%20images/GIFS/NM-M-NM.gif)

- There is no movement in two pairs in a row, we don't store any images and we continue with the rest of the images,
skipping 4 frames.

![alt text](https://github.com/santiagopardal/CamerAI/blob/master/Docs%20images/GIFS/NM-NM.gif)

The graph of the cost function (red) and it's derivative with respect to b (purple) when n = 100:

![alt text](https://github.com/santiagopardal/CamerAI/blob/master/Docs%20images/Math%20functions%20for%20CamerAI/n%3D100.png)

The graph of the cost function (red) and it's derivative with respect to b (purple) when n = 50:

![alt text](https://github.com/santiagopardal/CamerAI/blob/master/Docs%20images/Math%20functions%20for%20CamerAI/n%3D50.png)

The graph of the cost function in 3 dimentions:

![alt text](https://github.com/santiagopardal/CamerAI/blob/master/Docs%20images/Math%20functions%20for%20CamerAI/3d_cost_function.png)


## I have a GPU can I use it?
Yes, of course! Just install the requirements (requirements.txt)
and you are ready to go, maybe you will benefit from decreasing
the detection batch size.
