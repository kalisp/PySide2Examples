from PySide2 import QtCore, QtWidgets, QtGui

'''
    Lists various lights/switches and their state (On/Off).
    Allows searching by name of item and search auto finishing.
'''

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        centralWidget = QtWidgets.QWidget()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(ItemWidget("Light"))
        layout.addStretch()
        centralWidget.setLayout(layout)

        self.setCentralWidget(centralWidget)

class ItemWidget(QtWidgets.QWidget):

    def __init__(self, name):
        super(ItemWidget, self).__init__()

        self.name = name

        self.create_widgets()
        self.create_ui()
        self.create_connections()

        self.off_btn_clicked()

    def create_widgets(self):
        self.label = QtWidgets.QLabel(self.name)
        self.on_btn = QtWidgets.QPushButton("On")
        self.off_btn = QtWidgets.QPushButton("Off")

    def create_connections(self):
        self.on_btn.clicked.connect(self.on_btn_clicked)
        self.off_btn.clicked.connect(self.off_btn_clicked)

    def create_ui(self):
        ''' Creates layout and adds widgets'''
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.label)
        layout.addStretch()
        layout.addWidget(self.on_btn)
        layout.addWidget(self.off_btn)

        self.setLayout(layout)

    def on_btn_clicked(self):
        self.is_on = True
        self.update_background()

    def off_btn_clicked(self):
        self.is_on = False
        self.update_background()

    def update_background(self):
        ''' Called after any button is clicked.
        '''
        if self.is_on:
            self.on_btn.setStyleSheet("background-color: green; color: #fff")
            self.off_btn.setStyleSheet("background-color: none; color: none")
        else:
            self.on_btn.setStyleSheet("background-color: none; color: none")
            self.off_btn.setStyleSheet("background-color: red; color: #fff")


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    win = MainWindow()
    win.show()

    app.exec_()