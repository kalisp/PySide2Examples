from PySide2 import QtCore, QtGui, QtWidgets
import table_content, table_list
from db import init_db



class MainWindow(QtWidgets.QMainWindow):
    ''' Main window, contains multiple columns:
        left - list of tables in DB
        top right - editor for SQL Query
        bottom right - table to view data
    '''
    def __init__(self):
        super(MainWindow, self).__init__()

        db = init_db()

        self.left_widget = table_list.TableListWidget(db)
        self.table_content_widget = table_content.TableContentWidget(db)

        self.setWindowTitle('SQL editor')

        self.create_widgets()
        self.create_ui()
        self.create_connections()

    def create_widgets(self):
        self.btn_start = QtWidgets.QPushButton("Run Query")
        self.query_text_edit = QtWidgets.QTextEdit()

    def create_ui(self):
        ''' Three views, list of tables, sql query, table content '''
        wrapper_layout = QtWidgets.QHBoxLayout()
        wrapper_layout.setContentsMargins(2, 2, 2, 2)

        left_layout = QtWidgets.QVBoxLayout()
        left_layout.addWidget(self.left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addStretch()

        right_layout = QtWidgets.QVBoxLayout()
        right_layout.addWidget(self.query_text_edit)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.btn_start)
        button_layout.addStretch()

        right_layout.addLayout(button_layout)

        right_layout.addWidget(self.table_content_widget) # content of the table
        right_layout.setContentsMargins(0, 0, 0, 0)

        wrapper_layout.addLayout(left_layout)
        wrapper_layout.addLayout(right_layout)

        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(wrapper_layout)

        self.setCentralWidget(central_widget)

    def create_connections(self):
        self.left_widget.tableChanged.connect(self.table_changed)   # TODO
        self.btn_start.clicked.connect(self.start_query)

    def table_changed(self, table):
        ''' Slot to call repopulate table on table content widget '''
        self.table_content_widget.set_model('table')
        self.table_content_widget.populate_table(table)

    def start_query(self):
        ''' Called after Start query button is clicked
            Sets model to QSqlQueryModel instead of QSqlTableModel
        '''
        query = self.query_text_edit.toPlainText()
        if query != '':
            self.table_content_widget.set_model('query')
            self.table_content_widget.populate_query(query)

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    win = MainWindow()
    #win.resize(800, 600)
    win.show()

    app.exec_()