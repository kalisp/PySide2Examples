from functools import partial

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui


from collections import defaultdict

import custom_color_button # from custom_color_button.py - implemented example

def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)



class LightItem(QtWidgets.QWidget):

    SUPPORTED_TYPES = ["ambientLight", "directionalLight", "pointLight", "spotLight"]
    EMIT_TYPES = ["directionalLight", "pointLight", "spotLight"]

    def __init__(self, shape_name, parent=None):
        super(LightItem, self).__init__(parent)

        self.setFixedHeight(26)
        
        self.shape_name = shape_name

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.light_type_btn = QtWidgets.QPushButton()
        self.light_type_btn.setFixedSize(20, 20)
        self.light_type_btn.setFlat(True)
        
        self.light_visibility_btn = QtWidgets.QCheckBox()
        
        self.light_name_label = QtWidgets.QLabel("Placeholder")
        self.light_name_label.setFixedWidth(120)
        self.light_name_label.setAlignment(QtCore.Qt.AlignCenter)
        
        light_type = self.get_light_type()
        if light_type in self.SUPPORTED_TYPES:
            self.intensity_dsb = QtWidgets.QDoubleSpinBox()
            self.intensity_dsb.setRange(0.0, 100.0)
            self.intensity_dsb.setDecimals(3)
            self.intensity_dsb.setSingleStep(0.1)
            self.intensity_dsb.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
            
            self.color_btn = CustomColorButton()
            
            if light_type in self.EMIT_TYPES:
                self.emit_diffuse_cb = QtWidgets.QCheckBox()
                self.emit_specular_cb = QtWidgets.QCheckBox()
        
        self.update_values()
        

    def create_layout(self):
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.light_type_btn)
        main_layout.addWidget(self.light_visibility_btn)
        main_layout.addWidget(self.light_name_label)
        
        light_type = self.get_light_type()
        if light_type in self.SUPPORTED_TYPES:
            main_layout.addWidget(self.intensity_dsb)
            main_layout.addSpacing(10)
            main_layout.addWidget(self.color_btn)
            
            if light_type in self.EMIT_TYPES:
                main_layout.addSpacing(34)
                main_layout.addWidget(self.emit_diffuse_cb)
                main_layout.addSpacing(50)
                main_layout.addWidget(self.emit_specular_cb)
        
        main_layout.addStretch()
        

    def create_connections(self):
        pass
        
    def update_values(self):
        self.light_name_label.setText(self.get_transform_name())
        self.light_type_btn.setIcon(self.get_light_type_icon())
        self.light_visibility_btn.setChecked(self.is_visible())
        
        light_type = self.get_light_type()
        if light_type in self.SUPPORTED_TYPES:
            self.intensity_dsb.setValue(self.get_intensity())
            self.color_btn.set_color(self.get_color())
            
            if light_type in self.EMIT_TYPES:
                self.emit_diffuse_cb.setChecked(self.get_diffuse())
                self.emit_specular_cb.setChecked(self.get_specular())
        
    def get_transform_name(self):
        return cmds.listRelatives(self.shape_name, parent=True)[0]
        
    def get_light_type(self):
        return cmds.objectType(self.shape_name)
        
    def get_light_type_icon(self):
        light_type = self.get_light_type()
        
        if light_type in self.SUPPORTED_TYPES:
            icon = QtGui.QIcon(":{}.svg".format(light_type))
        else:
            icon = QtGui.QIcon(":Light.png")
            
        return icon
        
    def get_attribute_value(self, name, attribute):
        return cmds.getAttr('{}.{}'.format(name, attribute))
        
    def is_visible(self):
        transform_name = self.get_transform_name()
        return self.get_attribute_value(transform_name, 'visibility')
        
    def get_intensity(self):
        return self.get_attribute_value(self.shape_name, 'intensity')

    def get_color(self):
        temp_color = self.get_attribute_value(self.shape_name, 'color')[0]
        
        return QtGui.QColor(temp_color[0] * 255, temp_color[1] * 255, temp_color[2] * 2)
        
    def get_diffuse(self):
        return self.get_attribute_value(self.shape_name, 'emitDiffuse')

    def get_specular(self):
        return self.get_attribute_value(self.shape_name, 'emitSpecular')

class LightPanel(QtWidgets.QDialog):

    WINDOW_TITLE = "Light Panel"

    def __init__(self, parent=maya_main_window()):
        super(LightPanel, self).__init__(parent)

        self.setWindowTitle(self.WINDOW_TITLE)
        if cmds.about(ntOS=True):
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        elif cmds.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.resize(500, 260)
        
        self.light_items = []

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.refreshButton = QtWidgets.QPushButton("Refresh Lights")

    def create_layout(self):
        # header
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.addSpacing(100)
        header_layout.addWidget(QtWidgets.QLabel("Light"))
        header_layout.addSpacing(50)
        header_layout.addWidget(QtWidgets.QLabel("Intensity"))
        header_layout.addSpacing(44)
        header_layout.addWidget(QtWidgets.QLabel("Color"))
        header_layout.addSpacing(24)
        header_layout.addWidget(QtWidgets.QLabel("Emit Diffuse"))
        header_layout.addSpacing(10)
        header_layout.addWidget(QtWidgets.QLabel("Emit Spec"))
        header_layout.addStretch()

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.refreshButton)
        
        light_list_wdg = QtWidgets.QWidget()
                
        self.light_layout = QtWidgets.QVBoxLayout(light_list_wdg)
        self.light_layout.setContentsMargins(2, 2, 2, 2)
        self.light_layout.setSpacing(3)
        self.light_layout.setAlignment(QtCore.Qt.AlignTop)
        
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(light_list_wdg)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.addLayout(header_layout)
        
        main_layout.addWidget(scroll_area)
        
        main_layout.addLayout(button_layout)

    def create_connections(self):
        self.refreshButton.clicked.connect(self.refresh_lights)
        
    
    def get_lights_in_scene(self): 
        """ Use Maya command to get list of lights in the scene """
        return cmds.ls(type='light')
        

    def refresh_lights(self):
        """ Redo list of all lists in dialog """
        self.clear_lights()
        
        lights = self.get_lights_in_scene()
        print('Lights: {}'.format(lights))
        if lights:        
            for light in lights:
                light_item = LightItem(light)
                self.light_items.append(light_item)
                
                self.light_layout.addWidget(light_item)

    def clear_lights(self):
        """ Clear list of lists, should be called before refresh to purge list of lights """
        self.light_items = []
        
        for i in range(self.light_layout.count()):
            item = self.light_layout.itemAt(i) # get item on index
            if item:
                wdg = item.widget() # Returns the widget managed by this item
                if wdg:
                    wdg.deleteLater()

    # called when Dialog shown (even for the first time)
    def showEvent(self, event):
        self.refresh_lights()

    def closeEvent(self, event):
        self.clear_lights()


if __name__ == "__main__":

    try:
        light_panel_dialog.close() # pylint: disable=E0601
        light_panel_dialog.deleteLater()
    except:
        pass

    light_panel_dialog = LightPanel()
    light_panel_dialog.show()
