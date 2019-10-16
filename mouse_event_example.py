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



class MoveableWidget(QtWidgets.QWidget):

    def __init__(self, x, y, width, height, color, parent=None):
        super(MoveableWidget, self).__init__(parent)

        self.setFixedSize(width, height)
        self.move(x, y)

        self.color = color
        self.original_color = color

        self.move_enabled = False

    def mousePressEvent(self, mouse_event):
        print("Mouse Button Pressed")
        
        if mouse_event.button() == QtCore.Qt.LeftButton:
            self.initial_pos = self.pos()
            self.global_pos = mouse_event.globalPos()
            self.move_enabled = True
            

    def mouseReleaseEvent(self, mouse_event):
        if self.move_enabled:
            self.move_enabled = False

    def mouseDoubleClickEvent(self, mouse_event):
        print("Mouse Double-Click")
        
        if self.color == self.original_color:
            self.color = QtCore.Qt.yellow
        else:
            self.color = self.original_color
        
        self.update() # explicitly call refresh

    def mouseMoveEvent(self, mouse_event):
        if self.move_enabled:
            diff = mouse_event.globalPos() - self.global_pos
            print("diff: {}".format(diff))
            self.move(self.initial_pos + diff)

    def paintEvent(self, paint_event):
        painter = QtGui.QPainter(self)
        painter.fillRect(paint_event.rect(), self.color)



class MouseEventExample(QtWidgets.QDialog):

    WINDOW_TITLE = "Mouse Event Example"

    def __init__(self, parent=maya_main_window()):
        super(MouseEventExample, self).__init__(parent)

        self.setWindowTitle(self.WINDOW_TITLE)
        if cmds.about(ntOS=True):
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        elif cmds.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.setMinimumSize(400, 400)

        self.create_widgets()
        self.create_layout()

    def create_widgets(self):
        self.red_widget = MoveableWidget(100, 100, 24, 24, QtCore.Qt.red, self)
        self.blue_widget = MoveableWidget(300, 300, 24, 24, QtCore.Qt.blue, self)

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)


if __name__ == "__main__":

    try:
        example_dialog.close() # pylint: disable=E0601
        example_dialog.deleteLater()
    except:
        pass

    example_dialog = MouseEventExample()
    example_dialog.show()
