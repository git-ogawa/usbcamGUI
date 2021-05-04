usbcamGUI
=======

usbcamGUI is simple GUI python scripts operating a usb camera for Debian-based distributions, providing the capture of image, set the cam properties interactively.


# Install
Clone this repository in your local machine. then execute by `pip` in the directory where `setup.py` exists.

```
git clone https://github.com/git-ogawa/usbcamGUI.git
cd usbcamGUI
pip install .
```

## Requirements
The propgram requires `python >= 3.6`. Dependent packages are installed automatically when executimg `pip install .`

- numpy
- pillow
- PySide2
- Opencv >= 4.1.0

It also needs `v4l2` library to get lists of camera-supported information. If you does not install yet, install wtih `apt`.
```
sudo apt install v4l-util
```

# Support

## OS
The Debian-based distributions are supported.

- ubuntu 18.04 LTS
- Raspberry Pi OS (32bit)
- Windows 10 (partially supported)

## Camera
I verified with cameras listed below. `Raspberry Pi Camera module V2` is also supprted because it can be treated as a USB device with opencv.

- Logicool C270


# Usage
Connect a usb camera to PC, then start GUI by executing `usbcamGUI/linux/usbcamGUI.py`
```

python usbcamGUI.py
```

## Save the frame
Press the Save button or `Ctrl + s` to save the frame on the window. Deaults to as a `png` Can change the format by option. `png`, `jpg`, `tiff`, `pgm` are supproted.


## Change properties
The d
on the right of the window.

Whether the specified parameter is valid strongly depends on what camera you use.


## Change image size and FPS




## Switch theme
To switch the GUI color-theme, Press toggle button above the frame window or `ctrl + t`. The dark theme is set by default.







## Execute on windows
Use `usbcamGUI/windows/usbcamGUI.py` instead of `linux`. I don't know the If anyone knows how to get list of the camera supported properties (min, max, step and so on), Tell me about the information.





## Arguments

You can specify the options
```
python usbcamGUI.py <option> <value>
```

The list are also shown by `-h` option.

| Option | Description | Default | example |
| :--: | :--: | :--: | :--: |
| -c | The kind of connected camera | usb_cam | -c usb_cam |
| -d | Device index of the connected camera ( /dev/video\<index> ) | 0 | -d 1 |
| --dir | フレームを保存するディレクトリ | . | --dir image_dir |
| -e | Extension of the image to save | png | -e pgm |
| -col | Colorspace (color or gray) | rgb | -col gray |





## Troubleshooting

### libEGL warning: DRI2: failed to authenticate
If you execute the program on Raspberry Pi, this error message may be shown. The libraries `libEGL*`, `libEGL*` link to full path so that the error may be solved.
```
sudo ln -fs /opt/vc/lib/libGLESv2.so /usr/lib/arm-linux-gnueabihf/libGLESv2.so
sudo ln -fs /usr/lib/arm-linux-gnueabihf/libGLESv2.so.2 /usr/lib/arm-linux-gnueabihf/libGLESv2.so
sudo ln -fs /opt/vc/lib/libEGL.so /usr/lib/arm-linux-gnueabihf/libEGL.so
sudo ln -fs /usr/lib/arm-linux-gnueabihf/libEGL.so /usr/lib/arm-linux-gnueabihf/libEGL.so.1
```
Refer to the link https://raspberrypi.stackexchange.com/questions/61078/qt-applications-dont-work-due-to-libegl



### qt5ct: using qt5ct plugin
This is not error message and no effect for operation. If you want to suppress it, set the enviroment varibale below.
```bash
export QT_LOGGING_RULES="qt5ct.debug=false"
```

### Show  message `[Error] Input parameter is invalid !`  
This message is shown when the value is invalid. A camera does not support the specified property. or for example, the change of exposure_absolute does not work when exposure_auto set Aperture Priority mode. Turning mode to manual allow users to change the value of exposure_auto. Therefore, you try to adjust other parameters related to the specified parameter.



# Change log
- version 1.0.0