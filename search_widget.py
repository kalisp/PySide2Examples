from PySide2 import QtCore, QtWidgets, QtGui

'''
    Lists various lights/switches in the building and their state (On/Off).
    Allows searching by name of item and search auto finishing.
    Exercise for PySide2
'''

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.items = []

        item_names = ["Kitchen Light", "Light", "Patio Light"] # for testing only
        for name in item_names:
            self.items.append(ItemWidget(name))

        self.completer = QtWidgets.QCompleter(item_names)
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)

        self.create_widgets()
        self.create_ui()
        self.create_connections()

        self.setWindowTitle("Light control panel")

    def create_widgets(self):
        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setCompleter(self.completer)

    def create_connections(self):
        self.search_input.textChanged.connect(self.text_changed)

    def create_ui(self):
        ''' Creates layout and adds widgets '''

        centralWidget = QtWidgets.QWidget()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.search_input)

        item_container = QtWidgets.QWidget()
        item_container_layout = QtWidgets.QVBoxLayout()
        for item in self.items:
            item_container_layout.addWidget(item)
        item_container.setLayout(item_container_layout)

        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidget(item_container)
        scroll_area.setAlignment(QtCore.Qt.AlignTop)
        layout.addWidget(scroll_area)
        layout.addStretch()

        centralWidget.setLayout(layout)

        self.setCentralWidget(centralWidget)

    def text_changed(self):
        ''' Refresh list of items '''
        for item in self.items:
            txt = self.search_input.text().lower()
            if  txt == '' or item.get_name().lower().startswith(txt):
                item.show()
            else:
                item.hide()

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

    def get_name(self):
        ''' Public API function '''
        return self.name

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

    def hide(self):
        ''' Public API function - hides item '''
        self.set_visible(False)

    def show(self):
        ''' Public API function - show item '''
        self.set_visible(True)

    def set_visible(self, is_visible):
        self.setVisible(is_visible)
        self.label.setVisible(is_visible)
        self.on_btn.setVisible(is_visible)
        self.off_btn.setVisible(is_visible)

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    win = MainWindow()
    win.show()

    app.exec_()