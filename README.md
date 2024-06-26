# CamerAI

## 📹 What is CameraAI?
CameraAI is a program which can retrieve images from CCTV cameras recognizing movement and acting on it.

## 📚 Requirements
 - 👉 Docker: CamerAI can run on any OS that supports Docker.

## 🛠 Instalation
To install the entire project, this is, CamerAI, CamerAPI and CamerAPP simply run:

```bash
./install
```

If you decide that you don't want the API or the web app, you can just just deploy the services you want by first running the `install` script and then `docker compose up -d [camerai || camerapi || camerapp]`.
Note that if you don't want CamerAPI you also don't need the database. Keep in mind that you will need an API, so if you are not deploying CamerAPI, you will need to implement your own API.

You may want to deploy multiple nodes, even in multiple devices. To do so, you can deploy the entire system in one device and in the rest just deploy CamerAI `docker compose up -d camerai`. In that case, you'll need to modify the `.env` file that the `install` script will create for you:

 - 👉 Change the `API_URL` so that the node can hit the API.

## 🤖 How does it detect movement?
There is a convolutional neural network which is fed with the difference between two frames and returns a probability, that probability will be the number that determines whether
there's been movement or not. The sensitivity can be modified either by editing it through CamerAPP or hitting the endpoint (see CamerAPI docs).

# 🤖 What's the architecture of the CNN?
![alt text](https://github.com/santiagopardal/CamerAI/blob/master/docs/Lite%20CNN%20architecture.png)

# 💻 What about the hardware requirements?
The system can run on any OS, RAM usage can be quite large depending on the quality of the CCTV cameras you are using. There is a trade-off between CPU performance and RAM usage, in order to make the program lighter on the CPU (because the idea is to run it on low end devices such as raspberry pi) modifications have been made so as not to load the CPU too much, these modifications come at the expense of a greater RAM usage. If you want to play with the performance you can do so by increasing or decreasing the detection batch size
(DBS) on [Constants.py](https://github.com/santiagopardal/CamerAI/blob/master/Constants.py). Note that the DBS must be greater than 1.

## 🤔 How's the optimization process?
Instead of checking frame by frame whether there has been movement or not, we look for movement every DBS(s) frames, the default value is 100 DBS but you can modify it. Once
we have DBSs frames we won't be checking frame by frame, instead we will skip some of them. In the worst case scenario we will be looking

![alt text](https://github.com/santiagopardal/CamerAI/blob/master/docs/Math%20functions%20for%20CamerAI/Worst%20case/Cost%20function.png)

times for movement, where n is the DBS and b is the number of frames we will be skipping, b will be determined by the following function:

![alt text](https://github.com/santiagopardal/CamerAI/blob/master/docs/Math%20functions%20for%20CamerAI/Worst%20case/Cost%20function%20derivative%20with%20respect%20to%20b.png)

in which we want the function to be equal to 0 to find the value b for the minimum cost, as you can see, there is no
value for b in which the partial derivative with respect to b equals to 0.
The truth is that the worst case scenario is extremely unlikely to happen because movements in the real world occur "continuously" and in that case we analyse what would happen if every time we skip frames we find the contrary state to the pair previously analysed, for example movement, not movement, movement, not movement, etc. A more reasonable case would be to have a constant "m" which would be the ammount of "bursts" we have in the batch, for example for a DBS of 92, I figured out that 2 is a very reasonable number to use. Using m as another variable the functions would be:

![alt text](https://github.com/santiagopardal/CamerAI/blob/master/docs/Math%20functions%20for%20CamerAI/Average%20case/Cost%20function.png)

![alt text](https://github.com/santiagopardal/CamerAI/blob/master/docs/Math%20functions%20for%20CamerAI/Average%20case/Cost%20function%20derivative%20with%20respect%20to%20b.png)

![alt text](https://github.com/santiagopardal/CamerAI/blob/master/docs/Math%20functions%20for%20CamerAI/Average%20case/b%20value.png)

As you can see, the worst case scenario function is the same to the "average case scenario", because m=n/2b. For different environments one has to explore what is the best value for m, in my case, as I said before, 2 is a very reasonable number and reduces significantly the number of times we have to look for movement. In order to figure out the best value for m, an statistical approach would be more suitable, unfortunately I don't have the means to do it. When setting m, you have to consider the final value of b and the framerate you are going to work with, because skipping 9 frames in a camera running at 120 fps is not the same as skipping 9 frames in a comera running at 23 fps, so be careful when setting this number, ideally we would not skip frames.

Graph when using n=92 and m=2, red is cost function and green is it's partial derivative with respect to b:

![alt text](https://github.com/santiagopardal/CamerAI/blob/master/docs/Math%20functions%20for%20CamerAI/graph.png)

Some visual explanations of what's happening when using b=5:

- We find movement in two pairs in a row, we store all the images, from the first one (0) to the last one (6):

![alt text](https://github.com/santiagopardal/CamerAI/blob/master/docs/GIFS/M-M.gif)

- We find movement in the first pair of images but on the next one there is no movement, we look in the middle, there is movement so we store all the images but the last one (6).

![alt text](https://github.com/santiagopardal/CamerAI/blob/master/docs/GIFS/M-NM-M.gif)

- We find movement in the first pair of images but on the next one there is no movement, we look in the middle, and there is no movement either, so whether there is movement or not between the first pair and the next image (of the first pair) we store the first two images (0 and 1) and the next one (2).

![alt text](https://github.com/santiagopardal/CamerAI/blob/master/docs/GIFS/M-NM-NM-NM.gif)

- We don't find movement in the first pair of images but on the next one we do, we look in the middle, there is movement in all of the images, so we store all them from 0 to 6.

![alt text](https://github.com/santiagopardal/CamerAI/blob/master/docs/GIFS/NM-M-M-M.gif)

- We don't find movement in the first pair of images but on the next one we do, we look in the middle, there is movement in all of the images but the ones next to the first pair, so we store from image 2 to 6.

![alt text](https://github.com/santiagopardal/CamerAI/blob/master/docs/GIFS/NM-M-M-NM.gif)

- We find no movement in the first pair of images but on the next one there is movement, we look in the middle, there is no movement, so we store the last pair and the last image before it.

![alt text](https://github.com/santiagopardal/CamerAI/blob/master/docs/GIFS/NM-M-NM.gif)

- There is no movement in two pairs in a row, we don't store any images and we continue with the rest of the images, skipping 5 frames.

![alt text](https://github.com/santiagopardal/CamerAI/blob/master/docs/GIFS/NM-NM.gif)


## 🎮 I have a GPU can I use it?
Not if you are using the dockerized version. But if you want to, you can install the application on your host or dockerize the system using your GPU.
To install the system in your host, just install the requirements (requirements.txt) and you are ready to go, CamerAPI and CamerAPP can be dockerized. Maybe you will benefit from decreasing the detection batch size, also remember that tensorflow for GPU requires CUDA toolkit and cuDNN, [here](https://www.tensorflow.org/install/gpu) is the official tutorial to install tensorflow GPU.
