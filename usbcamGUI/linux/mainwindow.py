#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create a window for displaying frame and its properties
"""
import re
import subprocess
import numpy as np
from pathlib import Path
from typing import Callable
from itertools import cycle
from PIL import Image

from PySide2.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QWidget, QAction,
    QPushButton, QMenu, QMenuBar, QVBoxLayout, QHBoxLayout, QStatusBar, QGridLayout,
    QMessageBox, QScrollArea, QLabel, QFrame, QTableWidget, QTableWidgetItem, QInputDialog, QDialog,
    QAbstractItemView, QSizePolicy, QFileDialog, QAbstractScrollArea, QGroupBox,
    QGraphicsPixmapItem, QSlider, QFontDialog, QDialogButtonBox, QToolBar, QSpinBox, QComboBox,
    QFontComboBox, QRadioButton, QButtonGroup, QCheckBox
    )
from PySide2.QtGui import QIcon, QFont, QPixmap, QImage, QBitmap
from PySide2.QtCore import Qt, QTimer, QTextStream, QFile, QByteArray, QSize

from camera import USBcam
from text import MessageText
from v4l import V4L2
from icon import Icon
from slot import Slot
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
    def __init__(self, device: int = 0, suffix: str = "png", camtype: str = "usb_cam", color: str = "RGB",
        dst: str = ".", param: str = "full", rule: str = "Sequential", parent=None):
        super(Window, self).__init__(parent)
        self.frame = USBcam(device, camtype, color, param, rule, dst)
        self.camtype = camtype
        self.colorspace = color
        self.image_suffix = suffix
        self.dst = Path(dst)
        self.parent = Path(__file__).parent.resolve()

        self.filename_rule_lst = FileIO.file_save
        self.filename_rule = FileIO.file_save_lst[-1]

        self.is_display = True
        self.param_separate = False

        self.slot = Slot(self)
        self.v4l2 = V4L2(device)
        self.setup()


    def setup(self):
        """Setup the main window for displaying frame and widget.

        Create a QMainWindow object, then set menubar, toolbar, statusbar, widgets and layout.
        """
        self.setFocusPolicy(Qt.ClickFocus)
        self.setContentsMargins(20, 0, 20, 0)
        self.view_setup()
        self.layout_setup()
        self.image_setup()
        self.toolbar_setup()
        self.setWindowTitle("usbcamGUI")
        wscale = 0.5
        hscale = 0.9
        w, h, _ = self.get_screensize()
        #self.resize(800, 600)
        #self.resize(1024, 768)
        self.resize(wscale * w, hscale * h)
        self.set_theme()
        self.set_timer()


    def set_theme(self):
        """Set color theme of the main window.
        """
        self.style_theme = "light"
        self.style_theme_sheet = ":/{}.qss".format(self.style_theme)
        self.slot.switch_theme()

        """
        self.css_sheet = self.parent / "app.qss"
        with open(str(self.css_sheet), "r") as f:
            self.setStyleSheet(f.read())
        """


    def set_timer(self):
        """Set QTimer

        Create a QTimer object to switch frame on view area. The interval is set to the inverse
        of camera FPS.
        """
        if self.frame.fps:
            self.msec = 1 / self.frame.fps * 1000
        else:
            self.msec = 1 / 30.0 * 1000
        self.timer = QTimer()
        self.timer.setInterval(self.msec)
        self.timer.timeout.connect(self.next_frame)
        self.timer.start()


    def stop_timer(self):
        """Deactivate the Qtimer object.
        """
        self.timer.stop()


    def start_timer(self):
        """Activate the Qtimer object.
        """
        self.timer.setInterval(self.msec)
        self.timer.start()


    def toolbar_setup(self):
        """Create toolbar
        """
        self.toolbar = QToolBar("test", self)
        self.addToolBar(self.toolbar)

        current_size = str(self.font().pointSize())
        lst = [str(i) for i in range(6, 14)]
        lst.extend([str(i) for i in range(14, 40, 2)])
        index = lst.index(current_size)

        self.fontsize_combo = QComboBox()
        self.fontsize_combo.addItems(lst)
        self.fontsize_combo.setCurrentIndex(index)
        self.fontsize_combo.currentTextChanged.connect(self.slot.set_fontsize)
        self.fontsize_label = QLabel("Font size")
        self.fontsize_label.setFrameShape(QFrame.Box)

        self.comb = QFontComboBox()

        self.toolbar.addWidget(self.save_button)
        self.toolbar.addWidget(self.stop_button)
        self.toolbar.addWidget(self.rec_button)
        self.toolbar.addWidget(self.close_button)
        self.toolbar.addWidget(self.theme_button)
        self.toolbar.addWidget(self.help_button)
        self.toolbar.addWidget(self.fontsize_label)
        self.toolbar.addWidget(self.fontsize_combo)
        self.toolbar.setStyleSheet(
            """
            QToolBar {spacing:5px;}
            """
            )


    def view_setup(self):
        """Set view area to diplay read frame in part of the main window
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

        self.main_layout = QHBoxLayout()
        self.window.setLayout(self.main_layout)

        self.add_actions()
        self.add_menubar()
        self.add_statusbar()
        self.button_block = self.add_buttons()
        self.slider_group = self.add_params()
        self.prop_block = self.add_prop_window()
        self.create_mainlayout()


    def image_setup(self):
        """Create a Qimage to assign frame, then initialize with an image which has zero in all pixels.
        """
        self.init_array = np.zeros((self.frame.width, self.frame.height, self.frame.ch))
        self.qimage = QImage(
            self.init_array,
            self.frame.width,
            self.frame.height,
            self.frame.width * self.frame.ch,
            QImage.Format_RGB888
            )
        self.pixmap = QPixmap.fromImage(self.qimage)


    def add_actions(self):
        """Add actions executed when press each item in the memu window.
        """
        self.save_act = self.create_action("&Save", self.save_frame, "Ctrl+s")
        self.stop_act = self.create_action("&Pause", self.stop_frame, "Ctrl+p", True)
        self.rec_act = self.create_action("&Record", self.record, "Ctrl+r", True)
        self.quit_act = self.create_action("&Quit", self.slot.quit, "Ctrl+q")

        self.theme_act = self.create_action("Switch &Theme", self.slot.switch_theme, "Ctrl+t")
        self.param_act = self.create_action("Choose parameter slider", self.slot.switch_paramlist, "Ctrl+g")
        self.show_paramlist_act = self.create_action("Parameters &List", self.slot.show_paramlist, "Ctrl+l")
        self.show_shortcut_act = self.create_action("&Keybord shortcut", self.slot.show_shortcut, "Ctrl+k")
        self.font_act = self.create_action("&Font", self.slot.set_font, "Ctrl+f")

        self.usage_act = self.create_action("&Usage", self.slot.usage, "Ctrl+h")
        self.about_act = self.create_action("&About", self.slot.about, "Ctrl+a")


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
        """
        self.menubar = QMenuBar()
        self.setMenuBar(self.menubar)

        self.file_tab = QMenu("&File")
        self.file_tab.addAction(self.save_act)
        self.file_tab.addAction(self.stop_act)
        self.file_tab.addAction(self.rec_act)
        self.file_tab.addSeparator()
        self.file_tab.addAction(self.quit_act)
        #self.file_tab.setSizePolicy(policy)

        self.view_tab = QMenu("&View")
        self.view_tab.addAction(self.theme_act)
        self.view_tab.addAction(self.font_act)
        self.view_tab.addAction(self.param_act)
        self.view_tab.addAction(self.show_shortcut_act)
        self.view_tab.addAction(self.show_paramlist_act)

        self.help_tab = QMenu("&Help")
        self.help_tab.addAction(self.usage_act)
        self.help_tab.addAction(self.about_act)


        self.menubar.addMenu(self.file_tab)
        self.menubar.addMenu(self.view_tab)
        self.menubar.addMenu(self.help_tab)
        self.menubar.setStyleSheet(
            """
            QMenuBar {
                    font-size: 16px;
                    spacing:10px;
                    padding-top: 5px;
                    padding-bottom: 10px;
                }
            """
            )

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


    def add_buttons(self):
        """Add push buttons on the window.

        Add quit, save stop and usage buttons on the windows. When press each button, the set
        method (called "slot" in Qt framework) are execeuted.
        """
        self.save_button = self.create_button("&Save", self.save_frame, None, None, "Save the frame")
        self.stop_button = self.create_button("&Pause", self.stop_frame, None, None, "Stop reading frame", True)
        self.rec_button = self.create_button("&Rec", self.record, None, None, "Start recording", True)
        self.close_button = self.create_button("&Quit", self.slot.quit, None, None, "Quit the program")
        self.theme_button = self.create_button("Light", self.slot.switch_theme, None, None, "Switche color theme")
        self.help_button = self.create_button("&Usage", self.slot.usage, None, None, "Show usage")

        self.frame_button = self.create_button(
            "Properties",
            self.slot.change_frame_prop,
            None,
            tip="Change properties",
            minsize=(150, 30)
            )
        self.default_button = self.create_button(
            "&Default params",
            self.slot.set_default,
            "Ctrl+d",
            tip="Set default parameters",
            minsize=(150, 30)
            )
        self.filerule_button = self.create_button(
            "File &naming convention",
            self.slot.set_file_rule,
            "Ctrl+n",
            tip="Change naming convention",
            minsize=(150, 30)
            )

        hbox = QHBoxLayout()
        hbox.addWidget(self.save_button)
        hbox.addWidget(self.stop_button)
        hbox.addWidget(self.rec_button)
        hbox.addWidget(self.close_button)
        hbox.addWidget(self.theme_button)
        hbox.addWidget(self.help_button)
        return hbox


    def create_button(self, text: str, slot: Callable, key: str = None, icon: Icon = None,
        tip: str = None, checkable: bool = False, minsize: tuple = None) -> QPushButton:
        """Create a QPushButton object.

        Args:
            text (str): Text shown on the button.
            slot (Callable): A method called when click the button.
            key (str, optional): Shortcut key. Defaults to None.
            icon (Icon, optional): An icon shown on the button. Defaults to None.
            tip (str, optional): A tips shown when position the pointer on the button. Defaults to None.
            checkable (bool, optional): Add button to checkbox. Defaults to False.
            msize (tuple, optional): Minimum size of the button box, (width, height).

        Returns:
            QPushButton: PySide2 QPushButton
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
        if minsize:
            button.setMinimumSize(minsize[0], minsize[1])
        else:
            button.setMinimumSize(80, 30)
        return button


    def add_params(self) -> QGridLayout:
        """Set the properties of camera parameter.

        Set the properties of camera parameter, then add sliders to change each parameter.
        When change value on the slider, the value of paramter also changes by the caller
        function.

        """

        for key, value in self.frame.current_params.items():
            self.add_slider(key)

        # add sliders
        self.slider_table = QGridLayout()
        self.slider_table.setSpacing(15)
        self.slider_table.setContentsMargins(20, 20, 20, 20)
        for row, param in enumerate(self.frame.current_params):
            self.slider_table.addWidget(self.frame.current_params[param]["slider_label"], row, 0)
            self.slider_table.addWidget(self.frame.current_params[param]["slider"], row, 1)
            self.slider_table.addWidget(self.frame.current_params[param]["slider_val"], row, 2)
        if len(self.frame.current_params) > 15:
            self.param_separate = True
        return self.slider_table



    def update_params(self, plist: list) -> QGridLayout:
        """Update properties of camera parameter.
        """
        self.frame.update_current_params(plist)
        for key, value in self.frame.current_params.items():
            self.add_slider(key)

        # add sliders
        grid = QGridLayout()
        grid.setSpacing(15)
        grid.setContentsMargins(20, 20, 20, 20)
        for row, param in enumerate(self.frame.current_params):
            grid.addWidget(self.frame.current_params[param]["slider_label"], row, 0)
            grid.addWidget(self.frame.current_params[param]["slider"], row, 1)
            grid.addWidget(self.frame.current_params[param]["slider_val"], row, 2)
        if len(self.frame.current_params) > 15:
            self.param_separate = True

        self.slider_group = grid
        self.update_mainlayout()
        print("update sliders")
        return grid


    def add_slider(self, param: str):
        """Create slider, labels to show pamarater's name and its value.

        Args:
            param (str): A parameter to crate slider.
        """
        min_ = self.frame.current_params[param]["min"]
        max_ = self.frame.current_params[param]["max"]
        step = self.frame.current_params[param]["step"]
        value = self.frame.current_params[param]["value"]

        slider = QSlider(Qt.Horizontal)
        if max_:
            slider.setRange(min_, max_)
        else:
            slider.setRange(0, 1)
        slider.setValue(value)
        slider.setTickPosition(QSlider.TicksBelow)
        slider.valueChanged.connect(lambda val, p=param: self.frame.set_param(p, val))

        if step:
            if max_ < 5:
                slider.setTickInterval(step)
            else:
                slider.setTickInterval(10)

        slider_label = QLabel(param)
        slider_value = QLabel(str(value))

        slider_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        slider_value.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.frame.current_params[param]["slider"] = slider
        self.frame.current_params[param]["slider_label"] = slider_label
        self.frame.current_params[param]["slider_val"] = slider_value


    def add_prop_window(self) -> QGridLayout:
        """Create a table to show the current properties of camera.

        Returns:
            QGridLayout: PySide2 QGridLayout
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


    def create_mainlayout(self):
        """Create the main layout which consists of view area and information window.
        """
        self.main_layout.addLayout(self.create_view_area_layout())
        self.main_layout.addLayout(self.create_information_layout())


    def update_mainlayout(self):
        """Recreate the main layout.
        """
        self.delete_layout(self.information_layout)
        self.delete_layout(self.upper_right)
        self.add_prop_window()
        self.main_layout.addLayout(self.create_information_layout())


    def delete_layout(self, layout):
        """Delete layout

        Args:
            layout (QBoxLayout): QBoxLayout class object to delete
        """
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            try:
                child.spacerIitem().deleteLater()
            except:
                pass


    def create_view_area_layout(self):
        """Create view-area layout
        """
        self.view_area_layout = QVBoxLayout()
        self.view_area_layout.addLayout(self.button_block)
        self.view_area_layout.addWidget(self.view)
        return self.view_area_layout


    def create_information_layout(self):
        """Create information-part layout

        upper-left: current properties
        upper-right: buttons
        lower: sliders

        """
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
            group.setLayout(self.slider_group)
            group.setContentsMargins(20, 20, 20, 20)

            hbox = QHBoxLayout()
            hbox.addLayout(vbox2, 1)
            hbox.addWidget(group, 2)
            hbox.addStretch(1)
            return hbox
        else:
            self.entity_box = QVBoxLayout()
            self.entity_box.addWidget(self.frame_button)
            self.entity_box.addWidget(self.filerule_button)
            self.entity_box.addWidget(self.default_button)
            self.entity_box.addStretch(1)
            self.entity_box.setSpacing(20)
            self.entity_box.setContentsMargins(20, 20, 20, 20)

            self.button_group_box = QGroupBox("Buttons", self)
            self.button_group_box.setLayout(self.entity_box)
            self.button_group_box.setAlignment(Qt.AlignLeft)

            self.upper_right = QHBoxLayout()
            self.upper_right.addWidget(self.prop_group)
            self.upper_right.addWidget(self.button_group_box)

            self.slider_group_box = QGroupBox("Parameters")
            self.slider_group_box.setLayout(self.slider_group)
            self.slider_group_box.setContentsMargins(20, 20, 20, 20)

            self.information_layout = QVBoxLayout()
            self.information_layout.addLayout(self.upper_right)
            self.information_layout.addWidget(self.slider_group_box)
            self.information_layout.setSpacing(30)
            return self.information_layout


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
        else:
            print("Start !!")
            self.frame.read_flg = True
            self.stop_button.setText('&Pause')
            self.stop_button.setChecked(False)
            self.stop_act.setText('&Pause')
            self.stop_act.setChecked(False)


    def keyPressEvent(self, event):
        """Exit the program

        This method will be called when press the Escape key on the window.
        """
        if event.key() == Qt.Key_Escape:
            QApplication.quit()



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

        Get next frame, set it to the view area and update.
        """
        if self.frame.read_flg and self.is_display:
            self.frame.read_frame()
            if self.frame.is_recording:
                return True
            self.convert_frame()
            self.scene.clear()
            self.scene.addPixmap(self.pixmap)
            self.update()


    def convert_frame(self):
        """Convert the class of frame

        Create qimage, qpixmap objects from ndarray frame for displaying on the window.

        """
        if self.camtype == "usb_cam":
            if self.colorspace == "rgb":
                self.qimage = QImage(
                    self.frame.cv_image.data,
                    self.frame.width,
                    self.frame.height,
                    self.frame.width * 3,
                    QImage.Format_RGB888)
                #self.qimage.loadFromData(self.frame.cv_image.flatten(), len(self.frame.cv_image.flatten()))
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

        self.pixmap.convertFromImage(self.qimage)


    def save_frame(self):
        """Save the frame on the window as an image.
        """
        if self.filename_rule == "Manual":
            self.save_frame_manual()
            if not self.filename:
                return None
            prm = re.sub(r"\.(.*)", ".csv", str(self.filename))
        else:
            self.filename = self.frame.get_filename(self.filename_rule, self.image_suffix, self.dst)
            prm = str(self.filename).replace(self.image_suffix, "csv")

        if not self.dst.exists():
            self.dst.mkdir(parents=True)
        im = Image.fromarray(self.frame.cv_image)
        im.save(self.filename)

        # make a parameter file
        with open(prm, "w") as f:
            for name, key in self.frame.current_params.items():
                f.write("{},{}\n".format(name, self.frame.current_params[name]["value"]))

        print("{:<20} :".format("save image"), self.filename)
        print("{:<20} :".format("save parameter file"), prm)


    def update_prop_table(self):
        col = 1
        for row in range(len(self.frame.prop_table)):
            text = str(self.frame.prop_table[row][col])
            self.prop_table.item(row, col).setText(text)


    def record(self):
        """Start or end recording
        """
        if self.frame.is_recording:
            self.frame.is_recording = False
            self.rec_button.setText('&Rec')
            self.rec_act.setText('&Record')
            print("save : ", self.frame.video_name)
            self.frame.video_writer.release()
        else:
            self.frame.is_recording = True
            self.rec_button.setText('Stop rec')
            self.rec_act.setText('Stop record')
            self.frame.video_write()


    @display
    def save_frame_manual(self) -> bool:
        """Determine file name of image to save with QFileDialog
        """
        self.dialog = QFileDialog()
        self.dialog.setWindowTitle("Save File")
        self.dialog.setNameFilters([
            "image (*.jpg *.png *.tiff *.pgm)",
            "All Files (*)"
            ])
        self.dialog.setAcceptMode(QFileDialog.AcceptSave)
        self.dialog.setOption(QFileDialog.DontUseNativeDialog)

        if self.dialog.exec_():
            r = self.dialog.selectedFiles()

            # If the file name doesn't include supproted suffixes, add to the end.
            if re.search(".pgm$|.png$|.jpg$|.tiff$", r[0]):
                self.filename = r[0]
            else:
                self.filename = "{}.{}".format(r[0], self.image_suffix)
            return True
        else:
            return False


    def get_screensize(self):
        """Get current screen size from the output of linux cmd xrandr.
        """
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
