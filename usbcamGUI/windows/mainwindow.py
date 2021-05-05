#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Define classes and methods to create and show the window for displaying the frame.
"""
import re
import subprocess
from pathlib import Path
from typing import Callable
from itertools import cycle
import numpy as np
from PIL import Image

from PySide2.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QWidget, QAction,
    QPushButton, QMenu, QMenuBar, QVBoxLayout, QHBoxLayout, QStatusBar, QGridLayout,
    QMessageBox, QScrollArea, QLabel, QFrame, QTableWidget, QTableWidgetItem, QInputDialog, QDialog,
    QAbstractItemView, QSizePolicy, QFileDialog, QAbstractScrollArea, QGroupBox,
    QGraphicsPixmapItem, QSlider, QFontDialog, QDialogButtonBox
    )
from PySide2.QtGui import QIcon, QFont, QPixmap, QImage
from PySide2.QtCore import Qt, QTimer, QRect, QTextStream, QFile, QSize

from camera import USBcam
from text import MessageText
from icon import Icon
import breeze_resources


class FileIO():

    file_save_lst = [
        "Timestamp",
        "Manual",
        "Sequential",
    ]

    file_save = cycle(file_save_lst)


class Window(QMainWindow):
    """Class to create main widnow

    Create main window for displaying frame read from a connected camera. The main window
    contains memu bar, push buttons, region window, sliders and status bar. These widget
    are created and added to main window in the instance method of this class.

    """
    def __init__(self, device: int = 0, _format: str = "png", camtype: str = "usb_cam", color: str = "RGB",
        dst: str = ".", param: str = "full", rule: str = "Sequential", parent=None):
        super(Window, self).__init__(parent)
        self.frame = USBcam(device, camtype, color, param, rule, dst)
        self.camtype = camtype
        self.colorspace = color
        self.filename_rule_lst = FileIO.file_save
        self.filename_rule = FileIO.file_save_lst[-1]
        self.file_format = _format
        if self.frame.fps:
            self.msec = 1 / self.frame.fps * 1000
        else:
            self.msec = 1 / 30.0 * 1000
        self.dst = Path(dst)
        self.parent = Path(__file__).parent.resolve()

        self.is_display = True
        self.is_recording = False
        self.param_separate = False

        self.setup()


    def setup(self):
        """Setup the main window for displaying frame and widget.
        """
        self.setFocusPolicy(Qt.ClickFocus)
        self.setContentsMargins(20, 0, 20, 0)
        self.view_setup()
        self.layout_setup()
        self.image_setup()
        self.setWindowTitle("Frame")
        #w, h, _ = self.get_screensize()
        self.resize(800, 600)
        #self.resize(1024, 768)
        #self.resize(wscale * w, hscale * h)
        self.set_theme()
        self.set_timer()


    def set_theme(self):
        """Set color theme of the main window.
        """
        self.style_theme = "light"
        self.style_theme_sheet = ":/{}.qss".format(self.style_theme)
        self.switch_theme()

        self.css_sheet = self.parent / "app.css"
        with open(str(self.css_sheet), "r") as f:
            self.setStyleSheet(f.read())



    def set_timer(self):
        """Set QTimer
        """
        self.timer = QTimer()
        self.timer.setInterval(self.msec)
        self.timer.timeout.connect(self.next_frame)
        self.timer.start()


    def stop_timer(self):
        self.timer.stop()

    def start_timer(self):
        self.timer.setInterval(self.msec)
        self.timer.start()


    def view_setup(self):
        """Set view region to diplay read frame in part of the main window
        """
        self.view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        self.width = 640
        self.height = 480
        self.scene.setSceneRect(0, 0, self.width, self.height)
        self.view.setMouseTracking(True)


    def layout_setup(self):
        """Set layout of objects on the window.
        """
        self.window = QWidget()
        self.setCentralWidget(self.window)
        self.view.mouseMoveEvent = self.get_coordinates
        #self.scene.addItem(self.frame)

        self.main_layout = QHBoxLayout()
        self.window.setLayout(self.main_layout)

        self.add_actions()
        self.add_menubar()
        self.add_statusbar()
        self.button_block = self.add_buttons()
        self.slider_block = self.add_params()
        self.prop_block = self.add_prop_window()
        self.construct_layout()


    def image_setup(self):
        self.init_array = np.zeros((self.frame.width, self.frame.height, self.frame.ch))
        self.qimage = QImage(
            self.init_array,
            self.frame.width,
            self.frame.height,
            self.frame.width * self.frame.ch,
            QImage.Format_RGB888
            )
        self.pixmap = QPixmap.fromImage(self.qimage)
        self.item = QGraphicsPixmapItem(self.pixmap)


    def add_actions(self):
        """Add actions executed when press each item in the memu window.
        """
        self.save_act = self.create_action("&Save", self.save_frame, "Ctrl+s")
        self.stop_act = self.create_action("&Pause", self.stop_frame, "Ctrl+p", True)
        self.rec_act = self.create_action("&Record", self.record, "Ctrl+r", True)
        self.quit_act = self.create_action("&Quit", self.quit, "Ctrl+q")

        self.theme_act = self.create_action("Switch &Theme", self.switch_theme, "Ctrl+t")
        #self.show_paramlist_act = self.create_action("Parameters &List", self.show_paramlist, "Ctrl+l")
        self.show_shortcut_act = self.create_action("&Keybord shortcut", self.show_shortcut, "Ctrl+k")
        self.font_act = self.create_action("&Font", self.set_font, "Ctrl+f")

        self.usage_act = self.create_action("&Usage", self.usage, "Ctrl+h")
        self.about_act = self.create_action("&About", self.about, "Ctrl+a")


    def create_action(self, text: str, slot: Callable, key: str = None, checkable: bool = False,
        check_defalut: bool = False) -> QAction:
        """Create a QAction object.

        Args:
            text (str): Text shown on menu.
            slot (Callable): A method called when click the menu.
            key (str, optional): Shortcut key. Defaults to None.
            checkable (bool, optional): Add a checkbox into the menu. Defaults to False.
            check_defalut (bool, optional): Check default status. Defaults to False.

        Returns:
            QAction: PySide2 QAction
        """
        act = QAction(text)
        act.setShortcut(key)
        if checkable:
            act.setCheckable(True)
            act.setChecked(check_defalut)
            act.toggled.connect(slot)
        else:
            act.triggered.connect(slot)

        return act


    def add_menubar(self):
        """Create menu bar, then add to the main window.

        The menu bar contains "Help" tag.
        """
        self.menubar = QMenuBar()
        self.setMenuBar(self.menubar)

        self.file_tab = QMenu("&File")
        self.file_tab.addAction(self.save_act)
        self.file_tab.addAction(self.stop_act)
        self.file_tab.addAction(self.rec_act)
        self.file_tab.addSeparator()
        self.file_tab.addAction(self.quit_act)
        self.file_tab.setMinimumWidth(100)
        #self.file_tab.setSizePolicy(policy)

        self.view_tab = QMenu("&View")
        self.view_tab.addAction(self.theme_act)
        self.view_tab.addAction(self.font_act)
        self.view_tab.addAction(self.show_shortcut_act)
        #self.view_tab.addAction(self.show_paramlist_act)

        self.help_tab = QMenu("&Help")
        self.help_tab.addAction(self.usage_act)
        self.help_tab.addAction(self.about_act)

        self.menubar.addMenu(self.file_tab)
        self.menubar.addMenu(self.view_tab)
        self.menubar.addMenu(self.help_tab)

        #self.menubar.setFont(QFont("Helvetica [Cronyx]", 18))
        #self.menubar.adjustSize()


    def add_statusbar(self):
        """Create status bar, then add to the main window.

        The status bar shows the coordinates on the frame where the cursor is located and
        its pixel value. The pixel value has RGB if the format of is color (RGB), does grayscale
        value if grayscale.
        """
        self.statbar_list = []
        if self.colorspace == "rgb":
            self.stat_css = {
                "postion": "color: white",
                "R": "color: white;",
                "G": "color: white;",
                "B": "color: white;",
                "alpha": "color: white;",
            }
        else:
            self.stat_css = {
                "postion": "color: black;",
                "gray": "color: black"
            }

        for s in self.stat_css.values():
            stat = QStatusBar(self)
            stat.setStyleSheet(s)
            self.statbar_list.append(stat)

        first = True
        for stat in self.statbar_list:
            if first:
                self.setStatusBar(stat)
                self.statbar_list[0].reformat()
                first = False
            else:
                self.statbar_list[0].addPermanentWidget(stat)


    def update_statusbar(self):
        """Update statubar's style

        This method will be called when swtitching the color theme.

        """
        if self.style_theme == "light":
            if self.colorspace == "rgb":
                self.stat_css = {
                    "postion": "color: black;",
                    "R": "color: red;",
                    "G": "color: green;",
                    "B": "color: blue;",
                    "alpha": "color: black;",
                    }
            else:
                self.stat_css = {
                    "postion": "color: black;",
                    "gray": "color: black;"
                }
        elif self.style_theme == "dark":
            if self.colorspace == "rgb":
                self.stat_css = {
                    "postion": "color: white;",
                    "R": "color: white;",
                    "G": "color: white;",
                    "B": "color: white;",
                    "alpha": "color: white;",
                    }
            else:
                self.stat_css = {
                    "postion": "color: white;",
                    "gray": "color: white;"
                }
        for stat, st in zip(self.statbar_list, self.stat_css.values()):
            stat.setStyleSheet(st)


    def add_buttons(self):
        """Add push buttons on the window.

        Add quit, save stop and usage buttons on the windows. When press each button, the set
        method (called "slot" in Qt framework) are execeuted.
        """
        self.save_button = self.create_button("&Save", self.save_frame, None, None, "Save the frame")
        self.stop_button = self.create_button("&Pause", self.stop_frame, None, None, "Stop reading frame", True)
        self.rec_button = self.create_button("&Rec", self.record, None, None, "Start recording", True)
        self.close_button = self.create_button("&Quit", self.quit, None, None, "Quit the program")
        self.theme_button = self.create_button("Light", self.switch_theme, None, None, "Switche color theme")
        self.help_button = self.create_button("&Usage", self.usage, None, None, "Show usage")

        self.frame_button = self.create_button("Properties", self.change_frame_prop, None, tip="Change properties")
        self.default_button = self.create_button("&Default params", self.set_param_default, "Ctrl+d", tip="Set default parameters")
        self.filerule_button = self.create_button("File &naming convention", self.set_file_rule, "Ctrl+n", tip="Change naming convention")

        #self.theme_button = QPushButton("&Light")
        #self.theme_button.clicked.connect(self.switch_theme)
        #self.theme_button.setIcon(QIcon(Icon.Dark.toggle_off))

        # Add buttons to the first row on the window .
        hbox = QHBoxLayout()
        hbox.addWidget(self.save_button)
        hbox.addWidget(self.stop_button)
        hbox.addWidget(self.rec_button)
        hbox.addWidget(self.close_button)
        hbox.addWidget(self.theme_button)
        hbox.addWidget(self.help_button)
        return hbox


    def create_button(self, text: str, slot: Callable, key: str = None, icon: Icon = None,
        tip: str = None, checkable: bool = False) -> QPushButton:
        """Create a QPushButton object.

        Args:
            text (str): Text shown on the button.
            slot (Callable): A method called when click the button.
            key (str, optional): Shortcut key. Defaults to None.
            icon (Icon, optional): An icon shown on the button. Defaults to None.
            tip (str, optional): A tips shown when position the pointer on the button. Defaults to None.
            checkable (bool, optional): . Defaults to False.

        Returns:
            [type]: [description]
        """
        button = QPushButton(text)
        if checkable:
            button.setCheckable(True)
            button.toggled.connect(slot)
        else:
            button.clicked.connect(slot)

        if key:
            button.setShortcut(key)
        if icon:
            button.setIcon(QIcon(icon))
        if tip:
            button.setToolTip(tip)
        return button


    def switch_theme(self):
        '''
        Toggle the stylesheet to use the desired path in the Qt resource
        system (prefixed by `:/`) or generically (a path to a file on
        system).

        quated : https://stackoverflow.com/questions/48256772/dark-theme-for-qt-widgets

        :path:      A full path to a resource or file on system
        '''

        # get the QApplication instance,  or crash if not set
        app = QApplication.instance()
        if app is None:
            raise RuntimeError("No Qt Application found.")

        text = ""
        if self.style_theme == "light":
            self.style_theme = "dark"
            self.style_theme_sheet = ":/dark.qss"
            self.update_statusbar()
            #self.theme_button.setIcon(QIcon(Icon.Dark.toggle_on))
            #self.close_button.setIcon(QIcon(Icon.Dark.close))
            text = "Light"
        elif self.style_theme == "dark":
            self.style_theme = "light"
            self.style_theme_sheet = ":/light.qss"
            self.update_statusbar()
            #self.theme_button.setIcon(QIcon(Icon.Light.toggle_off))
            text = "Dark"

        file = QFile(self.style_theme_sheet)
        self.theme_button.setText(text)
        file.open(QFile.ReadOnly | QFile.Text)
        stream = QTextStream(file)
        app.setStyleSheet(stream.readAll())



    def add_params(self) -> QGridLayout:
        """Set the properties of camera parameter.

        Set the properties of camera parameter, then add sliders to change each parameter.
        When change value on the slider, the value of paramter also changes by the caller
        function. The list of the added paramaters is below when set usb-cam as camtype.

            - brightness
            - contrast
            - gain
            - saturation
        """
        self.param_list = self.frame.get_params()

        for key, value in self.param_list.items():
            self.add_slider(key)

        # add sliders
        grid = QGridLayout()
        grid.setSpacing(15)
        grid.setContentsMargins(20, 20, 20, 20)
        for row, param in enumerate(self.param_list):
            grid.addWidget(self.frame.params[param]["slider_label"], row, 0)
            grid.addWidget(self.frame.params[param]["slider"], row, 1)
            grid.addWidget(self.frame.params[param]["slider_val"], row, 2)
        if len(self.param_list) > 15:
            self.param_separate = True
        return grid


    def add_slider(self, param: str):
        min_ = self.frame.params[param]["min"]
        max_ = self.frame.params[param]["max"]
        step = self.frame.params[param]["step"]
        value = self.frame.params[param]["value"]

        slider = QSlider(Qt.Horizontal)
        if max_:
            slider.setRange(min_, max_)
        else:
            slider.setRange(0, 1)
        slider.setValue(value)
        slider.setTickPosition(QSlider.TicksBelow)
        slider.valueChanged.connect(lambda val, p=param: self.frame.change_param(p, val))

        if step:
            if max_ < 5:
                slider.setTickInterval(step)
            else:
                slider.setTickInterval(10)

        slider_label = QLabel(param)
        slider_value = QLabel(str(value))

        slider_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        slider_value.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.frame.params[param]["slider"] = slider
        self.frame.params[param]["slider_label"] = slider_label
        self.frame.params[param]["slider_val"] = slider_value


    def add_prop_window(self) -> QGridLayout:
        """
        for val in self.prop_list.values():
            val.setFrameStyle(QFrame.Box)
            val.setFrameStyle(QFrame.StyledPanel)
            val.setMinimumSize(40, 30)
            val.setMaximumSize(360, 150)
        """
        header = ["property", "value"]

        self.prop_table = QTableWidget(self)
        self.prop_table.setColumnCount(len(header))
        self.prop_table.setRowCount(len(self.frame.prop_table))

        self.prop_table.setHorizontalHeaderLabels(header)
        self.prop_table.verticalHeader().setVisible(False)
        self.prop_table.setAlternatingRowColors(True)
        self.prop_table.horizontalHeader().setStretchLastSection(True)
        self.prop_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.prop_table.setFocusPolicy(Qt.NoFocus)

        for row, content in enumerate(self.frame.prop_table):
            for col, elem in enumerate(content):
                self.item = QTableWidgetItem(elem)

                self.prop_table.setItem(row, col, self.item)
        self.prop_table.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        #self.prop_table.resizeColumnsToContents()
        #self.prop_table.resizeRowsToContents()
        self.prop_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.prop_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.prop_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContentsOnFirstShow)

        vbox = QVBoxLayout()
        vbox.addWidget(self.prop_table)
        vbox.setContentsMargins(20, 20, 20, 20)
        self.prop_group = QGroupBox("Frame Properties")
        self.prop_group.setLayout(vbox)

        return self.prop_group



    def construct_layout(self):
        self.main_layout.addLayout(self.view_region_layout())
        self.main_layout.addLayout(self.make_information_layout())


    def view_region_layout(self):
        vbox = QVBoxLayout()
        vbox.addLayout(self.button_block)
        vbox.addWidget(self.view)
        return vbox


    def make_information_layout(self):
        if self.param_separate:
            vbox = QVBoxLayout()
            vbox.addWidget(self.frame_button)
            vbox.addWidget(self.filerule_button)
            vbox.addWidget(self.default_button)
            vbox.addStretch(1)
            vbox.setSpacing(20)
            vbox.setContentsMargins(20, 20, 20, 20)

            button_group = QGroupBox("Buttons", self)
            button_group.setLayout(vbox)
            button_group.setAlignment(Qt.AlignLeft)

            vbox2 = QVBoxLayout()
            vbox2.addWidget(self.prop_group, 1)
            vbox2.addWidget(button_group, 1)

            group = QGroupBox("Parameters")
            group.setLayout(self.slider_block)
            group.setContentsMargins(20, 20, 20, 20)

            hbox = QHBoxLayout()
            hbox.addLayout(vbox2, 1)
            hbox.addWidget(group, 2)
            hbox.addStretch(1)
            return hbox
        else:
            vbox = QVBoxLayout()
            vbox.addWidget(self.frame_button)
            vbox.addWidget(self.filerule_button)
            vbox.addWidget(self.default_button)
            vbox.addStretch(1)
            vbox.setSpacing(20)
            vbox.setContentsMargins(20, 20, 20, 20)

            button_group = QGroupBox("Buttons", self)
            button_group.setLayout(vbox)
            button_group.setAlignment(Qt.AlignLeft)

            hbox = QHBoxLayout()
            hbox.addWidget(self.prop_group, 1)
            hbox.addWidget(button_group, 1)

            param_group = QGroupBox("Parameters")
            param_group.setLayout(self.slider_block)
            param_group.setContentsMargins(20, 20, 20, 20)

            vbox = QVBoxLayout()
            vbox.addLayout(hbox, 1)
            vbox.addWidget(param_group, 1)
            vbox.setSpacing(30)
            return vbox


    # decorator
    def display(func):
        def wrapper(self, *args, **kwargs):
            try:
                self.is_display = False
                self.read_flg = False
                self.stop_timer()
                func(self, *args, **kwargs)
            finally:
                self.is_display = True
                self.read_flg = True
                self.start_timer()
        return wrapper



    def stop_frame(self, checked: bool):
        """Stop reading next frame.

        Args:
            checked (bool): True when presse the Stop button (toggle on). False when press
                again (toggel off).
        """
        if checked:
            print("Stop !!")
            self.frame.read_flg = False
            self.stop_button.setText('Start')
            self.stop_button.setChecked(True)
            self.stop_act.setText('Start')
            self.stop_act.setChecked(True)
            #self.stop_button.setIcon(QIcon("icon/start.png"))
        else:
            print("Start !!")
            self.frame.read_flg = True
            self.stop_button.setText('&Pause')
            self.stop_button.setChecked(False)
            self.stop_act.setText('&Pause')
            self.stop_act.setChecked(False)
            #self.stop_button.setIcon(QIcon("icon/stop.png"))


    def keyPressEvent(self, event):
        """Exit the program

        This method will be called when press the Escape key on the window.
        """
        if event.key() == Qt.Key_Escape:
            self.close()


    def get_coordinates(self, event):
        """Show the current coordinates and value in the pixel where the cursor is located.

        The status bar is updates by the obtained values.
        """
        if self.item is self.view.itemAt(event.pos()):
            sp = self.view.mapToScene(event.pos())
            lp = self.item.mapFromScene(sp).toPoint()
            (x, y) = lp.x(), lp.y()
            #color = self.frame.image.pixel(x, y)
            color = self.qimage.pixelColor(x, y)
            if self.colorspace == "rgb":
                value = color.getRgb()
            elif self.colorspace == "gray":
                value = color.value()

            # print("color", value)

            # Return none if the coordinates are out of range
            if x < 0 and self.frame.width < x:
                return
            elif y < 0 and self.frame.height < y:
                return

            if self.frame.img_is_rgb:
                status_list = [
                    "( x : {}, y :{} )".format(x, y),
                    "R : {}".format(value[0]),
                    "G : {}".format(value[1]),
                    "B : {}".format(value[2]),
                    "alpha : {}".format(value[3])
                ]
            else:
                status_list = [
                    "( x : {}, y :{} )".format(x, y),
                    "gray value : {}".format(value),
                ]

            for statbar, stat in zip(self.statbar_list, status_list):
                statbar.showMessage(stat)


    def next_frame(self):
        """Get next frame from the connected camera.
        """
        if self.frame.read_flg and self.is_display:
            #self.scene.removeItem(self.item)
            self.frame.read_frame()
            self.convert_frame()
            #print(self.frame.item.shape())
            self.scene.clear()
            #self.scene.addItem(self.pixmap)
            self.scene.addPixmap(self.pixmap)
            self.update()
            if self.is_recording:
                self.video_writer.write(self.frame.cv_image)


    def convert_frame(self):
        if self.camtype == "usb_cam":
            if self.colorspace == "rgb":
                self.qimage = QImage(
                    self.frame.cv_image.data,
                    self.frame.width,
                    self.frame.height,
                    self.frame.width * 3,
                    QImage.Format_RGB888)
            elif self.colorspace == "gray":
                self.qimage = QImage(
                    self.frame.cv_image.data,
                    self.frame.width,
                    self.frame.height,
                    self.frame.width * 1,
                    QImage.Format_Grayscale8)
        elif self.camtype == "raspi":
            self.qimage = QImage(
                self.frame.cv_image.data,
                self.frame.width,
                self.frame.height,
                self.frame.width * 3,
                QImage.Format_RGB888)
        elif self.camtype == "uvcam":
            image_8 = self.cv_image / 8
            self.qimage = QImage(
                image_8,
                self.frame.width,
                self.frame.height,
                self.frame.width * 1,
                QImage.Format_Grayscale8)

        self.pixmap.convertFromImage(self.qimage)
        #self.item.setPixmap(self.pixmap)


    @display
    def about(self):
        """Show the about message on message box.
        """
        msg = QMessageBox()
        msg.setTextFormat(Qt.MarkdownText)
        msg.setIcon(msg.Information)
        msg.setWindowTitle("About this tool")
        msg.setText(MessageText.about_text)
        ret = msg.exec_()


    @display
    def show_shortcut(self):
        """Show the list of valid keyboard shortcut.
        """
        self.is_display = False
        self.read_flg = False
        self.dialog = QDialog()
        table = QTableWidget()
        vbox = QVBoxLayout()
        self.dialog.setLayout(vbox)
        self.dialog.setWindowTitle("Keyboard shortcut")

        header = ["key", "description"]
        keys = MessageText.keylist
        table.setColumnCount(len(header))
        table.setRowCount(len(keys))
        table.setHorizontalHeaderLabels(header)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        table.horizontalHeader().setStretchLastSection(True)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setFocusPolicy(Qt.NoFocus)
        #table.setTextFormat(Qt.RichText)
        #table.setSelectionMode(QAbstractItemView.NoSelection)

        for row, content in enumerate(keys):
            for col, elem in enumerate(content):
                item = QTableWidgetItem(elem)
                item.setFlags(Qt.ItemIsDragEnabled | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                item.font
                table.setItem(row, col, item)

        button = QPushButton("&Ok")
        button.clicked.connect(self.close)
        button.setAutoDefault(True)

        vbox.addWidget(table)
        vbox.addWidget(button)

        self.dialog.resize(640, 480)
        ret = self.dialog.exec_()


    @display
    def usage(self):
        """Show usage of the program.
        """

        msg = QMessageBox()
        msg.setWindowTitle("Usage")
        #msg.setTitle("Usage of this GUI")
        text = QLabel(MessageText.usage_text)
        msg.setIcon(QMessageBox.Information)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        grid = msg.findChild(QGridLayout)
        text.setWordWrap(True)
        scroll.setWidget(text)
        scroll.setMinimumSize(800, 400)
        scroll.setStyleSheet(
            """
            border: 1.5px solid black;
            """
        )
        grid.addWidget(scroll, 0, 1)
        ret = msg.exec_()


    def quit(self):
        """Quit the program.
        """
        QApplication.quit()


    def save_frame(self):
        """Save the frame on the window as png.

        The file is saved as <directory>/<filename>.png. Each fromat is as follows.

            - file name
                - Timestamp (%y%m%d-%H%M%S)
            - directory
                - By defaults, make a directory with today's date under the execute path.

        """
        if self.filename_rule == "Manual":
            self.save_frame_manual()
            if not self.filename:
                return None
            prm = re.sub(r"\.(.*)", ".csv", str(self.filename))
        else:
            self.filename = self.frame.get_filename(self.filename_rule, self.file_format, self.dst)
            prm = str(self.filename).replace(self.file_format, "csv")

        im = Image.fromarray(self.frame.cv_image)
        im.save(self.filename)

        #pprint(self.frame.params)
        with open(prm, "w") as f:
            for name, key in self.frame.params.items():
                f.write("{},{}\n".format(name, self.frame.params[name]["value"]))

        print("{:<20} :".format("save image"), self.filename)
        print("{:<20} :".format("save parameter file"), prm)



    @display
    def change_frame_prop(self):
        self.dialog = QDialog(self)
        self.dialog.setWindowTitle("Change frame properties")

        text = QLabel()
        text.setText("Select fourcc, size and FPS.")

        self.fourcc_label = QLabel("Fourcc")
        self.size_label = QLabel("Size")
        self.fps_label = QLabel("FPS")
        self.fourcc_result = QLabel(str(self.frame.fourcc))
        self.fourcc_result.setFrameShape(QFrame.StyledPanel)
        self.size_result = QLabel(str(self.frame.size))
        self.size_result.setFrameShape(QFrame.Box)
        self.size_result.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.fps_result = QLabel(str(self.frame.fps))
        self.fps_result.setFrameStyle(QFrame.Panel | QFrame.Sunken)

        fourcc_button = QPushButton("...")
        fourcc_button.clicked.connect(self.select_fourcc)
        size_button = QPushButton("...")
        size_button.clicked.connect(self.select_size)
        fps_button = QPushButton("...")
        fps_button.clicked.connect(self.select_fps)

        grid = QGridLayout()
        grid.addWidget(self.fourcc_label, 0, 0)
        grid.addWidget(self.fourcc_result, 0, 1)
        grid.addWidget(fourcc_button, 0, 2)
        grid.addWidget(self.size_label, 1, 0)
        grid.addWidget(self.size_result, 1, 1)
        grid.addWidget(size_button, 1, 2)
        grid.addWidget(self.fps_label, 2, 0)
        grid.addWidget(self.fps_result, 2, 1)
        grid.addWidget(fps_button, 2, 2)
        grid.setSpacing(5)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.dialog.accept)
        self.button_box.rejected.connect(self.dialog.reject)
        # button_ok = QPushButton("ok")
        # button_ok.clicked.connect(self.set_param)
        # button_cancel = QPushButton("cancel")
        # button_cancel.clicked.connect(self.close)

        hbox = QHBoxLayout()
        hbox.addWidget(button_ok)
        hbox.addWidget(button_cancel)

        vbox = QVBoxLayout()
        #vbox.addWidget(text, 1)
        vbox.addLayout(grid, 3)
        vbox.addWidget(self.button_box, 1)

        #vbox.addLayout(hbox, 1)
        #vbox.setStretchFactor(text, 10)
        #vbox.setStretchFactor(grid, 300)
        #vbox.setStretch(0, 1)

        self.dialog.setLayout(vbox)
        #self.dialog.resize(400, 300)
        self.dialog.resize(480, 270)
        if self.dialog.exec_():
            self.set_param()
            self.close()
        else:
            self.close()


    def select_fourcc(self):
        items = ["YUYV", "MJPG"]
        item, ok = QInputDialog.getItem(
            self,
            "Select",
            "Select Fourcc",
            items, 0, False
        )
        if ok:
            self.fourcc_result.setText(item)
        else:
            return None

    def select_size(self):
        items = self.frame.raspicam_img_format()
        item, ok = QInputDialog.getItem(
            self,
            "Select",
            "Select Fourcc",
            items, 0, False
        )
        if ok:
            self.size_result.setText(item)
        else:
            return None


    def select_fps(self):
        items = ["{}.0".format(i) for i in range(5, 31, 5)]
        item, ok = QInputDialog.getItem(
            self,
            "Select",
            "Select Fourcc",
            items, 0, False
        )
        if ok:
            self.fps_result.setText(item)
        else:
            return None


    def close(self):
        try:
            self.dialog.close()
            return True
        except:
            return False


    def set_param(self):
        fourcc = self.fourcc_result.text()
        size = self.size_result.text()
        width, height = map(int, size.split("x"))
        fps = self.fps_result.text()
        self.frame.set_format(fourcc, width, height, float(fps))
        self.scene.setSceneRect(0, 0, width, height)
        self.msec = 1 / float(fps) * 1000

        self.update_prop_table()


    def set_param_default(self):
        self.frame.set_param_default()


    def update_prop_table(self):
        col = 1
        for row in range(len(self.frame.prop_table)):
            text = str(self.frame.prop_table[row][col])
            self.prop_table.item(row, col).setText(text)


    def set_file_rule(self):
        self.filename_rule = next(self.filename_rule_lst)
        self.prop_table.item(5, 1).setText(self.filename_rule)


    def record(self):
        if self.is_recording:
            self.is_recording = False
            self.rec_button.setText('&Rec')
            self.rec_act.setText('&Record')
            print("save : ", self.frame.video_name)
            del self.video_writer
        else:
            self.is_recording = True
            self.rec_button.setText('Stop rec')
            self.rec_act.setText('Stop record')
            self.video_writer = self.frame.video_write()


    @display
    def save_frame_manual(self) -> str:
        self.dialog = QFileDialog()
        self.dialog.setWindowTitle("Save File")
        self.dialog.setNameFilters([
            "image (*.jpg *.png *.tiff *.pgm)",
            "All Files (*)"
            ])
        self.dialog.setAcceptMode(QFileDialog.AcceptSave)
        #self.dialog.setOption(QFileDialog.DontUseNativeDialog)

        if self.dialog.exec_():
            r = self.dialog.selectedFiles()
            if re.search(".pgm$|.png$|.jpg$|.tiff$", r[0]):
                self.filename = r[0]
            else:
                self.filename = "{}.{}".format(r[0], self.file_format)
            return True
        else:
            return None


    def get_screensize(self):
        cmd = ["xrandr"]
        ret = subprocess.check_output(cmd)
        output = ret.decode()
        pattern = r"current(\s+\d+\s+x\s+\d+)"

        m = re.search(pattern, output)
        if m:
            size = re.sub(" ", "", m.group(1))
            w, h = map(int, size.split("x"))
            return w, h, size
        else:
            return None


    @display
    def set_font(self):
        self.dialog = QFontDialog()
        self.dialog.setOption(QFontDialog.DontUseNativeDialog)
        self.dialog.resize(800, 600)
        ret = self.dialog.exec_()
        if ret:
            font = self.dialog.selectedFont()
            family = str(font.family())
            size = str(font.pointSize())
            font_css = str(self.parent / "font.css")
            with open(font_css, "w") as f:
                f.write("* {\n")
                f.write('    font-family: "{}";\n'.format(family))
                f.write('    font-size: {}px;\n'.format(size))
                f.write("}")
            with open(font_css, "r") as f:
                self.setStyleSheet(f.read())



