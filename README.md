usbcam-gui
=======

Usbcam-gui is simple GUI python scripts operating a usb camera for Debian-based distributions, providing the capture of image, set the cam properties interactively.


# Install
Clone this repository in your local machine. then execute by `pip` in the directory where `setup.py` exists.

```
git clone https://github.com/git-ogawa/usbcam-gui.git
cd usbcam-gui
pip install .
```


# Support
The Debian-based distributions are supported.

## OS
- ubuntu 18.04 LTS
- Raspberry Pi OS (32bit)
- Windows 10 (partially supported)

## Camera
I verified with cameras listed below. The 

- Logicool C270

`Raspberry Pi Camera module V2` is also supprted because it can be treated as a USB device with opencv.


## Requirements
The propgram requires `python >= 3.6`. installed automatically when executimg `pip install .`

- numpy
- PySide2
- Opencv >= 4.1.0

It also needs `v4l2` library to get lists of camera-supported information. If you does not install yet, install wtih `apt`.
```
sudo apt install v4l-util
```

# Usage
Connect a usb camera to PC, then start GUI by executing `usbcam-gui/usbcam-gui.py`
```
python usbcam-gui.py
```


## windows
I don't know the If anyone knows how to get list of the camera supported properties (min, max, step and so on), Tell me about the information.

## Arguments

You can specify the options
```
python usbcam-gui.py <option> <value>
```

The list are also shown by `-h` option.

| Option | Description | Default | example |
| :--: | :--: | :--: | :--: |
| -c | The kind of connected camera | usb_cam | -c usb_cam |
| -d | Device index of the connected camera ( /dev/video\<index> ) | 0 | -d 1 |
| --dir | フレームを保存するディレクトリ | . | --dir image_dir |
| -e | Extension of the image to save | png | -e pgm |
| -col | Colorspace (RGB or gray) | rgb | -col gray |



## Change properties
The d
on the right of the window.

Whether the specified parameter is valid strongly depends on what camera you use.

## Switch theme
To switch the GUI color-theme, Press toggle button above the frame window. The dark theme is set by default.

## Information


# Troubleshooting

### libEGL warning: DRI2: failed to authenticate
    - https://raspberrypi.stackexchange.com/questions/61078/qt-applications-dont-work-due-to-libegl
    - https://stackoverflow.com/questions/59928395/rapsbian-and-qt5


### qt5ct: using qt5ct plugin
This is not error message and no effect for operation. If you want to suppress it, set the enviroment varibale below.
```bash
export QT_LOGGING_RULES="qt5ct.debug=false"
```

### Show  message `[Error] Input parameter is invalid !`  
This message is shown when the value is invalid. A camera does not support the specified property. or for example, the change of exposure_absolute does not work when exposure_auto set Aperture Priority mode. Turning mode to manual allow users to change the value of exposure_auto. Therefore, you try to adjust other parameters related to the specified parameter.


# raspivid
```
mmal: mmal_vc_component_enable: failed to enable component: ENOSPC
mmal: camera component couldn't be enabled
mmal: main: Failed to create camera component
mmal: Failed to run camera app. Please check for firmware updates
```
- gpu_mem=128 into `gpu_mem=144` in `boot/config.txt`

# Change log
- version 1.0.0