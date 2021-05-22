#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Creating GUI for displaying fraem from usb camera.
"""
import sys
import signal
import argparse

from PySide2.QtWidgets import QApplication

from mainwindow import Window
from util import Utility


class SignalHandle():
    """set default handler called when catch SIGINT (ctrl+c).
    """
    @staticmethod
    def set_default_handler():
        signal.signal(signal.SIGINT, signal.SIG_DFL)


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
        choices=["usb_cam", "raspi"]
    )
    parser.add_argument(
        '-d',
        '--device',
        type=int,
        default=0,
        help='Device number of connected camere (it means <X> in /dev/video<X>).'
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
        choices=["png", "jpg", "pgm", "tiff"]
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
        help="Show a list of format supported by camera.",
        action='store_true'
    )
    parser.add_argument(
        '-sp',
        '--show-param',
        help="Show a list of parameters supported by camera.",
        action='store_true'
    )

    args = parser.parse_args()
    if args.show:
        Utility.support_format_list(args.device)
        parser.exit()
    elif args.show_all:
        Utility.show_all(args.device)
        parser.exit()
    elif args.show_param:
        Utility.show_param(args.device)
        parser.exit()

    SignalHandle.set_default_handler()
    app = QApplication(sys.argv)
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