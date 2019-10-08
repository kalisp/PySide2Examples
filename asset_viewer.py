import sys
import os as os
from PySide2 import QtCore, QtGui, QtWidgets
import json
import shutil
from datetime import datetime

class AssetViewer(QtWidgets.QWidget):

    IMAGE_WIDTH = 400
    IMAGE_HEIGHT = IMAGE_WIDTH / 1.77778

    ASSET_DIR_PATH = "{}/{}".format(os.getcwd(), 'assets')
    JSON_FILE_NAME = 'assets.json'

    def __init__(self):
        super(AssetViewer, self).__init__(parent=None)

        self.setWindowTitle("AssetViewer")
        self.setMinimumSize(400, 300)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

        self.load_assets_from_json()

        self.refresh_asset_details()

    def create_widgets(self):
        self.asset_list_lbl = QtWidgets.QLabel("Asset Code:")
        self.asset_list_cmb  = QtWidgets.QComboBox()

        self.image_preview_lbl = QtWidgets.QLabel()
        #self.image_preview_lbl.setFixedHeight(self.IMAGE_WIDTH)
        self.image_preview_lbl.setFixedHeight(self.IMAGE_HEIGHT)

        print("width {}".format(self.image_preview_lbl.width()))

        self.name_le = QtWidgets.QLineEdit()
        self.description_ple = QtWidgets.QPlainTextEdit()
        self.creator_le = QtWidgets.QLineEdit()
        self.creator_le.setReadOnly(True)
        self.created_le = QtWidgets.QLineEdit()
        self.created_le.setReadOnly(True)
        self.modified_le = QtWidgets.QLineEdit()
        self.modified_le.setReadOnly(True)

        self.save_btn = QtWidgets.QPushButton("Save")
        self.cancel_btn = QtWidgets.QPushButton("Cancel")

    def create_layout(self):
        asset_list_layout = QtWidgets.QHBoxLayout()
        asset_list_layout.addStretch()
        asset_list_layout.addWidget(self.asset_list_lbl)
        asset_list_layout.addWidget(self.asset_list_cmb)

        asset_description_layout = QtWidgets.QFormLayout()
        asset_description_layout.addRow("Name", self.name_le)
        asset_description_layout.addRow("Description", self.description_ple)
        asset_description_layout.addRow("Creator", self.creator_le)
        asset_description_layout.addRow("Created", self.created_le)
        asset_description_layout.addRow("Modified", self.modified_le)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(3,3,3,3)
        main_layout.addLayout(asset_list_layout)
        main_layout.addWidget(self.image_preview_lbl)
        main_layout.addLayout(asset_description_layout)
        main_layout.addLayout(button_layout)

    def create_connections(self):
        self.asset_list_cmb.currentIndexChanged.connect(self.refresh_asset_details)

        self.save_btn.clicked.connect(self.save_assets_to_json)

    def refresh_asset_details(self):
        """ Updates asset information
            Sets image preview
        """
        asset_details = self.content[self.asset_list_cmb.currentText()]
        self.load_image_preview(asset_details["image_path"])

        self.name_le.setText(asset_details["name"])
        self.description_ple.setPlainText(asset_details["description"])
        self.creator_le.setText(asset_details["creator"])
        self.created_le.setText(asset_details["created"])
        self.modified_le.setText(asset_details["modified"])

    def load_assets_from_json(self):
        """ Parse json file to produce codes in asset_list_cmb """
        url = "{}/{}".format(self.ASSET_DIR_PATH, self.JSON_FILE_NAME)

        with open(url, 'r') as asset_file:
            self.content = json.load(asset_file)

            for asset in self.content.keys():
                self.asset_list_cmb.addItem(asset)

    def load_image_preview(self, file_name):
        """ loads PixMap of file_name to QLabel """
        img_url = "{}/{}".format(self.ASSET_DIR_PATH, file_name)
        print("img_url {}".format(img_url))
        file_info = QtCore.QFileInfo(img_url)
        if file_info:
            image = QtGui.QImage(img_url)
            print("width load_image_preview {}".format(self.image_preview_lbl.width()))
            image.scaled(self.image_preview_lbl.width(), self.image_preview_lbl.height(), QtCore.Qt.KeepAspectRatio,
                         QtCore.Qt.SmoothTransformation)

            pixmap = QtGui.QPixmap(image)
        else:
            pixmap = QtGui.QPixmap(self.preview_image_label.size())
            pixmap.fill(QtCore.Qt.transparent)

        self.image_preview_lbl.setPixmap(pixmap)

    def save_assets_to_json(self):
        """
            Stores updated value from form to json file
            Called via "Save" button
        """
        asset_code = self.asset_list_cmb.currentText()
        self.content[asset_code]["name"] = self.name_le.text()
        self.content[asset_code]["description"] = self.description_ple.toPlainText()
        self.content[asset_code]["creator"] = self.creator_le.text()
        self.content[asset_code]["created"] = self.created_le.text()
        self.content[asset_code]["modified"] = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")

        url = "{}/{}".format(self.ASSET_DIR_PATH, self.JSON_FILE_NAME)
        shutil.copyfile(url, url+'.tmp')
        try:
            with open(url, 'w') as asset_file:
                json.dump(self.content, asset_file)
        except:
            shutil.copyfile(url + '.tmp', url)
        finally:
            os.remove(url + '.tmp')

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = AssetViewer()
    window.show()

    app.exec_()