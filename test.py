import sys
from PySide2.QtWidgets import *
from PySide2.QtCore import *



class Window(QWidget):

    def __init__(self, *args, parent=None):
        super(Window, self).__init__(parent)

        self.resize(800, 600)

        self.b = QPushButton("Push")
        self.b.clicked.connect(self.dialog)
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.b)
        self.setLayout(self.vbox)


    def dialog(self):
        diag = QFontDialog()
        diag.setOption(QFontDialog.DontUseNativeDialog)
        #ret, font = diag.getFont()
        #font = diag.selectedFont()
        ret = diag.exec_()
        print(ret)
        print(diag.selectedFont())
        self.setFont(font)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = Window()
    main_window.show()
    sys.exit(app.exec_())