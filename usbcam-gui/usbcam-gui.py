#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" GUI tool for displaying fraem from usb camera.
"""
import sys
import signal
import argparse
from PySide2.QtWidgets import QApplication
from PySide2.QtCore import QTextStream, QFile

from BreezeStyleSheets import breeze_resources

from mainwindow import Window
from v4l import V4L2


class SignalHandle():
    """set default handler called when catch signal.
    """
    @staticmethod
    def set_default_handler():
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        signal.signal(signal.SIGTSTP, signal.SIG_DFL)
        signal.signal(signal.SIGQUIT, signal.SIG_DFL)



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
    parser.add_argument(
        '-s',
        '--show',
        help="Show a list of width, height, fourcc and FPS supported by camera.",
        action='store_true'
    )
    parser.add_argument(
        '-sa',
        '--show-all',
        help="Show the v4l2-ctl output.",
        action='store_true'
    )
    parser.add_argument(
        '-sp',
        '--show-param',
        help="Show the v4l2-ctl",
        action='store_true'
    )

    args = parser.parse_args()
    if args.show:
        v4l2 = V4L2(args.device)
        print(v4l2.support_format_list())
        parser.exit()
    elif args.show_all:
        V4L2(args.device).show_all()
        parser.exit()
    elif args.show_param:
        V4L2(args.device).show_param()
        parser.exit()


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

