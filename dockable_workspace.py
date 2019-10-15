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

if __name__ == "__main__":
    
    workspace_control_name = "MyWorkspaceControl"
    if cmds.window(workspace_control_name, exists=True):
        cmds.deleteUI(workspace_control_name)
        
    workspace_control = WorkspaceControl(workspace_control_name)
    workspace_control.create(workspace_control_name, QtWidgets.QPushButton("Push It"))
    workspace_control.set_label("Workspace Control")