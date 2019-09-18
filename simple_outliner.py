from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import maya.cmds as cmds
import maya.OpenMayaUI as omui


def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class SimpleOutliner(QtWidgets.QDialog):

    WINDOW_TITLE = "Simple Outliner"

    def __init__(self, parent=maya_main_window()):
        super(SimpleOutliner, self).__init__(parent)

        self.setWindowTitle(self.WINDOW_TITLE)
        if cmds.about(ntOS=True):
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        elif cmds.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.setMinimumWidth(300)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

        self.refresh_tree_widget()

    def create_widgets(self):
        self.refresh_btn = QtWidgets.QPushButton("Refresh")

    def create_layout(self):
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.refresh_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)
        main_layout.addLayout(button_layout)

    def create_connections(self):
        self.refresh_btn.clicked.connect(self.refresh_tree_widget)

    def refresh_tree_widget(self):
        print("TODO: Implement refresh_tree_widget()")


if __name__ == "__main__":

    try:
        simple_outliner.close() # pylint: disable=E0601
        simple_outliner.deleteLater()
    except:
        pass

    simple_outliner = SimpleOutliner()
    simple_outliner.show()
