#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" GUI tool for displaying fraem from usb camera.
"""
import sys
import signal
import argparse
from PySide2.QtWidgets import QApplication
from PySide2.QtCore import QTextStream, QFile

from window import Window
#from v4l import V4L2
from BreezeStyleSheets import breeze_resources


class SignalHandle():
    """set default handler called when catch signal.
    """
    @staticmethod
    def set_default_handler():
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        signal.signal(signal.SIGTSTP, signal.SIG_DFL)
        signal.signal(signal.SIGQUIT, signal.SIG_DFL)


def set_color_theme(theme):
    style = ":/{}.qss".format(theme)
    file = QFile(style)
    file.open(QFile.ReadOnly | QFile.Text)
    stream = QTextStream(file)
    app.setStyleSheet(stream.readAll())
    return style


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="GUI for USB camera",
        #formatter_class=argparse.ArgumentDefaultsHelpFormatter
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
        help='Directory where a saved frame is stored.'
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
        '-f',
        '--fps',
        type=int,
        default=30,
        help='FPS'
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
        '-he',
        '--height',
        type=int,
        default=480,
        help='Height of read frame.'
    )

    parser.add_argument(
        '-p',
        '--param',
        type=str,
        default="all",
        help='Set a list of camera parameter that can be changed by GUI.',
        choices=["minimum", "full"]
    )
    parser.add_argument(
        '-r',
        '--filename_rule',
        type=str,
        default="Sequential",
        help='this is help'
    )
    parser.add_argument(
        '-s',
        '--show',
        help="Show a list of configuratable width, height, fourcc and fps",
        action='store_true'
    )
    parser.add_argument(
        '-t',
        '--theme',
        type=str,
        default="dark",
        help='Set color theme of the main window.',
        choices=["dark", "light"]
    )
    parser.add_argument(
        '-w',
        '--width',
        type=int,
        default=640,
        help='Width of read frame'
    )

    args = parser.parse_args()
    if args.show:
        v4l2 = V4L2(args.device)
        print(v4l2.support_format_list())
        parser.exit()

    app = QApplication(sys.argv)
    SignalHandle.set_default_handler()
    style = set_color_theme(args.theme)
    mainWindow = Window(
        args.device,
        args.width,
        args.height,
        args.fps,
        args.ext,
        args.camera,
        args.color,
        args.dir,
        args.filename_rule,
        args.param
    )
    mainWindow.show()
    sys.exit(app.exec_())

