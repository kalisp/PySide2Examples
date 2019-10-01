from functools import partial

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui


from collections import defaultdict



def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

class CustomColorButton(QtWidgets.QWidget):

    color_changed = QtCore.Signal(QtGui.QColor)


    def __init__(self, color=QtCore.Qt.white, parent=None):
        super(CustomColorButton, self).__init__(parent)

        self.setObjectName("CustomColorButton")

        self.create_control()

        self.set_size(50, 14)
        self.set_color(color)

    def create_control(self):
        """ 1) Create the colorSliderGrp """
        window = cmds.window()
        color_slider_name = cmds.colorSliderGrp()

        """ 2) Find the colorSliderGrp widget """
        self._color_slider_obj = omui.MQtUtil.findControl(color_slider_name)
        if self._color_slider_obj:
            self._color_slider_widget = wrapInstance(long(self._color_slider_obj), QtWidgets.QWidget)

            """ 3) Reparent the colorSliderGrp widget to this widget """
            main_layout = QtWidgets.QVBoxLayout(self)
            main_layout.setObjectName("main_layout")
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.addWidget(self._color_slider_widget)

            """ 4) Identify/store the colorSliderGrp’s child widgets (and hide if necessary)  """
            self._slider_widget = self._color_slider_widget.findChild(QtWidgets.QWidget, "slider")
            if self._slider_widget:
                self._slider_widget.hide()

            self._color_widget = self._color_slider_widget.findChild(QtWidgets.QWidget, "port")

            cmds.colorSliderGrp(self.get_full_name(), e=True, changeCommand=partial(self.on_color_changed))


        cmds.deleteUI(window, window=True)

    def get_full_name(self):
        return omui.MQtUtil.fullName(long(self._color_slider_obj))

    def set_size(self, width, height):
        self._color_slider_widget.setFixedWidth(width)
        self._color_widget.setFixedHeight(height)

    def set_color(self, color):
        color = QtGui.QColor(color)
        
        print('new {} old {}'.format(color, self.get_color()))

        if color != self.get_color():
            cmds.colorSliderGrp(self.get_full_name(), e=True, rgbValue=(color.redF(), color.greenF(), color.blueF()))
            self.on_color_changed()

    def get_color(self):
        color = cmds.colorSliderGrp(self.get_full_name(), q=True, rgbValue=True)

        color = QtGui.QColor(color[0] * 255, color[1] * 255, color[2] * 255)
        return color

    def on_color_changed(self, *args):
        self.color_changed.emit(self.get_color())

class LightItem(QtWidgets.QWidget):

    SUPPORTED_TYPES = ["ambientLight", "directionalLight", "pointLight", "spotLight"]
    EMIT_TYPES = ["directionalLight", "pointLight", "spotLight"]
    
    node_deleted = QtCore.Signal(str)

    def __init__(self, shape_name, parent=None):
        super(LightItem, self).__init__(parent)

        self.setFixedHeight(26)
        
        self.shape_name = shape_name
        # get unique id based on shape name, used to rename light if needed
        self.uuid = cmds.ls(shape_name, uuid=True) 
        self.script_jobs = []

        self.create_widgets()
        self.create_layout()
        self.create_connections()
        
        self.create_script_jobs()

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
        self.light_type_btn.clicked.connect(self.select_light)
        self.light_visibility_btn.toggled.connect(self.set_visibility)
        
        light_type = self.get_light_type()
        if light_type in self.SUPPORTED_TYPES:
            self.intensity_dsb.editingFinished.connect(self.on_intensity_change)
            self.color_btn.color_changed.connect(self.set_color)
            
            if light_type in self.EMIT_TYPES:
                self.emit_diffuse_cb.toggled.connect(self.set_emit_diffuse)
                self.emit_specular_cb.toggled.connect(self.set_emit_specular)
        
    def update_values(self):
        print("update_values " + self.get_transform_name())
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
        
    # helper function for filling UI
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
        
    def set_attribute_value(self, name, attribute, *args): 
        attr_name = "{}.{}".format(name, attribute) # full attribute name consists of node name + attribute
        cmds.setAttr(attr_name, *args) # sent variable count of attribute values
        
        
    def is_visible(self):
        transform_name = self.get_transform_name()
        return self.get_attribute_value(transform_name, 'visibility')
        
    def get_intensity(self):
        return self.get_attribute_value(self.shape_name, 'intensity')

    def get_color(self):
        temp_color = self.get_attribute_value(self.shape_name, 'color')[0]
        
        return QtGui.QColor(temp_color[0] * 255, temp_color[1] * 255, temp_color[2] * 255)
        
    def get_diffuse(self):
        return self.get_attribute_value(self.shape_name, 'emitDiffuse')

    def get_specular(self):
        return self.get_attribute_value(self.shape_name, 'emitSpecular')
        
    # helper methods for changing attribute values in Maya scene via Light Panel UI
    def select_light(self):
        cmds.select(self.get_transform_name())
        
    def set_visibility(self, checked):
        self.set_attribute_value(self.get_transform_name(), "visibility", checked)
        
    def on_intensity_change(self):
        self.set_attribute_value(self.shape_name, "intensity", self.intensity_dsb.value())
        
    def set_color(self, color):
        print("set_color {}".format(color))
        self.set_attribute_value(self.shape_name, "color", color.redF(), color.greenF(), color.blueF()) # send colors as a floats
        
    def set_emit_diffuse(self, checked):
        self.set_attribute_value(self.shape_name, "emitDiffuse", checked)
        
    def set_emit_specular(self, checked):
        self.set_attribute_value(self.shape_name, "emitSpecular", checked)
        
    def on_node_deleted(self):
        """ Calls emit signal when light (node) is deleted """
        self.node_deleted.emit(self.shape_name)
        
    def on_name_changed(self):
        """ Called when light name is changed in Maya """
        print("on_name_changed")
        self.shape_name = cmds.ls(self.uuid)[0] # get new shape name via uuid
        self.update_values() # set new name
        
    def add_attribute_change_script_job(self, name, attribute):
        """ Helper method for changes in visibility, color, emits... """
        self.script_jobs.append(cmds.scriptJob(attributeChange=("{}.{}".format(name, attribute), partial(self.update_values))))

    def create_script_jobs(self):
        """ Create script jobs - on node deleted,... """
        self.delete_script_jobs() #purge existing
        
        self.add_attribute_change_script_job(self.get_transform_name(), 'visibility')
        
        light_type = self.get_light_type()
        if light_type in self.SUPPORTED_TYPES:
            self.add_attribute_change_script_job(self.get_transform_name(), 'color')
            self.add_attribute_change_script_job(self.get_transform_name(), 'intensity')
            
            if light_type in self.EMIT_TYPES:
               self.add_attribute_change_script_job(self.get_transform_name(), 'emitDiffuse') 
               self.add_attribute_change_script_job(self.get_transform_name(), 'emitSpecular')
               
        self.script_jobs.append(cmds.scriptJob(nodeDeleted=(self.shape_name, partial(self.on_node_deleted))))
        self.script_jobs.append(cmds.scriptJob(nodeNameChanged=(self.shape_name, partial(self.on_name_changed))))
        
    def delete_script_jobs(self):
        """ Loops through existing script jobs, kills them via command """
        for script_number in self.script_jobs:
            # node could be deleted outside, script job gets deleted automatically
            # evalDeferred let Maya delete object first
            cmds.evalDeferred("if cmds.scriptJob(exists={0}):\tcmds.scriptJob(kill={0}, force=True)".format(script_number))
            
        self.script_jobs = []

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
        self.script_jobs = []

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
        if lights:        
            for light in lights:
                light_item = LightItem(light)
                light_item.node_deleted.connect(self.on_node_deleted) # hook slot to LightItem signal
                self.light_items.append(light_item)
                
                self.light_layout.addWidget(light_item)

    def clear_lights(self):
        """ Clear list of lists, should be called before refresh to purge list of lights """
        for light in self.light_items:# delete all existing script job for light
            light.delete_script_jobs()
        
        self.light_items = []
        
        for i in range(self.light_layout.count()):
            item = self.light_layout.itemAt(i) # get item on index
            if item:
                wdg = item.widget() # Returns the widget managed by this item
                if wdg:
                    wdg.deleteLater()
                    
    def create_script_jobs(self):
        """ Called to create 2 script jobs """
        self.script_jobs.append(cmds.scriptJob(event=["DagObjectCreated", partial(self.on_dag_object_created)]))#script job created when new object
        self.script_jobs.append(cmds.scriptJob(event=["Undo", partial(self.on_undo)]))
        
    def delete_script_jobs(self):
        """ Loops through existing script jobs, kills them via command """
        for script_number in self.script_jobs:
            cmds.scriptJob(kill=script_number)
            
        self.script_jobs = []
        
    def on_dag_object_created(self):
        """ Called via scriptJob when new DAG object created """
        if len(self.light_items) != len(cmds.ls(type="light")):
            self.refresh_lights()
            print("New light created")
            
    def on_undo(self):
        """ Called via scriptJob when undo pressed """
        if len(self.light_items) != len(cmds.ls(type="light")):
            self.refresh_lights()
            print("Undo light created")
            
    def on_node_deleted(self):
        """ Slot called by LightItem.on_node_deleted """
        self.refresh_lights()
        
    # called when Dialog shown (even for the first time)
    def showEvent(self, event):
        self.create_script_jobs()
        self.refresh_lights()

    def closeEvent(self, event):
        """ Called when dialog is closed - hidden """
        self.delete_script_jobs()
        self.clear_lights()


if __name__ == "__main__":

    try:
        light_panel_dialog.close() # pylint: disable=E0601
        light_panel_dialog.deleteLater()
    except:
        pass

    light_panel_dialog = LightPanel()
    light_panel_dialog.show()
