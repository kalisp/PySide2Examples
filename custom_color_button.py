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
    

class CustomColorButton(QtWidgets.QLabel):
    """    
    Custom label mimicing button, when pressed brings QColorDialog and 
    sets its color with returned value 
    """
    
    color_changed = QtCore.Signal() # to emit signal for listeners, currently used only in TestDialog.create_connections
    
    def __init__(self, color=QtCore.Qt.white, parent=None):
        super(CustomColorButton, self).__init__(parent)
        self._color = QtGui.QColor() #private variable, empty color - invalid for now
        self.set_size(50, 14)
        self.set_color(color)
        
    def set_size(self, width, height):
        """ setter for size, sets as FixedSize """
        self.setFixedSize(width, height)
        
        
    # setter for private variable
    def set_color(self, color):
        color = QtGui.QColor(color) # passed in variable is stored as a QColor object
        
        if self._color != color:    
            self._color = color

            pixmap = QtGui.QPixmap(self.size())
            pixmap.fill(self._color)
            
            self.setPixmap(pixmap)
            
            self.color_changed.emit() # emit Signal when color changed
        
    def get_color(self):
        """ getter for private variable """
        return self._color
        
    def select_color(self):
        """ created QColorDialog and return selected color """
        color = QtWidgets.QColorDialog.getColor(self.get_color(), self, options=QtWidgets.QColorDialog.DontUseNativeDialog)
        
        if color.isValid(): # when user closes dialog without selecting color >> returned color is invalid
            self.set_color(color)
                
    def mouseReleaseEvent(self, mouse_event):
        """ trigger selection dialog, overriding QLabel method """
        if mouse_event.button() == QtCore.Qt.LeftButton: # limit only for LMB
            self.select_color()

class TestDialog(QtWidgets.QDialog):

    WINDOW_TITLE = "Custom Color Example"

    def __init__(self, parent=maya_main_window()):
        super(TestDialog, self).__init__(parent)

        self.setWindowTitle(self.WINDOW_TITLE)
        if cmds.about(ntOS=True):
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        elif cmds.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.setMinimumSize(320, 150)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.foreground_color_btn = CustomColorButton(QtCore.Qt.white)
        self.background_color_btn = CustomColorButton(QtCore.Qt.black)

        self.print_btn = QtWidgets.QPushButton("Print")
        self.close_btn = QtWidgets.QPushButton("Close")

    def create_layout(self):
        color_layout = QtWidgets.QFormLayout()
        color_layout.addRow("Foreground:", self.foreground_color_btn)
        color_layout.addRow("Background:", self.background_color_btn)

        color_grp = QtWidgets.QGroupBox("Color Options")
        color_grp.setLayout(color_layout)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setSpacing(2)
        button_layout.addStretch()
        button_layout.addWidget(self.print_btn)
        button_layout.addWidget(self.close_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.addWidget(color_grp)
        main_layout.addStretch()
        main_layout.addLayout(button_layout)

    def create_connections(self):
        self.foreground_color_btn.color_changed.connect(self.print_colors) # print selected color when color changed
        self.background_color_btn.color_changed.connect(self.print_colors)
        self.print_btn.clicked.connect(self.print_colors)
        self.close_btn.clicked.connect(self.close)

    def print_colors(self):
        foreground_color = self.foreground_color_btn.get_color()
        background_color = self.background_color_btn.get_color()
        
        print("Foreground Color: [{0}, {1}, {2}]".format(foreground_color.red(), foreground_color.green(), foreground_color.blue()))
        print("Background Color: [{0}, {1}, {2}]".format(background_color.red(), background_color.green(), background_color.blue()))


if __name__ == "__main__":

    try:
        test_dialog.close() # pylint: disable=E0601
        test_dialog.deleteLater()
    except:
        pass

    test_dialog = TestDialog()
    test_dialog.show()
