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
