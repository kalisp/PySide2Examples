from PySide2 import QtWidgets, QtGui, QtCore
import maya.cmds as cmds
import pymel.core as pm

''' App that allows select object(s) in the Maya stage, store their start and end values 
    for multiple attributes.
    Allows driving change of state from start to end via slider.
'''

NODE = 'node'
START = 'start'
END = 'end'
CACHE = 'cache'

SLIDER_MIN = 0
SLIDER_MAX = 50

AXIS = ['x', 'y', 'z']

class Interpolator(QtWidgets.QDialog):

    def __init__(self):
        super(Interpolator, self).__init__()
        print("init")
        self.setWindowTitle("Interpolator tool")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.create_ui()
        self.set_connections()

        self.items = {}
        self.enable_buttons(False)


    def create_ui(self):
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        layout_store = QtWidgets.QHBoxLayout()
        self.btn_store_items = QtWidgets.QPushButton("Store Items")
        self.btn_clear_items = QtWidgets.QPushButton("Clear Items")
        layout_store.addWidget(self.btn_store_items)
        layout_store.addWidget(self.btn_clear_items)

        layout_start_end = QtWidgets.QHBoxLayout()
        self.btn_store_start = QtWidgets.QPushButton("Store Start")
        self.btn_store_end = QtWidgets.QPushButton("Store End")
        self.btn_reset = QtWidgets.QPushButton("Reset")
        layout_start_end.addWidget(self.btn_store_start)
        layout_start_end.addWidget(self.btn_store_end)
        layout_start_end.addWidget(self.btn_reset)

        layout_slider = QtWidgets.QHBoxLayout()
        lbl_start = QtWidgets.QLabel("Start")

        self.slider = QtWidgets.QSlider()
        self.slider.setMinimum(SLIDER_MIN)
        self.slider.setMaximum(SLIDER_MAX)
        self.slider.setOrientation(QtCore.Qt.Horizontal)

        lbl_end = QtWidgets.QLabel("End")
        layout_slider.addWidget(lbl_start)
        layout_slider.addWidget(self.slider)
        layout_slider.addWidget(lbl_end)

        layout_transform = QtWidgets.QHBoxLayout()
        self.chk_transform = QtWidgets.QCheckBox()
        self.chk_transform.setMaximumWidth(20)
        self.chk_transform.setChecked(True)

        self.chk_attributes = QtWidgets.QCheckBox()
        self.chk_attributes.setMaximumWidth(20)

        lbl_transform = QtWidgets.QLabel("Transform")
        lbl_transform.setAlignment(QtCore.Qt.AlignLeft)
        lbl_attributes = QtWidgets.QLabel("UD Attributes")
        lbl_attributes.setAlignment(QtCore.Qt.AlignLeft)

        layout_transform.addWidget(self.chk_transform)
        layout_transform.addWidget(lbl_transform)
        layout_transform.addWidget(self.chk_attributes)
        layout_transform.addWidget(lbl_attributes)

        # stylesheet = "color: lightgray; "
        # self.btn_store_items.setStyleSheet(stylesheet)
        # self.btn_clear_items.setStyleSheet(stylesheet)
        # self.btn_reset.setStyleSheet(stylesheet)
        # self.btn_store_start.setStyleSheet(stylesheet)
        # self.btn_store_end.setStyleSheet(stylesheet)

        layout.addLayout(layout_store)
        layout.addLayout(layout_start_end)
        layout.addLayout(layout_slider)
        layout.addLayout(layout_transform)

        self.setLayout(layout)

    def set_connections(self):
        self.btn_store_items.clicked.connect(self.store_items)
        self.btn_clear_items.clicked.connect(self.clear_items)
        self.btn_store_start.clicked.connect(self.store_start)
        self.btn_store_end.clicked.connect(self.store_end)
        self.btn_reset.clicked.connect(self.reset)
        self.slider.valueChanged.connect(self.slider_changed)


    def store_items(self):
        ''' Store base state of selected nodes '''
        selection = pm.ls(sl=True,fl=True)

        if not selection: return

        self.items = {}
        for item in selection:
            self.items[item.name()] = {NODE : item, START:{}, END:{}, CACHE:{}}

        self.enable_buttons(True)

    def clear_items(self):
        ''' Clear saved items and their states '''
        self.items = {}
        self.enable_buttons(False)

    def reset(self):
        ''' Reset saved objects to empty state'''
        for item in self.items():
            self.items[item] = {NODE : item, START:{}, END:{}, CACHE:{}}

        print(self.items)

    def enable_buttons(self, value):
        ''' Enable/disable buttons based on stored items'''
        self.btn_clear_items.setEnabled(value)
        self.btn_reset.setEnabled(value)
        self.btn_store_start.setEnabled(value)
        self.btn_store_end.setEnabled(value)

    def store_start(self):
        print('store_start')
        self._store(START)
        self.slider.setValue(SLIDER_MIN)

    def store_end(self):
        print('store_end')
        self._store(END)
        self.slider.setValue(SLIDER_MAX)

    def _store(self, step):
        if not self.items: return

        for item in self.items.values():
            if self.chk_transform.isChecked():
                translateX, translateY, translateZ = item[NODE].translate.get()
                item[step] = { 'translateX' : translateX, 'translateY' : translateY, 'translateZ' : translateZ}

    def slider_changed(self, value):
        if value == SLIDER_MIN: # start
            self._change_state(START)
        elif value == SLIDER_MAX:
            self._change_state(END)
        else:
            self._change_state_step(value)

    def _change_state_step(self, step):
        print("_change_state_step {}".format(step))
        for item in self.items.values():
            node = item[NODE]
            zipped = zip(item[START].items(), item[END].items())
            for zz in zipped:
                start = zz[0]
                diff = zz[1][1] - zz[0][1] # change of value end - start
                diff = diff / (SLIDER_MAX - SLIDER_MIN) * step
                node.attr(zz[0][0]).set(zz[0][1] + diff)

    def _change_state(self, step):
        for item in self.items.values():
            node = item[NODE]
            for key, value in item[step].items(): # return tuples for 'start', 'end'
                node.attr(key).set(value)

if __name__ == '__main__':
    ui = Interpolator()

    ui.show()