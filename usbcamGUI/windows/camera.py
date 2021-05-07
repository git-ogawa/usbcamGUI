#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Retreive frame from USB camera connected to PC  by opencv
"""
import sys
import subprocess
import re
import cv2
import numpy as np

from pathlib import Path
from datetime import datetime


class USBcam():
    """A Class to handle frame read from usb camera.
    """

    def __init__(self, device: int = 0, camtype: str = "usb_cam", color: str = "RGB",
        param: str = "full", rule=None, dst="."):
        """

        Intilizate QGraphicsItem, then set width and heigth size of read frame. self.msec means
        the time interval to switch the read frame in unit of miliseconds.
        """
        # image
        self.device = device
        self.camtype = camtype
        self.color = color
        self.rule = rule
        self.param_type = param
        self.dir = Path(dst)

        # video
        self.video_suffix = "avi"
        self.video_codec = "XVID"
        self.is_recording = False

        self.read_flg = True

        if self.color == "rgb":
            self.img_is_rgb = True
            self.ch = 3
        else:
            self.img_is_rgb = False
            self.ch = 1
        self.bit_depth = 8

        self.usbcam_setup()

        self.fourcc_list = ["YUYV", "MJPG"]
        self.current_params = {}
        self.set_params_list(self.param_type)
        self.set_fps()


    def usbcam_setup(self):
        self.capture = cv2.VideoCapture(self.device, cv2.CAP_DSHOW)
        if not self.capture.isOpened():
            print("cannot open /dev/video{0}. Check if /dev/video{0} exists, then reconnect the camera".format(self.device), file=sys.stderr)
            sys.exit(-1)

        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.get_format()


    def get_format(self):
        if self.camtype == "raspi":
            self.fourcc = "YUYV"
            self.capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*self.fourcc))
        else:
            self.fourcc = self.decode_fourcc(self.capture.get(cv2.CAP_PROP_FOURCC))
        self.width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.capture.get(cv2.CAP_PROP_FPS)
        self.size = "{}x{}".format(self.width, self.height)
        self.update_prop_table()


    def set_format(self, fourcc: str, width: int, height: int, fps: float):
        #self.capture.release()
        #self.capture = cv2.VideoCapture(self.device)

        self.capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*fourcc))
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.capture.set(cv2.CAP_PROP_FPS, fps)

        self.fourcc = self.decode_fourcc(self.capture.get(cv2.CAP_PROP_FOURCC))
        self.width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.size = "{}x{}".format(self.width, self.height)
        self.fps = self.capture.get(cv2.CAP_PROP_FPS)
        self.update_prop_table()

        print("Change frame properties")
        print("-" * 80)
        print("{:<10} : {}".format("fourcc", self.fourcc))
        print("{:<10} : {}".format("width", self.width))
        print("{:<10} : {}".format("height", self.height))
        print("{:<10} : {}".format("FPS", self.fps))
        print("-" * 80)


    def decode_fourcc(self, v: float) -> str:
        """Decode the return value.

        Args:
            v (float): [description]

        Returns:
            str: Fourcc such as YUYV, MJPG, etc.

        Examples:
            >>> decoder_fourcc(1448695129.0)
            >>> "YUYV"
        """
        v = int(v)
        return "".join([chr((v >> 8 * i) & 0xFF) for i in range(4)])


    def update_prop_table(self):
        self.prop_table = [
            ["Fourcc", self.fourcc],
            ["Width", str(self.width)],
            ["Height", str(self.height)],
            ["FPS", str(self.fps)],
            ["Bit depth", str(self.bit_depth)],
            ["Naming style", self.rule]
        ]


    def read_frame(self):
        """Read next frame from the connected camera.

        Read next frame from the connected camera by opencv Videocapture method. The read
        frame is store in self.cv_image. The self.qframe can be put into Qt scene object.

        """
        ret, cv_image = self.capture.read()
        if not ret:
            print("cannot read the next frame.", file=sys.stderr)
            sys.exit(-1)

        if self.is_recording:
            self.video_writer.write(self.cv_image)
            return True
        # Convert the order of channel from BGR to RGB
        if self.camtype == "usb_cam":
            if self.color == "rgb":
                self.cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
            elif self.color == "gray":
                self.cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        elif self.camtype == "raspi":
            self.cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)


    def set_params_list(self, type_: str = None, *plist: list = None) -> dict:
        support_params = {
            "brightness": {
                "min": 0,
                "max": 255,
                "step": 1,
                "value": 128,
                "default": 128,
            },
            "contrast": {
                "min": 0,
                "max": 255,
                "step": 1,
                "value": 32,
                "default": 32,
            },
            "saturation": {
                "min": 0,
                "max": 255,
                "step": 1,
                "value": 32,
                "default": 32,
            },
            "gain": {
                "min": 0,
                "max": 255,
                "step": 1,
                "value": 64,
                "default": 64,
            },
            "sharpness": {
                "min": 0,
                "max": 255,
                "step": 1,
                "value": 24,
                "default": 24,
            },
            #"exposure_absolute": {
            #    "min": 0,
            #    "max": 10000,
            #    "step": 1,
            #    "value": 166,
            #    "default": 166,
            #},
            #"exposure_auto": {
            #    "min": 0,
            #    "max": 3,
            #    "step": 1,
            #    "value": 3,
            #    "default": 3,
            #},
        }

        self.cv_param = [
            cv2.CAP_PROP_BRIGHTNESS,
            cv2.CAP_PROP_CONTRAST,
            cv2.CAP_PROP_SATURATION,
            cv2.CAP_PROP_GAIN,
            cv2.CAP_PROP_SHARPNESS,
            cv2.CAP_PROP_EXPOSURE,
            cv2.CAP_PROP_AUTO_EXPOSURE
        ]

        self.support_params = []
        for key in support_params.keys():
            self.support_params.append(key)

        if type_ == "set":
            self.current_params.clear()
            for p in plist:
                for param, val in support_params.items():
                    if p == param:
                        self.current_params[p] = val
        elif type_ == "full":
            self.current_params = support_params
        return self.current_params


    def set_param(self, param, value):
        """Change a paramter value.

        This method will be called when user change a parameter by its slider.

        Args:
            value (int): Value to be set.
        """
        prop_id = self.get_cvprop(param)
        self.capture.set(prop_id, value)
        self.current_params[param]["slider_val"].setText(str(value))


    def get_cvprop(self, param: str) -> int:
        if param == "brightness":
            return self.cv_param[0]
        elif param == "contrast":
            return self.cv_param[1]
        elif param == "saturation":
            return self.cv_param[2]
        elif param == "gain":
            return self.cv_param[3]
        elif param == "sharpness":
            return self.cv_param[4]
        elif param == "exposure_absolute":
            return self.cv_param[5]
        elif param == "exposure_auto":
            return self.cv_param[6]
        else:
            return None


    def set_param_default(self):
        for param, val in self.current_params.items():
            default = val["default"]
            prop_id = self.get_cvprop(param)
            self.capture.set(prop_id, default)
            self.current_params[param]["slider"].setValue(default)
            self.current_params[param]["slider_val"].setText(str(default))


    def video_write(self):
        self.video_name = self.get_filename("Timestamp", self.video_suffix, self.dir)
        w = self.width
        h = self.height
        fps = int(self.fps)
        cc = cv2.VideoWriter_fourcc(*self.video_codec)
        self.video_writer = cv2.VideoWriter(self.video_name, cc, fps, (w, h))
        return self.video_writer


    def raspicam_img_format(self):
        self.lst = [
            "320x240",
            "640x480",
            "800x600",
            "1280x720",
            "1640x720",
            "1640x922",
            "1920x1080",
            "1920x1200",
            "2560x1440",
            "3280x2464"
        ]
        return self.lst


    def set_fps(self):
        self.fps_list = [str(i) for i in range(5, 61, 5)]
        return self.fps_list


    def update_current_params(self, plist: list) -> dict:
        self.current_params.clear()
        self.current_params = self.set_params_list("set", *plist)
        return self.current_params


    def raspicam_fps(self):
        return [str(i) for i in range(10, 91, 5)]


    def format_string(self, string: str, pattern: str = "videocapture") -> str:
        user = "User Controls"
        codec = "Codec Controls"
        camera = "Camera Controls"
        jpeg = "JPEG Compression Controls"

        # index
        start, end = 0, 0

        if pattern == "videocapture":
            m1 = re.search(user, string)
            if m1:
                start = m1.end()
            m2 = re.search(codec, string)
            if m2:
                end = m2.start()
            else:
                end = -1
            s = string[start:end]
            m3 = re.search(camera, string)
            if m3:
                start = m3.end()
            else:
                return s
            m4 = re.search(jpeg, string)
            if m4:
                end = m4.start()
            else:
                return s
            s += string[start:end]
            return s


    def get_filename(self, pattern: str, ext: str, dir_: str = ".") -> str:
        if pattern == "Sequential":
            index = 0
            index_str = "{:0>5}.{}".format(index, ext)
            filename = dir_ / index_str
            while index < 100000:
                if not filename.exists():
                    break
                index += 1
                index_str = "{:0>5}.{}".format(index, ext)
                filename = dir_ / index_str
        elif pattern == "Timestamp":
            now = datetime.strftime(datetime.now(), "%y%m%d-%H%M%S")
            image = "{}.{}".format(now, ext)
            filename = Path(dir_) / image
        else:
            filename = None

        return str(filename)