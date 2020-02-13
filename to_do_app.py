from PySide2 import QtCore, QtWidgets, QtGui
import json
import os.path

''' 
    Uses Model/View approach to show simple list of task with their status (Done/Not done) 
    Persists data in to_do.json for loading, all changes are saved immediately 
'''

tick = QtGui.QImage('tick.png') # https://p.yusukekamiyamane.com/

class ToDoModel(QtCore.QAbstractListModel ):

    def __init__(self):
        super(ToDoModel, self).__init__()

        self._data = [('Test Item1', False), ('Test Item2', False)] #  test data - label and status

    def rowCount(self, index):
        ''' Implemented function - to count items'''
        return len(self._data)

    def data(self, index, role):
        '''
            Implemented function - return text label of specific index

            :param index - position/coordinates which item view requests, values could be pulled by row() or column()
            :param role - should return only for QtCore.Qt.DisplayRole
        '''
        if role == QtCore.Qt.DisplayRole:
            text, status = self._data[index.row()]
            return text

        if role == QtCore.Qt.DecorationRole:
            _, status = self._data[index.row()]
            if status:
                return tick

    def add(self, label):
        '''
            Add to do item with 'label' text
        :param label:
        :return: None
        '''
        if label:
            self._data.append((label, False))
            self.layoutChanged.emit()

    def delete(self, selection):
        '''
            Deletes selected to do item
        :param selection: position/coordinates which item view requests, values could be pulled by row() or column()
        :return: None
        '''
        for select in selection:
            self._data.pop(select.row())

        self.layoutChanged.emit()

    def complete(self, selection):
        '''
            Completes selected to do item
        :param selection: position/coordinates which item view requests, values could be pulled by row() or column()
        :return: None
        '''
        for select in selection:
            text, status = self._data[select.row()]

            self._data[select.row()] = (text, True)

        self.dataChanged.emit(select.row(), select.row()) # needs to have top-left, bottom-right values

    def set_data(self, json_data):
        '''
            Sets data from saved file
        :param json_data: previously saved data
        :return: None
        '''
        self._data = json_data
        self.layoutChanged.emit()

    def get_data(self):
        '''
            Returns data for persisting
        :return: string
        '''
        return self._data

class MainWindow(QtWidgets.QMainWindow):
    SAVE_FILE_NAME = 'to_do.json'

    def __init__(self):
        super(MainWindow, self).__init__()

        self.model = ToDoModel()

        self.setWindowTitle('To Do App')

        self.create_widgets()
        self.create_ui()
        self.create_connections()

        self.load()

    def create_widgets(self):
        self.list_view = QtWidgets.QListView()
        self.list_view.setModel(self.model)
        self.delete_btn = QtWidgets.QPushButton("Delete")
        self.delete_btn.setEnabled(False)
        self.complete_btn = QtWidgets.QPushButton("Complete")
        self.complete_btn.setEnabled(False)
        self.line_edit = QtWidgets.QLineEdit()
        self.add_btn = QtWidgets.QPushButton("Add To Do")
        self.add_btn.setEnabled(False)

    def create_ui(self):
        central_widget = QtWidgets.QWidget()

        outer_layout = QtWidgets.QVBoxLayout()
        outer_layout.addWidget(self.list_view)

        # wrapper for edit buttons
        edit_button_layout = QtWidgets.QHBoxLayout()
        edit_button_layout.addWidget(self.delete_btn)
        edit_button_layout.addWidget(self.complete_btn)

        outer_layout.addLayout(edit_button_layout)
        outer_layout.addWidget(self.line_edit)
        outer_layout.addWidget(self.add_btn)

        central_widget.setLayout(outer_layout)

        self.setCentralWidget(central_widget)

    def create_connections(self):
        ''' Set slots and signals '''
        self.add_btn.clicked.connect(self.add)
        self.delete_btn.clicked.connect(self.delete)
        self.complete_btn.clicked.connect(self.complete)

        self.line_edit.textChanged.connect(self.update_buttons)
        self.list_view.selectionModel().selectionChanged.connect(self.update_buttons)

    def update_buttons(self):
        ''' Disable Add button if text empty, disable edit buttons if nothing selected '''
        self.add_btn.setEnabled(False)
        if self.line_edit.text():
            self.add_btn.setEnabled(True)

        self.delete_btn.setEnabled(True)
        self.complete_btn.setEnabled(True)
        if not self.list_view.selectedIndexes():
            self.delete_btn.setEnabled(False)
            self.complete_btn.setEnabled(False)

    def add(self):
        ''' After clicked button, adds item to model via its method '''
        if self.line_edit.text():
            self.model.add(self.line_edit.text())
            self.line_edit.setText('')
            self.update_buttons()
            self.save()

    def delete(self):
        ''' After delete button is clicke '''
        selection = self.list_view.selectedIndexes()
        if selection:
            self.model.delete(selection)
            self.list_view.clearSelection()
            self.update_buttons()
            self.save()

    def complete(self):
        ''' After Complete button is pressed, completes item(s) '''
        selection = self.list_view.selectedIndexes()
        if selection:
            self.model.complete(selection)
            self.list_view.clearSelection()
            self.update_buttons()
            self.save()

    def load(self):
        ''' Loads persisted data, if exists '''
        if os.path.exists(self.SAVE_FILE_NAME):
            with open(self.SAVE_FILE_NAME, 'r') as fp:
                self.model.set_data(json.load(fp))

    def save(self):
        ''' Persists current state of model into json file '''
        with open(self.SAVE_FILE_NAME, 'w') as fp:
            data = json.dump(self.model.get_data(), fp)



if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    win = MainWindow()
    win.show()

    app.exec_()