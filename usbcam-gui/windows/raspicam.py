#!/usr/bin/env python3

import numpy as np
import cv2
from PIL import Image


class RaspiCam():

    def __init__(self, device: int = 0, width: int = 640, height: int = 480, fps: float = 30.0,
        color: str = "RGB", fourcc: str = "YUYV"):
        self.device = device
        self.width = width
        self.height = height
        self.fps = fps
        self.colorspace = color
        self.fourcc = fourcc
        self.bit_depth = 8

        self.setup()


    def setup(self):
        res = "{}x{}".format(self.width, self.height)
        self.cam = PiCamera(resolution=res)
        #self.cam.resolution(self.width, self.height)
        self.cam.framerate = self.fps
        self.get_array_func, self.iamge_format = self.set_arrayfunc()
        self.frame = self.get_array_func(self.cam)
        print(self.get_array_func)


    def set_arrayfunc(self):
        if self.fourcc == "YUYV":
            return RaspiCam.array_format["yuv"], "yuv"
        elif self.fourcc == "H264":
            return RaspiCam.array_format["h264"], "yuv"
        elif self.fourcc == "RGB3":
            return RaspiCam.array_format["rgb"], "rgb"
        else:
            return None


    def read_frame(self) -> np.ndarray:
        self.cam.capture(self.frame, "rgb")
        return self.frame
        pass


    def update_params():
        pass



def simple():
    with picamera.PiCamera() as cam:
        cam.resolution = (2592, 1944)
        frame = array.PiRGBArray(cam)
        cam.capture(frame, "rgb")
        print(frame.array)
        print(type(frame.array))
        im = Image.fromarray(frame.array)
        im.save("test.png")
#cam = picamera.PiCamera()
#cam.resolution(1200, 1200)
#cam.resolution(3280, 2464)
#print(cam.resolution)


def came():
    cam = picamera.PiCamera()
    cam.resolution = (2592, 1944)
    frame = array.PiRGBArray(cam)
    print(frame.array)
    print(type(frame.array))
    cam.capture(frame, "rgb")
    im = Image.fromarray(frame.array)
    im.save("test.png")


#simple()
#cam = RaspiCam(fourcc="YUYV")
cam = RaspiCam(fourcc="RGB3")
#cam = RaspiCam(fourcc="H264")
cam.read_frame()