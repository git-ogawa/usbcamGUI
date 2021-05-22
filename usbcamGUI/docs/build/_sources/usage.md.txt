# Usage
Connect a usb camera to PC, then start GUI by executing `usbcamGUI/linux/usbcamGUI.py`
```
python usbcamGUI.py
```


## Save frame
Press the `Save` button on the top or `Ctrl + s` to save frame displayed on the window. The image is saved as png and the suffix can be changed by `-p <suffix>` option (for example, `python usbcamGUI -p jpg`). The following suffixes will be acceptable.
- `png`
- `jpg`
- `pgm`
- `tiff`


The filename is determined by the `Naming style` flag. While determined automatically in Sequantial and Timestamp mode, user can choose any filename in Manual mode. Press the `Naming style` button or `Ctrl + n` to switch the next flag.

| style | example             |
| ---------- | :-----------------: |
| Sequential | 00000.png           |
| Timestamp  | [yymmdd-HHMMSS].png |
| Manual     | any                 |


When save the image, the csv file that contain the parameters is also made at the same time. In the file, each parameter is listed in the format: `[param],[value]`


## Video record (experimantal)
Press the `Record` button on the top or `Ctrl + r` to start recording. To reduce, frame in the view area **doesn't update**.


## Change parameters
The label, slider and value on the right of the window shows each adjustable parameter supported by camera. You can drag the slider to change its value. Whether the specified parameter is valid strongly depends on what camera you use. 


### Change sliders
Click Choose parameter sliders in View tab or `Ctrl + g` to see the list of parameters supported by camera. Check the items you want to set and click ok to reconstruct the layout contain the sliders of the selected parameters.

![](../../img/param.png)


## Change image size and FPS
Pressing the `Properties` button calls a dialog box to change image size and FPS. Select fourcc, size and fps you want to set, then click ok to apply the values.

![](../../img/dialog.png)


## Switch theme
To switch the GUI color-theme, Press `Light/Dark` button above the view area or `ctrl + t`. The dark theme is set by default. The files for setting style are quoted from [Alexhuszagh/BreezeStyleSheets](https://github.com/Alexhuszagh/BreezeStyleSheets)


# Arguments
Users can execute the program with options
```
python usbcamGUI.py <option> <value>
```

| Option | Description | Default | example |
| :--: | :--: | :--: | :--: |
| -c | The kind of connected camera | usb_cam | -c usb_cam |
| -d | Device index of the connected camera ( /dev/video\<index> ) | 0 | -d 1 |
| --dir | A directory where the saved image and video are stored  | . | --dir image_dir |
| -e | Extension of the image to save | png | -e pgm |
| -col | Colorspace (color or gray) | rgb | -col gray |
| -s | Show a list of width, height, fourcc and FPS supported by camera. | False | -s |
| -sa | Show a list of format supported by camera. This is output of v4l2-ctl command | False | -sa |
| -sp | Show a list of parameters supported by camera. This is output of v4l2-ctl command | False | -sp |


# Note


## Execute on Raspberry Pi
Executing `usbcamGUI/linux/usbcamGUI.py` with `-c raspi` option is recommended due to the adjustment of window layout and parameters.

```bash
python usbcamGUI.py -c raspi
```


## Execute on windows
Use `usbcamGUI/windows/usbcamGUI.py` instead of `usbcamGUI/linux/usbcamGUI.py`. Note that
- In many case, the device number 0 is connected to the internal camera. To use usb camera connected as external device, specify the device number 1 by the following (when one camera is connected to PC).
```bash
python usbcamGUI/py -d 1
```

- The number of adjustable parameters is set to minumum. I don't know how to extract the camera-supported information (parameters and its min, max, step and so on) on windows machine. If anyone knows how to get that, please tell me about the information.


# Troubleshooting

## libEGL warning: DRI2: failed to authenticate
This error message may be shown when use on Raspberry Pi. Linking the libraries `libEGL*`, `libEGL*` to full path may solve the error.
```bash
sudo ln -fs /opt/vc/lib/libGLESv2.so /usr/lib/arm-linux-gnueabihf/libGLESv2.so
sudo ln -fs /usr/lib/arm-linux-gnueabihf/libGLESv2.so.2 /usr/lib/arm-linux-gnueabihf/libGLESv2.so
sudo ln -fs /opt/vc/lib/libEGL.so /usr/lib/arm-linux-gnueabihf/libEGL.so
sudo ln -fs /usr/lib/arm-linux-gnueabihf/libEGL.so /usr/lib/arm-linux-gnueabihf/libEGL.so.1
```
Refer to the link https://raspberrypi.stackexchange.com/questions/61078/qt-applications-dont-work-due-to-libegl



## qt5ct: using qt5ct plugin
This is not error message and no effect for operation. If you want to suppress it, set the enviroment varibale below.
```bash
export QT_LOGGING_RULES="qt5ct.debug=false"
```

## [Error] Input parameter is invalid !
This message is shown when the specified parameter is invalid. There are mainly two reasons. One is that a camera you use does not support change of the parameter. The other is that you need to set flag before changing the parameter. 

For logicool c270, the change of `exposure_absolute` will not work when `exposure_auto` is set to Aperture Priority mode. Turning mode to manual allow users to change the value of `exposure_absolute`. Therefore, you should try to adjust other parameters related to the specified ones.



# Change log
- version 1.1.0
    - can change font size with combox 
    - can change the number of sliders interactively

- version 1.0.0

