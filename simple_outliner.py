from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

from functools import partial

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
        
        self.script_job_number = -1  # no script job exists yet
        
        self.transform_icon = QtGui.QIcon(":transform.svg")
        self.camera_icon = QtGui.QIcon(":Camera.png")
        self.mesh_icon = QtGui.QIcon(":mesh.svg")
        
        
        
        self.create_actions() # to add items to menu_bar

        self.create_widgets()
        self.create_layout()
        self.create_connections()
        
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu) # RMB for context menu
        self.customContextMenuRequested.connect(self.show_context_menu)

        self.refresh_tree_widget()
        
    def create_actions(self):
        self.about_action = QtWidgets.QAction("About", self)
        
        self.display_shape_action = QtWidgets.QAction("Shapes", self )
        self.display_shape_action.setCheckable(True) # set as checkbox
        self.display_shape_action.setChecked(True) # show shapes by default
        self.display_shape_action.setShortcut(QtGui.QKeySequence("Ctrl+Shift+H"))
        

    def create_widgets(self):
        self.menu_bar = QtWidgets.QMenuBar() #menu at top of widget
        display_menu = self.menu_bar.addMenu("Display")
        display_menu.addAction(self.display_shape_action)
        
        help_menu = self.menu_bar.addMenu("Help")
        help_menu.addAction(self.about_action)
 
        
        self.tree_widget = QtWidgets.QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection) # for CTRL selection
        # header = self.tree_widget.headerItem()
        # header.setText(0, "")
        
        self.refresh_btn = QtWidgets.QPushButton("Refresh")

    def create_layout(self):
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.refresh_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)
        main_layout.setMenuBar(self.menu_bar)
        main_layout.addWidget(self.tree_widget)
        main_layout.addLayout(button_layout)

    def create_connections(self):
        self.refresh_btn.clicked.connect(self.refresh_tree_widget)
        self.tree_widget.itemCollapsed.connect(self.update_icon)
        self.tree_widget.itemExpanded.connect(self.update_icon)
        self.tree_widget.itemSelectionChanged.connect(self.select_items) # select items in Maya views
         
        self.about_action.triggered.connect(self.about)
        self.display_shape_action.toggled.connect(self.set_shape_nodes_visible) #toggled has 1 bool argument, which gets passed as 'visible' value
    
    def refresh_tree_widget(self):
        self.shape_nodes = cmds.ls(shapes = True) # list all shapes only
        self.tree_widget.clear()
        
        top_level_object_names = cmds.ls(assemblies = True) # list all objects in scene (cameras, meshes/shapes)
        print(top_level_object_names)
        for name in top_level_object_names:
            item = self.create_item(name)
            self.tree_widget.addTopLevelItem(item)
            
        self.update_selection()

    # iterates depth first (via add_children method)
    def create_item(self, name):    
        item = QtWidgets.QTreeWidgetItem([name])
        self.add_children(item)
        self.update_icon(item)
        
        is_shape = name in self.shape_nodes
        item.setData(0, QtCore.Qt.UserRole, is_shape) # mark which line items are 'shapes' - to show/hide them
        
        return item
        
    def add_children(self, item):
        children = cmds.listRelatives(item.text(0), children=True)
        if children: # None returned if no children
            for child in children:
                child_item = self.create_item(child)
                item.addChild(child_item)
                
    # called any time item is clicked in the widget
    def update_icon(self, item):
        object_type = ""
        
        if item.isExpanded():
            object_type = "transform"
        else:
            child_count = item.childCount()
            if child_count == 0:
                object_type = cmds.objectType(item.text(0))
            elif child_count == 1:
                child_item = item.child(0)
                object_type = cmds.objectType(child_item.text(0))
            else:
                object_type = "transform"
                
            if object_type == "transform":
                item.setIcon(0, self.transform_icon)
            elif object_type == "camera":
                item.setIcon(0, self.camera_icon)
            elif object_type == "mesh":
                item.setIcon(0, self.mesh_icon)
            
    def select_items(self):
        items = self.tree_widget.selectedItems()
        
        names = [item.text(0) for item in items]
        
        cmds.select(names, replace=True)
        
    def about(self):
        QtWidgets.QMessageBox.about(self, "About Simple Outliner", "Add about text here")
        
    # show/hide 'shape' objects in the widget
    def set_shape_nodes_visible(self, visible):
        iterator = QtWidgets.QTreeWidgetItemIterator(self.tree_widget)
        
        while iterator.value():
            item = iterator.value()
            is_shape = item.data(0, QtCore.Qt.UserRole)
            if is_shape:
                item.setHidden(not visible)
                
            iterator += 1 # needs to be here, iterator doesnt increment automatically
            
    def show_context_menu(self, point):
        context_menu = QtWidgets.QMenu()
        context_menu.addAction(self.display_shape_action) #show/hide shapes
        context_menu.addSeparator()
        context_menu.addAction(self.about_action)
        
        context_menu.exec_(self.mapToGlobal(point)) # point needs to be converted to global position
        
    # update selected objects in Outliner
    def update_selection(self):
        selection = cmds.ls(selection=True)
        
        iterator = QtWidgets.QTreeWidgetItemIterator(self.tree_widget)
        
        while iterator.value():
            item = iterator.value()
            is_selected = item.text(0) in selection
            item.setSelected(is_selected)
            
            iterator += 1
            
    # to synchronize selection of meshes from camera to SimpleOutliner selection
    def set_script_job_enabled(self, enabled):
        if enabled and self.script_job_number < 0: # no script job is already created
            self.script_job_number = cmds.scriptJob(event = ["SelectionChanged", partial(self.update_selection)], protected = True)
        elif not enabled and self.script_job_number >= 0: # is there script job to disable (delete)
            cmds.scriptJob(kill=self.script_job_number, force=True) # force because 'protected'
            self.script_job_number = -1

    def showEvent(self, e):
        super(SimpleOutliner, self).showEvent(e)
        self.set_script_job_enabled(True)
        
    def closeEvent(self, e):
        if isinstance(self, SimpleOutliner):
            super(SimpleOutliner, self).closeEvent(e)
            self.set_script_job_enabled(False)
        
        
if __name__ == "__main__":

    try:
        SimpleOutliner.set_script_job_enabled(False)
        simple_outliner.close() # pylint: disable=E0601
        simple_outliner.deleteLater()
    except:
        pass

    simple_outliner = SimpleOutliner()
    simple_outliner.show()
