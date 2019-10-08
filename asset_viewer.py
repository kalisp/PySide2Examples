import sys
from PySide2 import QtCore, QtGui, QtWidgets

class AssetViewer(QtWidgets.QWidget):

    IMAGE_WIDTH = 400
    IMAGE_HEIGHT = IMAGE_WIDTH / 1.77778

    def __init__(self):
        super(AssetViewer, self).__init__(parent=None)

        self.setWindowTitle("AssetViewer")
        self.setMinimumSize(400, 300)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.asset_list_lbl = QtWidgets.QLabel("Asset Code:")
        self.asset_list_cmb  = QtWidgets.QComboBox()

        self.image_preview_lbl = QtWidgets.QLabel()
        self.image_preview_lbl.setMinimumWidth(self.IMAGE_WIDTH)




    def create_layout(self):
        asset_list_layout = QtWidgets.QHBoxLayout()
        asset_list_layout.addStretch()
        asset_list_layout.addWidget(self.asset_list_lbl)
        asset_list_layout.addWidget(self.asset_list_cmb)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(asset_list_layout)

    def create_connections(self):
        pass


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = AssetViewer()
    window.show()

    app.exec_()