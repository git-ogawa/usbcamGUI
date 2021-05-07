#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Slot class for handling signal of Qt objects
"""
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

from text import MessageText


class Slot():
    """Slot class for handling signal of Qt objects
    """
    def __init__(self, parent):
        self.parent = parent

    # decorator
    def display(func):
        def wrapper(self, *args, **kwargs):
            try:
                self.parent.is_display = False
                self.parent.read_flg = False
                self.parent.stop_timer()
                func(self, *args, **kwargs)
            finally:
                self.parent.is_display = True
                self.parent.read_flg = True
                self.parent.start_timer()
        return wrapper


    def set_default(self):
        """Set parameter to default value.
        """
        self.parent.frame.set_default()


    def switch_theme(self):
        """
        Toggle the stylesheet to use the desired path in the Qt resource
        system (prefixed by `:/`) or generically (a path to a file on
        system). This is quoted : https://stackoverflow.com/questions/48256772/dark-theme-for-qt-widgets
        """
        # get the QApplication instance,  or crash if not set
        app = QApplication.instance()
        if app is None:
            raise RuntimeError("No Qt Application found.")

        text = ""
        if self.parent.style_theme == "light":
            self.parent.style_theme = "dark"
            self.parent.style_theme_sheet = ":/dark.qss"
            self.update_statusbar()
            text = "Light"
        elif self.parent.style_theme == "dark":
            self.parent.style_theme = "light"
            self.parent.style_theme_sheet = ":/light.qss"
            self.update_statusbar()
            text = "Dark"

        file = QFile(self.parent.style_theme_sheet)
        self.parent.theme_button.setText(text)
        file.open(QFile.ReadOnly | QFile.Text)
        stream = QTextStream(file)
        app.setStyleSheet(stream.readAll())


    def set_fontsize(self, text: str):
        """Change the font-size of all widgets.

        Args:
            text (str): font-size
        """
        size = int(text)
        font = self.parent.font()
        family = str(font.family())
        font_css = str(self.parent.parent / "font.qss")
        with open(font_css, "w") as f:
            f.write("* {\n")
            f.write('    font-family: "{}";\n'.format(family))
            f.write('    font-size: {}px;\n'.format(size))
            f.write("}")
        self.parent.setStyleSheet("")
        with open(font_css, "r") as f:
            self.parent.setStyleSheet(f.read())


    def switch_paramlist(self) -> list:
        """Change the number of sliders shown on the window.

        User can select which parameter is shown on the window with Checkbox.

        Returns:
            list: List of selected paramters.
        """
        self.dialog = QDialog(self.parent)
        self.vbox2 = QVBoxLayout()

        self.check_boxes = []
        self.button_box = QGroupBox("params")
        self.button_box.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        for label in self.parent.frame.support_params:
            self.check_box = QCheckBox(label)
            if label in self.parent.frame.current_params.keys():
                self.check_box.setChecked(True)
            self.check_boxes.append(self.check_box)
            self.vbox2.addWidget(self.check_box)
        self.vbox2.addStretch(1)
        self.button_box.setLayout(self.vbox2)

        self.check_all = QCheckBox("Check all")
        self.check_all.setChecked(False)
        self.check_all.stateChanged.connect(self.ALLCheck)

        label = QLabel("Select parameters to create slider")

        self.qdbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.qdbox.accepted.connect(self.dialog.accept)
        self.qdbox.rejected.connect(self.dialog.reject)

        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.check_all)
        self.hbox.addWidget(self.qdbox)

        self.vbox = QVBoxLayout()
        self.vbox.addWidget(label)
        self.vbox.addWidget(self.button_box)
        self.vbox.addLayout(self.hbox)

        self.dialog.setLayout(self.vbox)

        self.dialog.resize(400, 300)
        if self.dialog.exec_():
            ret = []
            for button, key in zip(self.check_boxes, self.parent.frame.support_params):
                if button.isChecked():
                    ret.append(key)
            self.parent.update_params(ret)


    def ALLCheck(self):
        """Checkes all chekebox.
        """
        if self.check_all.isChecked():
            for cb in self.check_boxes:
                cb.setChecked(True)
        else:
            for cb in self.check_boxes:
                cb.setChecked(False)


    @display
    def about(self):
        """Show the about message on message box.
        """
        msg = QMessageBox(self.parent)
        msg.setTextFormat(Qt.MarkdownText)
        msg.setIcon(msg.Information)
        msg.setWindowTitle("About this tool")
        msg.setText(MessageText.about_text)
        ret = msg.exec_()


    @display
    def show_shortcut(self):
        """Show the list of valid keyboard shortcut.
        """
        self.parent.dialog = QDialog(self.parent)
        table = QTableWidget()
        vbox = QVBoxLayout()
        self.parent.dialog.setLayout(vbox)
        self.parent.dialog.setWindowTitle("Keyboard shortcut")

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

        for row, content in enumerate(keys):
            for col, elem in enumerate(content):
                item = QTableWidgetItem(elem)
                item.setFlags(Qt.ItemIsDragEnabled | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                table.setItem(row, col, item)

        button = QPushButton("&Ok")
        button.clicked.connect(self.close)
        button.setAutoDefault(True)

        vbox.addWidget(table)
        vbox.addWidget(button)

        self.parent.dialog.resize(640, 480)
        ret = self.parent.dialog.exec_()


    @display
    def usage(self):
        """Show usage of the program.
        """

        msg = QMessageBox(self.parent)
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


    @display
    def change_frame_prop(self):
        """Change the properties of camera.
        """
        self.dialog = QDialog(self.parent)
        self.dialog.setWindowTitle("Change frame properties")

        text = QLabel()
        text.setText("Select fourcc, size and FPS.")

        self.parent.fourcc_label = QLabel("Fourcc")
        self.parent.size_label = QLabel("Size")
        self.parent.fps_label = QLabel("FPS")
        self.parent.fourcc_result = QLabel(str(self.parent.frame.fourcc))
        self.parent.fourcc_result.setFrameShape(QFrame.StyledPanel)
        self.parent.size_result = QLabel(str(self.parent.frame.size))
        self.parent.size_result.setFrameShape(QFrame.Box)
        self.parent.size_result.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.parent.fps_result = QLabel(str(self.parent.frame.fps))
        self.parent.fps_result.setFrameStyle(QFrame.Panel | QFrame.Sunken)

        fourcc_button = QPushButton("...")
        fourcc_button.clicked.connect(self.select_fourcc)
        size_button = QPushButton("...")
        size_button.clicked.connect(self.select_size)
        fps_button = QPushButton("...")
        fps_button.clicked.connect(self.select_fps)

        grid = QGridLayout()
        grid.addWidget(self.parent.fourcc_label, 0, 0)
        grid.addWidget(self.parent.fourcc_result, 0, 1)
        grid.addWidget(fourcc_button, 0, 2)
        grid.addWidget(self.parent.size_label, 1, 0)
        grid.addWidget(self.parent.size_result, 1, 1)
        grid.addWidget(size_button, 1, 2)
        grid.addWidget(self.parent.fps_label, 2, 0)
        grid.addWidget(self.parent.fps_result, 2, 1)
        grid.addWidget(fps_button, 2, 2)
        grid.setSpacing(5)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.dialog.accept)
        self.button_box.rejected.connect(self.dialog.reject)

        vbox = QVBoxLayout()
        vbox.addLayout(grid, 3)
        vbox.addWidget(self.button_box, 1)

        self.dialog.setLayout(vbox)
        self.dialog.resize(480, 270)
        if self.dialog.exec_():
            self.set_param()
            self.close()
        else:
            self.close()


    def select_fourcc(self):
        items = self.parent.frame.fourcc_list
        item, ok = QInputDialog.getItem(
            self.dialog,
            "Select",
            "Select Fourcc",
            items, 0, False
        )
        if ok:
            self.parent.fourcc_result.setText(item)
        else:
            return None


    def select_size(self):
        if not self.parent.fourcc_result.text():
            msg = QMessageBox(self.parent)
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText("Select fourcc")
            msg.setWindowTitle("Error")
            msg.exec_()
            self.select_fourcc()
            return True

        items = self.parent.frame.raspicam_img_format()
        item, ok = QInputDialog.getItem(
            self.dialog,
            "Select",
            "Select Size",
            items, 0, False
        )
        if ok:
            self.parent.size_result.setText(item)
        else:
            return None


    def select_fps(self):
        if not self.parent.size_result.text():
            msg = QMessageBox(self.parent)
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText("Select size")
            msg.setWindowTitle("Error")
            msg.exec_()
            self.select_size()
            return True

        items = self.parent.frame.fps_list
        item, ok = QInputDialog.getItem(
            self.dialog,
            "Select",
            "Select FPS",
            items, 0, False
        )
        if ok:
            self.parent.fps_result.setText(item)
        else:
            return None


    def set_param(self):
        fourcc = self.parent.fourcc_result.text()
        size = self.parent.size_result.text()
        width, height = map(int, size.split("x"))
        fps = self.parent.fps_result.text()
        self.parent.frame.set_format(fourcc, width, height, float(fps))
        self.parent.scene.setSceneRect(0, 0, width, height)
        self.parent.msec = 1 / float(fps) * 1000

        self.parent.update_prop_table()


    def close(self):
        """Close the dialog.
        """
        try:
            self.parent.dialog.close()
            return True
        except:
            return False


    @display
    def show_paramlist(self):
        """Show the list of currently set parameters.
        """
        self.parent.dialog = QDialog(self.parent)
        table = QTableWidget()
        vbox = QVBoxLayout()
        self.parent.dialog.setLayout(vbox)
        self.parent.dialog.setWindowTitle("Parameters list")

        header = ["param", "min", "max", "step", "default"]
        lst = []
        for key, val in self.parent.frame.current_params.items():
            sub = []
            sub.append(key)
            for head in header:
                if head in val:
                    sub.append(val[head])
            lst.append(sub)

        table.setColumnCount(len(header))
        table.setRowCount(len(self.parent.frame.current_params))
        table.setHorizontalHeaderLabels(header)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        table.horizontalHeader().setStretchLastSection(True)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setFocusPolicy(Qt.NoFocus)

        for row, content in enumerate(lst):
            for col, elem in enumerate(content):
                item = QTableWidgetItem(str(elem))
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                item.setFlags(Qt.ItemIsDragEnabled | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                table.setItem(row, col, item)

        table.resizeColumnsToContents()
        table.resizeRowsToContents()
        button = QPushButton("&Ok")
        button.clicked.connect(self.close)
        button.setAutoDefault(True)

        vbox.addWidget(table)
        vbox.addWidget(button)

        self.parent.dialog.resize(640, 480)
        ret = self.parent.dialog.exec_()


    @display
    def set_font(self):
        """Change the font of all widgets through QFontDialog.
        """
        self.parent.dialog = QFontDialog(self.parent)
        self.parent.dialog.setOption(QFontDialog.DontUseNativeDialog)
        self.parent.dialog.resize(800, 600)
        ret = self.parent.dialog.exec_()
        if ret:
            font = self.parent.dialog.selectedFont()
            family = str(font.family())
            size = str(font.pointSize())
            font_css = str(self.parent.parent / "font.qss")
            with open(font_css, "w") as f:
                f.write("* {\n")
                f.write('    font-family: "{}";\n'.format(family))
                f.write('    font-size: {}px;\n'.format(size))
                f.write("}")
            self.parent.setStyleSheet("")
            with open(font_css, "r") as f:
                self.parent.setStyleSheet(f.read())


    def update_statusbar(self):
        """Update statubar's style

        This method will be called when swtitching the color theme.

        """
        if self.parent.style_theme == "light":
            if self.parent.colorspace == "rgb":
                self.parent.stat_css = {
                    "postion": "color: black;",
                    "R": "color: red;",
                    "G": "color: green;",
                    "B": "color: blue;",
                    "alpha": "color: black;",
                    }
            else:
                self.parent.stat_css = {
                    "postion": "color: black;",
                    "gray": "color: black;"
                }
        elif self.parent.style_theme == "dark":
            if self.parent.colorspace == "rgb":
                self.parent.stat_css = {
                    "postion": "color: white;",
                    "R": "color: white;",
                    "G": "color: white;",
                    "B": "color: white;",
                    "alpha": "color: white;",
                    }
            else:
                self.parent.stat_css = {
                    "postion": "color: white;",
                    "gray": "color: white;"
                }
        for stat, st in zip(self.parent.statbar_list, self.parent.stat_css.values()):
            stat.setStyleSheet(st)


    def set_file_rule(self):
        """Change the style of naming when saving frame as an image.
        """
        self.parent.filename_rule = next(self.parent.filename_rule_lst)
        self.parent.prop_table.item(5, 1).setText(self.parent.filename_rule)
