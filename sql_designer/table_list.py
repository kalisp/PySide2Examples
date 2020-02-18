from PySide2 import QtWidgets, QtCore


class TableListWidget(QtWidgets.QWidget):
    ''' Lists all tables in DB via model '''

    tableChanged = QtCore.Signal((str,))

    def __init__(self, db):
        super(TableListWidget, self).__init__()

        self.db = db
        self.model = TableListModel()
        self.model.input_data(db.tables())

        self.create_widgets()
        self.create_ui()
        self.create_connections()

        # self.setAutoFillBackground(True)

    def create_widgets(self):
        self.list_view = QtWidgets.QListView()
        self.list_view.setModel(self.model)

    def create_ui(self):
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.list_view)
        layout.addStretch()

        self.setLayout(layout)

        #self.setMinimumHeight(600)
        self.setFixedWidth(100)

    def create_connections(self):
        self.list_view.selectionModel().selectionChanged.connect(self.table_changed)

    def table_changed(self, selection):
        table = self.model.get_table_name(selection)
        self.tableChanged.emit(table)

# list of tables model
class TableListModel(QtCore.QAbstractListModel):
    ''' List presentation of tables in DB'''
    def __init__(self):
        super(TableListModel, self).__init__()

    def data(self, index, role) :
        if role == QtCore.Qt.DisplayRole:
            return self._data[index.row()]

    def get_table_name(self, selection):
        ''' Returns table name from_data based on selection in the list '''
        for index in selection.indexes():
            return self._data[index.row()]

    def rowCount(self, index):
        ''' Implemented function - to count items'''
        return len(self._data)

    def input_data(self, data):
        ''' Set non default data '''
        self._data = list(data)