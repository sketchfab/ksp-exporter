from PyQt4 import QtGui, QtCore
from kspmanager import KSP2Skfb, SKETCHFAB_MODEL_URL
import os
import json


class Window(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle('Ksp2Sketchfab')
        self.settings = QtCore.QSettings("Sketchfab", "Ksp2Sketchfab")
        self.game_dir = 'C:\\Kerbal Space Program'
        self.craft_list = []
        self.manager = None

        main_layout = QtGui.QVBoxLayout()
        title_label = QtGui.QLabel('Publish your craft to Sketchfab')
        self.game_path_info_label = QtGui.QLabel('pending')

        game_path_label = QtGui.QLabel('Game Directory :')
        game_path_tb = QtGui.QLineEdit()

        main_layout.addWidget(title_label)
        main_layout.addWidget(game_path_label)
        main_layout.addWidget(game_path_tb)
        main_layout.addWidget(self.game_path_info_label)

        craft_list_label = QtGui.QLabel('Select the craft to upload')
        self.craft_list_ql = QtGui.QListWidget()

        if os.path.exists(self.game_dir):
            self.manager = KSP2Skfb(self.game_dir)
            self.game_path_info_label.setText('Found')
            self.craft_list = self.manager.get_craft_list()
            self.craft_list_ql.addItems(self.craft_list)
        else:
            self.game_path_info_label.setText('Warning : game directory not found')

        self.game_dir_btn = QtGui.QPushButton("Browse game directory", self)
        self.game_dir_btn.clicked.connect(self.search_game_directory)
        main_layout.addWidget(self.game_dir_btn)

        game_path_tb.setText(self.game_dir)
        api_token_label = QtGui.QLabel('API token*:')
        self.api_token_tb = QtGui.QLineEdit()
        api_token_info_label = QtGui.QLabel("(You can find your API token \
            <a href=\"https://sketchfab.com/settings/password\">here</a> when logged)")
        api_token_info_label.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        api_token_info_label.setOpenExternalLinks(True)

        title_label = QtGui.QLabel('Title:')
        self.title_tb = QtGui.QLineEdit()
        title_info_label = QtGui.QLabel('Enter a title for your Sketchfab model')

        description_label = QtGui.QLabel('Description:')
        self.description_tb = QtGui.QTextEdit()
        description_info_label = QtGui.QLabel('Some words about your craft ?')

        tags_label = QtGui.QLabel('Tags:')
        self.tags_tb = QtGui.QLineEdit()
        tags_info_label = QtGui.QLabel('<KSP> tag is automatically added')

        self.upload_btn = QtGui.QPushButton("Upload", self)
        self.upload_btn.clicked.connect(self.start_upload)
        self.status_info_label = QtGui.QLabel('')

        self.close_btn = QtGui.QPushButton("Close", self)
        self.close_btn.clicked.connect(self.close)

        main_layout.addWidget(api_token_label)
        main_layout.addWidget(self.api_token_tb)
        main_layout.addWidget(api_token_info_label)

        main_layout.addWidget(title_label)
        main_layout.addWidget(self.title_tb)
        main_layout.addWidget(title_info_label)

        main_layout.addWidget(description_label)
        main_layout.addWidget(self.description_tb)
        main_layout.addWidget(description_info_label)

        main_layout.addWidget(tags_label)
        main_layout.addWidget(self.tags_tb)
        main_layout.addWidget(tags_info_label)

        main_layout.addWidget(craft_list_label)
        main_layout.addWidget(self.craft_list_ql)

        main_layout.addWidget(self.status_info_label)
        self.update_game_gui(self.game_dir)
        self.craft_list_ql.currentRowChanged.connect(self.updateList)
        main_layout.addWidget(self.upload_btn)
        main_layout.addWidget(self.close_btn)
        self.setLayout(main_layout)

    def updateList(self, index):
        self.upload_btn.setEnabled(True)
        self.upload_btn.setText('Upload {}'.format(self.craft_list[index].split('.')[1].strip()))
        self.status_info_label.setText('')

    def update_window_data(self):
        if os.path.exists(self.game_dir):
            self.manager = KSP2Skfb(self.game_dir)
            self.craft_list = self.manager.get_craft_list()

    def update_status(self, status):
        self.upload_status = status
        print(self.upload_status)
        if self.upload_status.startswith('http'):
            self.status_info_label.setText('<a href=\"{}\">See your model here</a>'.format(self.upload_status))
            self.status_info_label.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
            self.status_info_label.setOpenExternalLinks(True)
        else:
            self.status_info_label.setText('Error : {}'.format(self.upload_status))
        self.upload_btn.setEnabled(False)

    def start_upload(self):
        self.upload_status = 'Uploading ...'
        self.status_info_label.setText('Uploading...')
        self.upload_btn.setEnabled(False)

        to_utf8 = lambda qstring: unicode(qstring.toUtf8(), encoding='utf8').encode('utf8')

        progress = QtGui.QProgressDialog("Uploading...", "Cancel", 0, 100, self)
        progress.setWindowTitle("Sketchfab upload")
        progress.setWindowModality(QtCore.Qt.WindowModal)
        progress.show()

        self.uploader, self.reply = self.manager.upload(
            self.craft_list_ql.currentRow(),
            title=to_utf8(self.title_tb.text()),
            description=to_utf8(self.description_tb.toPlainText()),
            tags=to_utf8(self.tags_tb.text()),
            token=to_utf8(self.api_token_tb.text()))

        def upload_finished():
            if not progress.wasCanceled():
                http_response = self.reply.readAll()
                print(http_response)
                data = json.loads(str(http_response))
                if 'uid' in data:
                    url = SKETCHFAB_MODEL_URL + '/' + data['uid']
                    self.update_status(url)
                    QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))
                else:
                    self.update_status(data['detail'])

                progress.close()

        def upload_error():
            progress.cancel()
            rawData = str(self.reply.readAll())
            data = json.loads(rawData)
            print(rawData)
            QtGui.QMessageBox.critical(self, "Upload error", data["detail"])
            self.update_status(data['detail'])
            progress.close()
            self.reply = None

        def upload_progress(value, max):
            progress.setValue(value)
            progress.setMaximum(max + 1)
            if value == max:
                progress.setLabelText('Processing...')

        def upload_canceled():
            self.reply = None
            self.status_info_label.setText('Cancelled')

        def ssl_errors(err_list):
            for err in err_list:
                print(err.errorString())
            self.reply.ignoreSslErrors()

        self.reply.finished.connect(upload_finished)
        self.reply.error.connect(upload_error)
        self.reply.uploadProgress.connect(upload_progress)
        self.reply.sslErrors.connect(ssl_errors)

    def search_game_directory(self):
        dialog = QtGui.QFileDialog()
        dialog.setFileMode(QtGui.QFileDialog.Directory)
        dialog.setOption(QtGui.QFileDialog.ShowDirsOnly)
        self.update_game_gui(dialog.getExistingDirectory())

    def update_game_gui(self, game_dir):
        if os.path.exists(game_dir):
            self.game_dir = game_dir
            self.game_path_tb = self.game_dir
            self.game_path_info_label.setText('Found')
            print(self.game_dir)
            self.manager = KSP2Skfb(str(self.game_dir))
            self.craft_list = []
            self.craft_list_ql.clear()
            self.craft_list = self.manager.get_craft_list()
            self.craft_list_ql.addItems(self.craft_list)

        if self.craft_list:
            self.craft_list_ql.setEnabled(True)
            self.upload_btn.setEnabled(True)
            self.game_dir_btn.setEnabled(False)
        else:
            self.craft_list_ql.setEnabled(False)
            self.upload_btn.setEnabled(False)
