from PySide2 import QtWidgets
from sql_designer import main_window

''' Simple SQLite editor, setups db, adds 2 tables, insert some data.
    Lists all tables to show their data. 
    Allow writing sql query and show its results
'''

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    win = main_window.MainWindow()
    win.show()

    app.exec_()