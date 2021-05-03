import os
from PyQt5.QtWidgets import (QApplication, QWidget, QLineEdit,
                             QInputDialog, QFileDialog, QMessageBox,
                             QGridLayout, QLabel, QPushButton, QFrame)

class InputDialog(QWidget):
    def __init__(self):
        super(InputDialog,self).__init__()

        label1 = QLabel("Make/Open file:")
        label2 = QLabel("pathFile:")
        label3 = QLabel("profil:")

        self.nameLable = QLabel()
        self.nameLable.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.pathFile = QLabel()
        self.pathFile.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.profilLable = QLabel()
        self.profilLable.setFrameStyle(QFrame.Panel | QFrame.Sunken)

        nameButton = QPushButton("...")
        nameButton.clicked.connect(self.selectName)
        profilButton = QPushButton("...")
        profilButton.clicked.connect(self.selectProfil)

        mainLayout = QGridLayout()
        mainLayout.addWidget(label1,          0, 0)
        mainLayout.addWidget(self.nameLable,  0, 1)
        mainLayout.addWidget(nameButton,      0, 2)
        mainLayout.addWidget(label3,          1, 0)
        mainLayout.addWidget(self.profilLable,1, 1)
        mainLayout.addWidget(profilButton,    1, 2)
        mainLayout.addWidget(label2,          2, 0)
        mainLayout.addWidget(self.pathFile,   2, 1, 1, 2)
        mainLayout.setRowMinimumHeight(2, 40)
        mainLayout.addWidget(QLabel(), 3, 0)
        mainLayout.setRowStretch(3, 1)
        mainLayout.setColumnMinimumWidth(1, 200 )
        mainLayout.setSpacing(5)

        self.setLayout(mainLayout)

    def selectName(self):
        items = ("Make a new testfile", "Open an existing one")
        item, okPressed = QInputDialog.getItem(self,
                                    "Select",
                                    "You want to: ",
                                    items, 0, False)
        if okPressed :
            self.nameLable.setText(item)
            if item == "Open an existing one" :
                pathFile, ok = QFileDialog.getOpenFileName(self,
                                    "Open a file",
                                    "",
                                    "All Files(*);;Python Files (*.py)")
                if pathFile:
                    self.pathFile.setText(pathFile)
                    self.profilLable.setText("")
            elif item == "Make a new testfile" :
                self.selectProfil()
        else:
            sys.exit(0)

    def selectProfil(self):
        if self.nameLable.text() == "Make a new testfile" :
            self.pathFile.setText("")
            items2 = ("New profil", "Existing profil")
            item2, okPressed2 = QInputDialog.getItem(self,"Select", "", items2, 0, False)
            if not okPressed2:      #pass so come back to the previous inputDialog
                 self.selectName()
            self.profilLable.setText(item2)
            if item2 == "New profil" :
                name, ok = QInputDialog.getText(self,
                                     "Profil name",
                                     "Enter file name:",
                                     QLineEdit.Normal)
                if ok and name:
                    dirName = 'Profiles'                    #  /' + name
                    if not os.path.exists(dirName):
                        os.makedirs(dirName)

                    filepath = os.path.join(dirName, name)
                    if not os.path.isfile(filepath):
                        f = open(filepath, "a")
                        f.close()
                        self.pathFile.setText(os.path.abspath(filepath))
                    else :
                        QMessageBox.about(self, 'Error','Profile name already taken')
                        self.selectProfil()
                elif ok and not name:
                    QMessageBox.about(self, 'Error', 'Enter a name')

                else :
                    #here I'd like to return to the initial inputDialog if the user press cancel
                    self.selectProfil()
            elif item2 == "Existing profil" :
                pathprofil, ok = QFileDialog.getOpenFileName(self,
                                             "Nom de profil",
                                             "", "All Files(*)")
                self.pathFile.setText(pathprofil)
        elif not self.nameLable.text():
            QMessageBox.about(self, 'Error', 'Select `Make / Open file`')
            self.selectName()

if __name__=="__main__":
    import sys
    app    = QApplication(sys.argv)
    myshow = InputDialog()
    myshow.setWindowTitle("InputDialog")
    myshow.show()
    sys.exit(app.exec_())