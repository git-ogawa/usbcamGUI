#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import subprocess
import re
import sys
from pprint import pprint

class V4L2():

    def __init__(self, device: int = 0, width: int = 640, heigth: int = 480, fps: int = 30,
        fourcc: str = "YUYV"):
        self.device = device
        self.width = width
        self.height = heigth
        self.fps = fps
        self.fourcc = fourcc

        self.fourcc_list = []
        self.vidcap_format = []
        self.get_fourcc()
        for cc in self.fourcc_list:
            self.get_fmt_size(cc)



    def show_fourcc(self):
        cmd = ["v4l2-ctl", "-d", str(self.device), "--list-formats"]
        self.run_v4l2cmd(cmd)


    def show_all(self):
        cmd = ["v4l2-ctl", "-d", str(self.device), "--list-formats-ext"]
        self.run_v4l2cmd(cmd)


    def show_param(self):
        cmd = ["v4l2-ctl", "-d", str(self.device), "-L"]
        self.run_v4l2cmd(cmd)



    def run_v4l2cmd(self, cmd: str, stdout: bool = True):
        ret = subprocess.run(cmd, stdout=subprocess.PIPE)
        if ret.returncode:
            print("An error occured while executing v4l2 command. \nCheck if /dev/video{} exists, then reconnect the camera to PC.".format(self.device),
                file=sys.stderr)
            sys.exit(ret.returncode)
        output = ret.stdout.decode()
        if stdout:
            print(output)
        else:
            return output



    def get_fourcc(self):
        cmd = ["v4l2-ctl", "-d", str(self.device), "--list-formats"]
        ret = subprocess.run(cmd, stdout=subprocess.PIPE)
        if ret.returncode:
            print("An error occured while executing v4l2 command. \nCheck if /dev/video{} exists, then reconnect the camera to PC.".format(self.device),
                file=sys.stderr)
            sys.exit(ret.returncode)
        fmt = ret.stdout.decode()

        pixel_format = r"\s+'"
        match = re.finditer(pixel_format, fmt)
        for index, m in enumerate(match):
            start = m.end()
            end = m.end()
            while end != len(fmt):
                end += 1
                if fmt[end] == "'":
                    break
            fourcc = fmt[start:end]
            if fourcc not in self.fourcc_list:
                self.fourcc_list.append(fmt[start:end])


    def get_fmt_size(self, name):
        cmd = ["v4l2-ctl", "-d", str(self.device), "--list-framesize={}".format(name)]
        ret = subprocess.run(cmd, stdout=subprocess.PIPE)
        if ret.returncode:
            print("An error occured while executing v4l2 command. \nCheck if /dev/video{} exists, then reconnect the camera to PC.".format(self.device),
                file=sys.stderr)
            sys.exit(ret.returncode)
        ret = ret.stdout.decode()

        pattern = r"[0-9]+x[0-9]+"
        match = re.findall(pattern, ret)
        for m in match:
            width, height = map(int, m.split("x"))
            self.get_fps(name, width, height)


    def get_fps(self, name, width, height):
        cmd = [
            "v4l2-ctl",
            "-d",
            str(self.device),
            "--list-frameintervals=width={},height={},pixelformat={}".format(width, height, name)
        ]
        ret = subprocess.run(cmd, stdout=subprocess.PIPE)
        if ret.returncode:
            print("An error occured while executing v4l2 command. \nCheck if /dev/video{} exists, then reconnect the camera to PC.".format(self.device),
                file=sys.stderr)
            sys.exit(ret.returncode)
        ret = ret.stdout.decode()

        fps = "[0-9]+.[0-9]+ fps"
        fps = re.findall(fps, ret)
        for f in fps:
            fmt = (name, width, height, float(f[:-3].strip()))
            self.vidcap_format.append(fmt)
        #print(self.vidcap_format)


    def support_format_list(self):
        print("{:^10} | {:^10} | {:^10} | {:^10}".format("Fourcc", "Width", "Height", "FPS"))
        print("-" * 60)
        for i in self.vidcap_format:
            #print("-" * 60)
            print("{:^10} | {:^10} | {:^10} | {:^10}".format(*i))

        """
        with open("test.csv", "w") as f:
            for form in self.vidcap_format:
                data = ",".join(str(i) for i in form)
                f.write(data)
                f.write("\n")
        """

    def set_vidcap_format(self):
        cmd = [
            "v4l2-ctl",
            "-d",
            str(self.device),
            "--set-fmt-video=width={},height={},pixelformat={}".format(self.width, self.height, self.fourcc)
        ]
        cmd2 = [
            "v4l2-ctl",
            "-d",
            str(self.device),
            "-p",
            "{:.0f}".format(self.fps)
        ]
        for c in [cmd, cmd2]:
            ret = subprocess.run(c, stdout=subprocess.PIPE)
            if ret.returncode:
                print("An error occured while executing v4l2 command. \nCheck if /dev/video{} exists, then reconnect the camera to PC.".format(self.device),
                    file=sys.stderr)
                sys.exit(ret.returncode)


    def get_vidcap_format(self, data: str) -> list:
        buf = []
        if data == "fourcc":
            for item in self.vidcap_format:
                target = item[0]
                if target not in buf:
                    buf.append(target)
        elif data == "size":
            for item in self.vidcap_format:
                width = item[1]
                height = item[2]
                target = "{}x{}".format(width, height)
                if target not in buf:
                    buf.append(target)
        elif data == "fps":
            for item in self.vidcap_format:
                target = str(item[3])
                if target not in buf:
                    buf.append(str(target))
        else:
            return None
        return buf


if __name__ == '__main__':

    desc = '''
description'''

    epi = '''
--------------------------- example ---------------------------------

- epi
>>> python %(prog)s args
---------------------------------------------------------------------'''

    parser = argparse.ArgumentParser(
        description=desc,
        epilog=epi,
)
    args = parser.parse_args()

    v4l2 = V4L2()
    #v4l2.show_fourcc()
    #v4l2.show_all()
    v4l2.support_formt_list()