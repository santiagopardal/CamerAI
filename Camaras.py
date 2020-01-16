from tkinter import *
import urllib.request
from PIL import Image, ImageTk
import threading
import os
import time
import gc
import numpy as np


class Camera:
    IP = ""
    port = 0
    model = ""
    placed_in = ""

    def __init__(self, i, p, m, place):
        self.IP = i
        self.port = p
        self.model = m
        self.placed_in = place
        if not os.path.exists(place):
            os.mkdir(place)
            if self.getModel() == "FI9803P V3":
                urllib.request.urlretrieve("http://" + self.getIP() + ":" + str(
                    self.getPort()) + "/cgi-bin/CGIProxy.fcgi?cmd=snapPicture2&usr=malelup&pwd=maxi7500",
                                           self.getPlace() + "/image.jpeg")
                print("http://" + self.getIP() + ":" + str(
                    self.getPort()) + "/cgi-bin/CGIProxy.fcgi?cmd=snapPicture2&usr=malelup&pwd=maxi7500",
                      self.getPlace() + "/image.jpeg")
            else:
                urllib.request.urlretrieve("http://" + self.getIP() + ":" + str(
                    self.getPort()) + "/snapshot.cgi?user=malelup&pwd=maxi7500&count=0", self.getPlace() + "/image.jpeg")
                print("http://" + self.getIP() + ":" + str(
                    self.getPort()) + "/snapshot.cgi?user=malelup&pwd=maxi7500&count=0", self.getPlace() + "/image.jpeg")

    def getIP(self):
        return self.IP

    def getPort(self):
        return self.port

    def getModel(self):
        return self.model

    def getPlace(self):
        return self.placed_in

    def equals(self, cam):
        return cam.getIP() == self.IP & cam.getPort() == self.port


frontYard1 = Camera("192.168.0.103", 90, "FI89182", "Frente1")
frontYard2 = Camera("192.168.0.14", 88, "FI9803P V3", "Frente2")
backYard1 = Camera("192.168.0.112", 85, "FI9803P V3", "Patio1")
backYard2 = Camera("192.168.0.110", 92, "FI9803P V3", "Patio2")

homeCameras = np.array([frontYard1, frontYard2, backYard1, backYard2])


class Window:
    closed = False

    def __init__(self):
        self.tk = Tk()
        self.tk.title("Camaras")
        self.tk.protocol('WM_DELETE_WINDOW', self.kill)
        self.tk.geometry("800x600")

        for camera in homeCameras:
            t = threading.Thread(target=self.show_image, args=(camera,))
            t.daemon = True
            t.start()
        self.tk.mainloop()

    def kill(self):
        self.closed = True
        self.tk.destroy()


    def update_image(self, cam):
        try:
            if cam.getModel() == "FI9803P V3":
                urllib.request.urlretrieve("http://"+cam.getIP()+":"+str(cam.getPort())+"/cgi-bin/CGIProxy.fcgi?cmd=snapPicture2&usr=malelup&pwd=maxi7500", cam.getPlace()+"/image.jpeg")
            else:
                urllib.request.urlretrieve("http://"+cam.getIP()+":"+str(cam.getPort())+"/snapshot.cgi?user=malelup&pwd=maxi7500&count=0", cam.getPlace()+"/image.jpeg")
        except Exception as e:
            print("Error", cam.getPlace() + ":", str(e))
            print("Trying again...")
            self.show_image(cam)

    # Model FI9803P V3 cgi-bin/CGIProxy.fcgi?cmd=snapPicture2&usr=[USERNAME]&pwd=[PASSWORD]
    # Model FI89182 snapshot.cgi?user=malelup&pwd=maxi7500&count=0

    def show_image(self, cam):
        img = Label()

        while not self.closed:
            start_time = time.time()
            self.update_image(cam)

            load = Image.open(cam.getPlace() + "/image.jpeg")
            load.thumbnail((1100, 360))
            render = ImageTk.PhotoImage(load)

            if cam.getPlace() == "Frente1":
                try:
                    img.configure(image=render)
                    img.image = render
                    img.grid(row=0, column=0)
                except Exception as e:
                    print("Error: " + cam.getPlace(), "Error: " + str(e))
            elif cam.getPlace() == "Frente2":
                try:
                    img.configure(image=render)
                    img.image = render
                    img.grid(row=0, column=1)
                except Exception as e:
                    print("Error: " + cam.getPlace(), "Error: " + str(e))
            elif cam.getPlace() == "Patio1":
                try:
                    img.configure(image=render)
                    img.image = render
                    img.grid(row=1, column=0)
                except Exception as e:
                    print("Error: " + cam.getPlace(), "Error: " + str(e))
            else:
                try:
                    img.configure(image=render)
                    img.image = render
                    img.grid(row=1, column=1)
                except Exception as e:
                    print("Error: " + cam.getPlace(), "Error: " + str(e))
            os.remove(cam.getPlace() + "/image.jpeg")
            gc.collect()
            print(cam.getPlace() + ": " + str(time.time() - start_time))


app = Window()
