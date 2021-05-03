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
        self.video_ext = "avi"

        self.read_flg = True
        self.params = {}

        if self.color == "rgb":
            self.img_is_rgb = True
        else:
            self.img_is_rgb = False
        self.bit_depth = 8

        self.usbcam_setup()

        self.prop_table = [
            ["Fourcc", self.fourcc],
            ["Width", str(self.width)],
            ["Height", str(self.height)],
            ["FPS", str(self.fps)],
            ["Bit depth", str(self.bit_depth)],
            ["File save rule", self.rule]
        ]


    def usbcam_setup(self):
        self.capture = cv2.VideoCapture(self.device, cv2.CAP_DSHOW)
        if not self.capture.isOpened():
            print("cannot open /dev/video{0}. Check if /dev/video{0} exists, then reconnect the camera".format(self.device), file=sys.stderr)
            sys.exit(-1)

        if self.camtype == "uvcam":
            self.capture.set(cv2.CAP_PROP_CONVERT_RGB, 0)
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
        self.capture.release()
        self.capture = cv2.VideoCapture(self.device)

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
            ["File save rule", self.rule]
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

        # Convert image format from BGR to RGB because the channel order of read frame by
        # opencv read method is BGR.
        if self.camtype == "usb_cam":
            if self.color == "rgb":
                self.cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
            elif self.color == "gray":
                self.cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        elif self.camtype == "raspi":
            self.cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        elif self.camtype == "uvcam":
            self.cv_image = self.convert_frame(cv_image)


    def convert_frame(self, img: np.ndarray) -> np.ndarray:
        """Convert frame with 8 bit 2ch into 16 bit 1ch.

        Args:
            img (ndarray): input frame. with 8 bit 2ch.

        Returns:
            ndarray: output frame with 16 bit 1ch.
        """
        upper = img.copy()
        lower = img.copy()
        upper[:, :, 1] = 0
        lower[:, :, 0] = 0
        upper = upper.astype(np.uint16)
        lower = lower.astype(np.uint16)
        upper = upper << 8
        out = np.logical_or(upper, lower)
        out = out >> 3
        return out


    def get_params(self):
        self.params = {
            "brightness": {
                "min": 0,
                "max": 255,
                "step": 1,
                "value": 100,
                "default": 128,
            },
            "contrast": {
                "min": 0,
                "max": 255,
                "step": 1,
                "value": 100,
                "default": 128,
            },
            "saturation": {
                "min": 0,
                "max": 255,
                "step": 1,
                "value": 100,
                "default": 128,
            },
            "exposure_absolute": {
                "min": 0,
                "max": 10000,
                "step": 1,
                "value": 100,
                "default": 100,
            },
            "exposure_auto": {
                "min": 0,
                "max": 3,
                "step": 1,
                "value": 1,
                "default": 3,
            },
        }

        self.cv_param = [
            cv2.CAP_PROP_BRIGHTNESS,
            cv2.CAP_PROP_CONTRAST,
            cv2.CAP_PROP_SATURATION,
            cv2.CAP_PROP_AUTO_EXPOSURE,
            cv2.CAP_PROP_EXPOSURE
        ]

        return self.params


    def change_param(self, param, value):
        """Change a paramter value.

        This method will be called when user change a parameter by its slider.

        Args:
            value (int): Value to be set.
        """
        prop_id = self.get_cvprop(param)
        self.capture.set(prop_id, value)
        self.params[param]["slider_val"].setText(str(value))


    def get_cvprop(self, param: str) -> int:
        if param == "brightness":
            return self.cv_param[0]
        elif param == "contrast":
            return self.cv_param[1]
        elif param == "saturation":
            return self.cv_param[2]
        elif param == "exposure_absolute":
            return self.cv_param[3]
        elif param == "exposure_auto":
            return self.cv_param[4]
        else:
            return None


    def set_param_default(self):
        for param, val in self.params.items():
            default = val["default"]
            prop_id = self.get_cvprop(param)
            self.capture.set(prop_id, default)
            self.params[param]["slider"].setValue(default)
            self.params[param]["slider_val"].setText(str(default))



    def video_write(self):
        self.video_name = self.get_filename("Timestamp", self.video_ext, self.dir)
        w = self.width
        h = self.height
        fps = int(self.fps)
        cc = cv2.VideoWriter_fourcc(*"avc1")
        video = cv2.VideoWriter(self.video_name, cc, fps, (w, h))
        return video


    def raspicam_img_format(self):
        """
        lst = [
            "320x240 (QVGA)"
            "640x480 (VGA)",
            "800x600 (SVGA)"
            "1280x720 (WXGA)",
            "1640x720",
            "1640x922",
            "1920x1080 (FHD)",
            "1920x1200 (WUXGA)",
            "2560x1440 (QHD)",
            "3280x2464 (Maximum)"
        ]
        """
        lst = [
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
        return lst

    def raspicam_fps(self):
        return [str(i) for i in range(10, 91, 10)]


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