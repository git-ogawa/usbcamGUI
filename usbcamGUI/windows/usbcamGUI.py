#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" GUI tool for displaying fraem from usb camera.
"""
import sys
import signal
import re
import argparse
import platform

from PySide2.QtWidgets import QApplication

from mainwindow import Window



class SignalHandle():
    """set default handler called when catch signal.
    """
    @staticmethod
    def set_default_handler():
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        #signal.signal(signal.SIGTSTP, signal.SIG_DFL)
        #signal.signal(signal.SIGQUIT, signal.SIG_DFL)


def get_os() -> str:
    os = platform.platform()
    if re.search("linux", os, re.IGNORECASE):
        if re.search("armv", os, re.IGNORECASE):
            return "raspi"
        else:
            return "linux"
    elif re.search("windows", os, re.IGNORECASE):
        return "windows"
    else:
        return "Unknown type"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="GUI tool for USB camera",
        formatter_class=argparse.RawTextHelpFormatter
        )
    parser.add_argument(
        '-c',
        '--camera',
        type=str,
        default="usb_cam",
        help='The kind of camera connected to PC.',
        choices=["usb_cam", "uvcam", "raspi"]
    )
    parser.add_argument(
        '-d',
        '--device',
        type=int,
        default=0,
        help='Device number of connected camere (it means X in /dev/videoX).'
    )
    parser.add_argument(
        '--dir',
        type=str,
        default=".",
        help="A directory where the saved image and video are stored",
    )
    parser.add_argument(
        '-e',
        '--ext',
        type=str,
        default="png",
        help='Image format of frame to save.',
        choices=["png", "jpg", "pgm"]
    )
    parser.add_argument(
        '-col',
        '--color',
        type=str,
        default="rgb",
        help='The color format of read frame. Defaults to RGB.',
        choices=["rgb", "gray"]
    )
    parser.add_argument(
        '-p',
        '--param',
        type=str,
        default="full",
        help='Set a list of camera parameter that can be changed by GUI.',
        choices=["minimum", "full"]
    )

    args = parser.parse_args()

    app = QApplication(sys.argv)
    SignalHandle.set_default_handler()
    main_window = Window(
        args.device,
        args.ext,
        args.camera,
        args.color,
        args.dir,
        args.param
    )
    main_window.show()
    sys.exit(app.exec_())

