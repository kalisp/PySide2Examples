from PySide2 import QtWidgets, QtCore, QtSql


class TableContentWidget(QtWidgets.QWidget):
    ''' Shows content of the DB table or query in table manner '''
    def __init__(self, db):
        super(TableContentWidget, self).__init__()

        self.db = db

        self.create_widgets()
        self.create_ui()
        self.create_connections()

        self.set_model('table')

    def create_widgets(self):
        self.table_view = QtWidgets.QTableView()

    def create_ui(self):
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.table_view)
        layout.addStretch()
        self.setLayout(layout)

    def create_connections(self):
        pass

    def populate_table(self, table):
        ''' Reloads content of widget with table provided by argument
            Called after selection changes in table list widget
        '''
        # no need to emit anything further, model takes care of it itself
        self.model.setTable(table)
        self.model.select()

    def populate_query(self, query):
        ''' Reloads content of the widget based on a arbitrary query '''
        self.model.setQuery(query)
        self.model.query().exec_()

    def set_model(self, model_type):
        ''' Changes model based on showing data via left column or via query '''
        if model_type == 'table':
            self.model = TableContentModel(self.db)
        elif model_type == 'query':
            self.model = TableContentQueryModel(self.db)

        self.table_view.setModel(self.model)

    def get_model(self):
        ''' Getter for model '''
        return self.model

class TableContentModel(QtSql.QSqlTableModel):
    ''' DB model that shows content of one table '''
    def __init__(self, db):
        super(TableContentModel, self).__init__(None, db)

class TableContentQueryModel(QtSql.QSqlQueryModel):
    ''' DB model that shows content of arbitrary query '''
    def __init__(self, db):
        super(TableContentQueryModel, self).__init__()

# # content of sql table
# class TableContentTestModel(QtCore.QSqlTableModel):
#
#     def __init__(self, db):
#         super(TableContentModel, self).__init__(None, db)
#
#         self._header_data = ['first', 'last', 'email', 'dob']
#         self._data = [
#                         ['John', 'Doe', 'john@doe.com', '1990-01-01'],
#                         ['Jane', 'Doe', 'jane@doe.com', '1995-01-01']
#         ]
#
#     def data(self, index, role) :
#
#         if role == QtCore.Qt.DisplayRole:
#             return self._data[index.row()][index.column()]
#
#         #if role == QtCore.Qt.DecorationRole:
#
#     def headerData(self, section, orientation, role):
#         if role == QtCore.Qt.DisplayRole:
#             if orientation == QtCore.Qt.Horizontal:
#                 return str(self._header_data[section])
#
#             if orientation == QtCore.Qt.Vertical:
#                 pass
#
#     def rowCount(self, index):
#         ''' Implemented function - to count items '''
#         return len(self._data)
#
#     def columnCount(self, index):
#         ''' Implemented function - to count columns '''
#         return len(self._data[0]) if self._data  else 0
