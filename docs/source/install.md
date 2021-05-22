# Installation

The program is single python script so that you just clone the repository in your local machine by `git clone`. 
```bash
git clone https://github.com/git-ogawa/usbcamGUI.git
```
However, you need install the dependent packages. If you haven't installed the packages in requirements yet, can install them with pip
```bash
pip install git+https://github.com/git-ogawa/usbcamGUI
```

If you use the Debian-based OS, it also needs `v4l2` so install with apt. If windows, don't need to install.

```bash
sudo apt install v4l-util
```

## Installation on Raspberry Pi
The error message will be shown by executing `pip install git+https://github.com/git-ogawa/usbcamGUI`
```
No matching distribution found for PySide2>=5.12.0 (from usbcamGUI==1.0.0)`
```
Apparently `Pyside2` cannot be installed with pip on Raspberry pi OS, so install with apt by the following command
```bash
sudo apt install python3-pyside2.qt3dcore python3-pyside2.qt3dinput python3-pyside2.qt3dlogic python3-pyside2.qt3drender python3-pyside2.qtcharts python3-pyside2.qtconcurrent python3-pyside2.qtcore python3-pyside2.qtgui python3-pyside2.qthelp python3-pyside2.qtlocation python3-pyside2.qtmultimedia python3-pyside2.qtmultimediawidgets python3-pyside2.qtnetwork python3-pyside2.qtopengl python3-pyside2.qtpositioning python3-pyside2.qtprintsupport python3-pyside2.qtqml python3-pyside2.qtquick python3-pyside2.qtquickwidgets python3-pyside2.qtscript python3-pyside2.qtscripttools python3-pyside2.qtsensors python3-pyside2.qtsql python3-pyside2.qtsvg python3-pyside2.qttest python3-pyside2.qttexttospeech python3-pyside2.qtuitools python3-pyside2.qtwebchannel python3-pyside2.qtwebsockets python3-pyside2.qtwidgets python3-pyside2.qtx11extras python3-pyside2.qtxml python3-pyside2.qtxmlpatterns python3-pyside2uic
```

## Requirements
The propgram requires `python >= 3.6`. The list of dependent packages is below. 

- numpy
- pillow
- PySide2
- Opencv >= 4.1.0


# Support

## OS
The Debian-based distributions are supported. I verified with OS below.

- ubuntu 18.04 LTS
- Raspberry Pi OS (32bit)
- Windows 10 (partially supported, experimantal)

## Camera
UVC (USB Video Class) Cameras probably are supported. I verified with cameras listed below.

- Logicool C270

`Raspberry Pi Camera module V2` on Raspberry Pi is also supported because it can be treated as a USB device with opencv.

