from PySide2 import QtCore
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


class TableExampleDialog(QtWidgets.QDialog):
    # to set data to store, UserRole (value 32) is standard for developer usage
    # there are different roles, but you dont want to overwrite them as values there could be important
    ATTR_ROLE = QtCore.Qt.UserRole 
    VALUE_ROLE = QtCore.Qt.UserRole + 1

    def __init__(self, parent=maya_main_window()):
        super(TableExampleDialog, self).__init__(parent)

        self.setWindowTitle("Table Example")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(500)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        """
        Creates all widgets
        Returns: None

        """
        self.table_wdg = QtWidgets.QTableWidget()
        self.table_wdg.setColumnCount(5)
        self.table_wdg.setColumnWidth(0, 22)
        self.table_wdg.setColumnWidth(2, 70)
        self.table_wdg.setColumnWidth(3, 70)
        self.table_wdg.setColumnWidth(4, 70)
        
        self.table_wdg.setHorizontalHeaderLabels(["", "Name", "TransX", "TransY", "TransZ"])
        header_view = self.table_wdg.horizontalHeader()
        header_view.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)

        
        self.refresh_btn = QtWidgets.QPushButton("Refresh")
        self.close_btn = QtWidgets.QPushButton("Close")

    def create_layout(self):
        """
        All layout stuff
        Returns: None

        """
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setSpacing(2)
        button_layout.addStretch()
        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.close_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)
        
        main_layout.addWidget(self.table_wdg)
        
        main_layout.addStretch()
        main_layout.addLayout(button_layout)

    def create_connections(self):
        """
        All connection from widgets to callbacks
        Returns: None

        """
        self.set_cell_changed_connection_enabled(True)
        #self.table_wdg.cellChanged.connect(self.on_cell_changed) #produces 1 event for each cell!!!
        self.refresh_btn.clicked.connect(self.refresh_table)
        self.close_btn.clicked.connect(self.close)

    def set_cell_changed_connection_enabled(self, enabled):
        """
        Without this function events would be trigered for every cell
        Args:
            enabled: boolean

        Returns: None

        """
        if enabled:
            self.table_wdg.cellChanged.connect(self.on_cell_changed)
        else:
            self.table_wdg.cellChanged.disconnect(self.on_cell_changed)
    
    #override existing method to call refresh_table automaticaly at each start of dialog    
    def showEvent(self, e):
        super(TableExampleDialog, self).showEvent(e)
        self.refresh_table()

    #override
    def keyPressEvent(self, e):
        super(TableExampleDialog, self).keyPressEvent(e) #do key press event for dialog
        e.accept() # consume key press event, do not push to parent, eg. mainwindow

    def refresh_table(self):
        """
        Recalculates content of the table
        Returns: None

        """
        self.set_cell_changed_connection_enabled(False) #limits triggering separete events for change per each cell
        self.table_wdg.setRowCount(0) #purge table
        
        meshes = cmds.ls(type="mesh")
        for i in range(len(meshes)):
            transform_name = cmds.listRelatives(meshes[i], parent=True)[0] #mesh name
            translation = cmds.getAttr("{}.translate".format(transform_name))[0]
            visible = cmds.getAttr("{}.visibility".format(transform_name))         
            
            self.table_wdg.insertRow(i)
            self.insert_item(i, 0, "", "visibility", visible, True)
            self.insert_item(i, 1, transform_name, None, transform_name, False)
            self.insert_item(i, 2, self.float_to_string(translation[0]), "tx", translation[0], False) # value for x
            self.insert_item(i, 3, self.float_to_string(translation[1]), "ty", translation[1], False) # value for y
            self.insert_item(i, 4, self.float_to_string(translation[2]), "tz", translation[2], False) # value for z  
            
        self.set_cell_changed_connection_enabled(True)  # enable regular event spawning                 
            
    def insert_item(self, row, column, text, attr, value, is_boolean):
        """
        Insert new item to the table
        Args:
            row: index of row (int)
            column: index of columnt (int)
            text: content of cell (string)
            attr: name of attribute (string)
            value: value of attribute (string
            is_boolean: is attribute boolean

        Returns: None

        """
        item = QtWidgets.QTableWidgetItem(text)
        self.set_item_attr(item, attr)
        self.set_item_value(item, value)
        if is_boolean:
            item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            self.set_item_checked(item, value)
        
        self.table_wdg.setItem(row, column, item)
     
    def on_cell_changed(self, row, column):
        """
        Called when value is changed in the table
        Args:
            row: index of row (int)
            column: index of column (int)

        Returns: None

        """
        self.set_cell_changed_connection_enabled(False) # see refresh table
        
        item = self.table_wdg.item(row, column)
        if column == 1:
            self.rename(item)
        else:
            is_boolean = column == 0
            self.update_attr(self.get_full_attr_name(row, item), item, is_boolean )
        
        self.set_cell_changed_connection_enabled(True)

    def rename(self, item):
        """
        Update value in column 1, eg. name
        Args:
            item: (Item)

        Returns: None

        """
        old_name = self.get_item_value(item)
        new_name = self.get_item_text(item)
        
        if old_name != new_name:
            actual_new_name = cmds.rename(old_name, new_name) # tell Maya to rename mesh
            if actual_new_name != new_name: # Maya follows special naming convention 'My Name' >> 'My_Name'
                self.set_item_text(item, actual_new_name)
                
            self.set_item_value(item, actual_new_name)

    def update_attr(self, attr_name, item, is_boolean):
        """
        update value in a cell via cmds
        Args:
            attr_name: attribute name (string)
            item: whole item (Item)
            is_boolean: is attribute boolean

        Returns: None

        """
        if is_boolean:
            value = self.is_item_checked(item)
            self.set_item_text(item, "")
        else:
            text = self.get_item_text(item)
            try:
                value = float(text)
            except ValueError as e: # cast error
                print("exception {}".format(e))
                self.revert_original_value(item, is_boolean)
                return
                
        try:
            cmds.setAttr(attr_name, value)
        except Exception as e: # attribute update error
            self.revert_original_value(item, is_boolean)
            return
            
        new_value = cmds.getAttr(attr_name)
        if is_boolean:
            self.set_item_checked(item, new_value)
        else:
            self.set_item_text(item, self.float_to_string(new_value))
            
        self.set_item_value(item, new_value)
        
    # helper methods to make item creation easier    
    def set_item_text(self, item, text):
        item.setText(text)
        
    def get_item_text(self, item):
        return item.text()
        
    def set_item_checked(self, item, checked):
        if checked:
            item.setCheckState(QtCore.Qt.Checked)
        else:
            item.setCheckState(QtCore.Qt.Unchecked)
            
    def is_item_checked(self, item):
        return item.checkState() == QtCore.Qt.Checked
        
    #set attribute name
    def set_item_attr(self, item, attr):
        item.setData(self.ATTR_ROLE, attr)
        
    # get name of attribute
    def get_item_attr(self, item):
        return item.data(self.ATTR_ROLE)
                
    # set value - see different stores ATTR_ROLE vs VALUE_ROLE
    # there could be only 1 value (could be array) stored there
    def set_item_value(self, item, value):
        item.setData(self.VALUE_ROLE, value)
        
    def get_item_value(self, item):
        return item.data(self.VALUE_ROLE)
        
    # nicer formation of translations
    def float_to_string(self, value):
        return "{0:.4f}".format(value)

    # used in case of exception, cast of wrong value etc
    def revert_original_value(self, item, is_boolean):
        original_value = self.get_item_value(item)
        if is_boolean:
            self.set_item_checked(item, original_value)
        else:
            self.float_to_string(original_value)
     
    # get Maya object name to use cmds. properly        
    def get_full_attr_name(self, row, item):
        node_name = self.table_wdg.item(row, 1).data(self.VALUE_ROLE)
        attr_name = self.get_item_attr(item)
        return "{}.{}".format(node_name, attr_name)


if __name__ == "__main__":

    try:
        table_example_dialog.close() # pylint: disable=E0601
        table_example_dialog.deleteLater()
    except:
        pass

    table_example_dialog = TableExampleDialog()
    table_example_dialog.show()
