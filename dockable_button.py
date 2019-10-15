from PySide2 import QtWidgets
from shiboken2 import getCppPointer
import maya.cmds as cmds

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from maya.OpenMayaUI import MQtUtil

class MyDockableButton(MayaQWidgetDockableMixin, QtWidgets.QPushButton):
    # workspace_control_name will be populated only after Maya restart to recreate window
    def __init__(self, workspace_control_name = None): 
        super(MyDockableButton, self).__init__()
        
        self.setText("My Button")
        self.setWindowTitle("Dockable Window")
        
        if workspace_control_name:
            workspace_control_ptr = long(MQtUtil.findControl(workspace_control_name)) # get C pointer to control
            widget_ptr = long(getCppPointer(self)[0])
            
            # parenting dockable button to workspace control
            MQtUtil.addWidgetToMayaLayout(widget_ptr, workspace_control_ptr)
            
    def create_connections(self):
        pass
        
    def on_pressed(self):
        print("Pressed")
        
        
if __name__ == '__main__':
    
    try:
        if button and button.parent: # pylint: disable=E0601
            workspace_control_name = button.parent().objectName()
            
            if cmds.window(workspace_control_name, exists=True):
                cmds.deleteUI(workspace_control_name)
    except:
        pass
        
    button = MyDockableButton()
    workspace_control_name = "{}WorkspaceControl".format(button.objectName())
    # gets called after restart
    ui_script = "from dockable_button import MyDockableButton\button = MyDockableButton('{}')".format(workspace_control_name)
    button.show(dockable=True, uiScript=ui_script) # uiScript will be called after restart to recreate window