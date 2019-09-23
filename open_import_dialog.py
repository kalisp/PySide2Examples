from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import maya.OpenMaya as om
import maya.OpenMayaUI as omui
import maya.cmds as cmds


def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

# secondary approach to insert image
# possibly more powerful than simple QLabel approach
# can draw also primitives, lines etc. 
class CustomImageWidget(QtWidgets.QWidget):
    def __init__(self, width, height, image_path, parent = None):
        super(CustomImageWidget, self).__init__(parent)
        self.set_size(width, height)
        self.set_image(image_path)
        self.set_background_color(QtCore.Qt.black)
        
        
    def set_size(self, width, height):
        self.setFixedSize(width, height) # no need for explicit update() as size change triggers it automatically
        
    def set_image(self, image_path):    
        image = QtGui.QImage(image_path)
        image = image.scaled(self.width(), self.height(), QtCore.Qt.IgnoreAspectRatio, QtCore.Qt.SmoothTransformation) # creates new instance, not applying size on current
        
        self.pixmap = QtGui.QPixmap()
        self.pixmap.convertFromImage(image)
        self.update()
        
    def set_background_color(self, color):
        self.background_color = color
        self.update()
        
    # override parent method
    # called when displaying, resizing..
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        
        painter.fillRect(0, 0, self.width(), self.height(), self.background_color)
        painter.drawPixmap(self.rect(), self.pixmap)

class OpenImportDialog(QtWidgets.QDialog):
    
    FILE_FILTERS = "Maya (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;All Files (*.*)"
    
    selected_filter = "Maya (*.ma *.mb)"
    
    dlg_instance = None
    
    @classmethod
    def show_dialog(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = OpenImportDialog()
            
        if cls.dlg_instance.isHidden():
            cls.dlg_instance.show()
        else:
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()

    def __init__(self, parent=maya_main_window()):
        super(OpenImportDialog, self).__init__(parent)

        self.setWindowTitle("Open/Import/Reference")
        self.setMinimumSize(300, 80)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.create_title_label()
        self.filepath_le = QtWidgets.QLineEdit()
        self.select_file_path_btn = QtWidgets.QPushButton("...")
        self.select_file_path_btn.setIcon(QtGui.QIcon(":fileOpen.png"))
        self.select_file_path_btn.setToolTip("Select file")
        
        self.open_rb = QtWidgets.QRadioButton("Open")
        self.open_rb.setChecked(True)
        self.import_rb = QtWidgets.QRadioButton("Import")
        self.reference_rb = QtWidgets.QRadioButton("Reference")
        
        self.force_cb = QtWidgets.QCheckBox("Force")
        
        self.apply_btn = QtWidgets.QPushButton("Apply")
        self.close_btn = QtWidgets.QPushButton("Close")
        
    def create_title_label(self):
        image_path = "{}".format(cmds.internalVar(userScriptDir=True)) + "/images/title_image_with_alpha.png"
        
        
        self.title_label = CustomImageWidget(280, 60, image_path)

    def create_layout(self):
        file_path_layout = QtWidgets.QHBoxLayout()
        file_path_layout.addWidget(self.filepath_le)
        file_path_layout.addWidget(self.select_file_path_btn)
        
        radio_button_layout = QtWidgets.QHBoxLayout()
        radio_button_layout.addWidget(self.open_rb)
        radio_button_layout.addWidget(self.import_rb)
        radio_button_layout.addWidget(self.reference_rb)
        
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.apply_btn)
        btn_layout.addWidget(self.close_btn)
        
        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow("File:", file_path_layout)
        form_layout.addRow("", radio_button_layout)
        form_layout.addRow("", self.force_cb)
        #form_layout.addRow("", btn_layout)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.title_label)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(btn_layout)

    def create_connections(self):
        self.select_file_path_btn.clicked.connect(self.show_file_select_dialog)
        
        self.open_rb.toggled.connect(self.update_force_visibility)
        
        self.apply_btn.clicked.connect(self.load_file)
        
        self.close_btn.clicked.connect(self.close)
     
        
    def show_file_select_dialog(self):
        file_name, self.selected_filter = QtWidgets.QFileDialog.getOpenFileName(self, "Select file", "", self.FILE_FILTERS, self.selected_filter)
        if file_name:
            self.filepath_le.setText(file_name)
        
    def update_force_visibility(self, checked):
        self.force_cb.setVisible(checked)
        
    def load_file(self):
        file_path = self.filepath_le.text()
        
        if not file_path:
            return
            
        file_info = QtCore.QFileInfo(file_path)
        if not file_info.exists():
            om.MGlobal.displayError("File does not exist: {}".format(file_path))
            return
        
        if self.open_rb.isChecked():
            self.open_file(file_path)
        elif self.import_rb.isChecked():
            self.import_file(file_path)
        else:
            self.reference_file(file_path)
    
    def open_file(self, file_path):
        force = self.force_cb.isChecked() #check force checkbox
        if not force and cmds.file(q=True, modified=True): #check if file is modified and not selected force
            result = QtWidgets.QMessageBox.question(self, "Modified", "Current scene has unsaved changes. Continue?")
            if result == QtWidgets.QMessageBox.StandardButton.Yes:
                force = True
            else:
                return
        
        cmds.file(file_path, open=True, ignoreVersion=True, force=force)

    def import_file(self, file_path):
        cmd.file(file_path, i=True, ignoreVersion=True) #i is import flag
        
    def reference_file(self, file_path):
        cmd.file(file_path, reference=True, ignoreVersion=True)

if __name__ == "__main__":

    try:
        open_import_dialog.close() # pylint: disable=E0601
        open_import_dialog.deleteLater()
    except:
        pass

    open_import_dialog = OpenImportDialog()
    open_import_dialog.show()
