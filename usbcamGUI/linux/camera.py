#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""USB camera class
"""
import sys
import subprocess
import re
import cv2

from pathlib import Path
from datetime import datetime
from v4l import V4L2


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

        self.v4l = V4L2(self.device, parent=self)
        self.support_params = []
        for param in self.v4l.get_params("full").keys():
            self.support_params.append(param)
        self.current_params = self.v4l.get_params(self.param_type, *self.get_plist())


    def usbcam_setup(self):
        self.capture = cv2.VideoCapture(self.device)
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


    def get_plist(self):
        if self.camtype == "usb_cam":
            plist = [
                "brightness",
                "contrast",
                "saturation",
                "exposure_auto",
                "exposure_absolute"
                ]
            return plist
        elif self.camtype == "raspi":
            plist = [
                "brightness",
                "contrast",
                "saturation",
                "horizontal_flip",
                "vertical_flip",
                "exposure_time_absolute",
                "auto_exposure",
                "iso_sensitivity",
                "iso_sensitivity_auto"
            ]
            return plist
        else:
            print("no support", file=sys.stderr)
            sys.exit(-1)



    def video_write(self):
        self.video_name = self.get_filename(self.rule, self.video_suffix, self.dir)
        w = self.width
        h = self.height
        fps = int(self.fps)
        cc = cv2.VideoWriter_fourcc(*self.video_codec)
        self.video_writer = cv2.VideoWriter(self.video_name, cc, fps, (w, h))
        self.is_recording = True
        print("Start recording")
        return self.video_writer


    def set_param(self, param: str, value: int):
        ret = self.v4l.change_param(param, value)
        if ret:
            self.current_params[param]["slider_val"].setText(str(value))


    def set_default(self):
        self.v4l.set_param_default()


    def update_current_params(self, plist: list) -> dict:
        self.current_params.clear()
        self.current_params = self.v4l.get_params("set", *plist)
        return self.current_params



    def raspicam_img_format(self):
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