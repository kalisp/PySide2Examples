from PySide2 import QtCore, QtWidgets

from shiboken2 import getCppPointer

import maya.OpenMayaUI as omui
import maya.cmds as cmds

class WorkspaceControl(object):
    def __init__(self, name):
        self.name = name
        self.widget = None
        
        
    def create(self, label, widget, ui_script=None):
        """ Creates workspace control with specific name """
        cmds.workspaceControl(self.name, label=label)
        
        if ui_script: # delay running ui_script, if it would be during creation, it would run immediately
            cmds.workspaceControl(self.name, e=True, uiScript=ui_script )
            
        self.add_widget_to_layout(widget)
        self.set_visible(True)
        
    def restore(self, widget):
        """ Called when Maya is starting, workspace is restoring UI """
        self.add_widget_to_layout(widget)
        
        
    def add_widget_to_layout(self, widget):
        """ Adds widget as a child to workspace control """
        if widget:
            self.widget = widget # save for future handling
            # do not set children as native, should speed up redraw, remove blittering 
            self.widget.setAttribute(QtCore.Qt.WA_DontCreateNativeAncestors)
            
            workspace_control_ptr = long(omui.MQtUtil.findControl(self.name))# get cpp pointer for a workspace
            widget_ptr = long(getCppPointer(self.widget)[0])
            
            omui.MQtUtil.addWidgetToMayaLayout(widget_ptr, workspace_control_ptr)
        
    def exists(self):
        """ Helper method, checks if self.name in workspace """
        return cmds.workspaceControl(self.name, q=True, exists=True)
        
    def is_visible(self):
        """ Helper method, checks if self.name in visible workspace """
        return cmds.workspaceControl(self.name, q=True, visible=True)
        
    def set_visible(self, visible):
        """ Helper method,set visibility """
        if visible:
            cmds.workspaceControl(self.name, e=True, restore=True)
        else:
            cmds.workspaceControl(self.name, e=True, visible=True)
            
    def set_label(self, label):
        """ Helper method, sets label to the window """
        cmds.workspaceControl(self.name, e=True, label=label)

    def is_floating(self):
        """ Helper method, checks if self.name in floating """
        cmds.workspaceControl(self.name, q=True, visible=True)
        
    def is_collapsed(self):
        """ Helper method, checks if self.name window is collapsed """
        cmds.workspaceControl(self.name, q=True, collapse=True)
        
class SampleUI(QtWidgets.QWidget):
    """ Sample UI with QPushButton, parented by WorkspaceControl to be dockable """
    
    WINDOW_TITLE = "Sample UI"
    UI_NAME = "SampleUI"
    
    ui_instance = None
    
    def __init__(self):
        super(SampleUI, self).__init__()
        
        self.setObjectName(self.__class__.UI_NAME)
        self.setMinimumSize(100, 100)
        
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.create_workspace_control()
    
    @classmethod
    def get_workspace_control_name(cls):
        return "{}WorkspaceControl".format(cls.UI_NAME)
        
    @classmethod
    def display(cls):
        """ Should be used in ui_script to restore after restart or in shelf button """
        if cls.ui_instance:
            cls.ui_instance.show_workspace_control()
        else:
            cls.ui_instance = SampleUI()
        
    def create_widgets(self):
        self.apply_button = QtWidgets.QPushButton("Push It")
        
    def create_layout(self):
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setMargin(2)
        main_layout.addStretch()
        main_layout.addWidget(self.apply_button)
        
    def create_connections(self):
        self.apply_button.clicked.connect(self.on_clicked)
        
    def create_workspace_control(self):
        """ Create workspace control to parent itself """
        self.workspace_control_instance = WorkspaceControl(self.get_workspace_control_name())
        
        if self.workspace_control_instance.exists():
            self.workspace_control_instance.restore(self) # parent SimpleUI to existing workspace control
        else:        
            script = "from workspace_control import SampleUI\nSampleUI.display()"
            self.workspace_control_instance.create(self.WINDOW_TITLE, self, ui_script=script) # actually creates workspace control widget
        
    def show_workspace_control(self):
        self.workspace_control_instance.set_visible(True)
        
    def on_clicked(self):
        print("Pushed")

if __name__ == "__main__":
    
    workspace_control_name = SampleUI.get_workspace_control_name()
    if cmds.window(workspace_control_name, exists=True):
        cmds.deleteUI(workspace_control_name)
        
    sample_ui = SampleUI()