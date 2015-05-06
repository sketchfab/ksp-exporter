from PyQt4 import QtGui, QtCore
from kspmanager import KSP2Skfb, SKETCHFAB_MODEL_URL
import os
import json
import sys


class Window(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle('Ksp2Sketchfab')
        self.settings = QtCore.QSettings("Sketchfab", "Ksp2Sketchfab")
        self.game_dir = 'C:\\Kerbal Space Program'
        self.craft_list = []
        self.manager = None

        self.user_data = dict()
        self.get_user_data()
        if 'path' in self.user_data:
            self.game_dir = self.user_data['path']

        # Setting the layouts
        self.main_layout = QtGui.QVBoxLayout()
        h_layout = QtGui.QHBoxLayout()

        name_label = QtGui.QLabel('Publish your craft to Sketchfab')

        # KSP gui
        game_path_label = QtGui.QLabel('Game Directory')
        self.game_path_tb = QtGui.QLineEdit()
        self.game_path_tb.setText(self.game_dir)
        self.game_dir_btn = QtGui.QPushButton("Browse", self)
        self.game_dir_btn.clicked.connect(self.search_game_directory)
        self.game_dir_btn.setEnabled(True)
        self.game_path_info_label = QtGui.QLabel('0 crafts found, please set the correct game directory')

        craft_list_label = QtGui.QLabel('Select the craft to upload')
        self.craft_list_ql = QtGui.QListWidget()

        # SKFB UI
        ## API Token
        api_token_label = QtGui.QLabel('Sketchfab API token*:')
        api_token_label.setStyleSheet("color: black; font-weight : bold;")
        self.api_token_tb = QtGui.QLineEdit()
        self.api_token_tb.setMaxLength(32)
        if 'api' in self.user_data:
            self.api_token_tb.setText(self.user_data['api'])
        else:
            self.api_token_tb.setPlaceholderText('Set your Sketchfab api Token (required)')

        api_token_info_label = QtGui.QLabel("(You can find your API token in your \
            <a href=\"https://sketchfab.com/settings/password\">password settings</a>)")
        api_token_info_label.setStyleSheet("color: rgb(150, 150, 150); font-style : italic;")
        api_token_info_label.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        api_token_info_label.setOpenExternalLinks(True)

        ## Model name
        name_label = QtGui.QLabel('Model Name')
        self.name_tb = QtGui.QLineEdit()
        self.name_tb.setMaxLength(48)
        self.name_tb.setPlaceholderText('Enter model name [up to 48 characters]')

        ## Description
        self.description_label = QtGui.QLabel('Description (0/1024 characters)')
        self.description_tb = QtGui.QTextEdit()
        self.description_tb.textChanged.connect(self.description_input_limit)

        ## Tags
        tags_label = QtGui.QLabel('Tags (separated by spaces)')
        self.tags_tb = QtGui.QLineEdit()
        self.tags_tb.setPlaceholderText('KerbalSpaceProgram Rocket Craft')
        ksp_tag_label = QtGui.QLabel('KSP')

        ## Upload btn
        self.upload_btn = QtGui.QPushButton("Publish to Sketchfab", self)
        self.upload_btn.setStyleSheet("background-color: rgb(28, 170, 217); color: white;")
        self.upload_btn.clicked.connect(self.start_upload)
        self.upload_btn.setEnabled(False)
        self.status_info_label = QtGui.QLabel('')

        # Set layouts
        self.main_layout.addWidget(game_path_label)
        h_layout.addWidget(self.game_path_tb)
        h_layout.addWidget(self.game_dir_btn)
        self.main_layout.addLayout(h_layout)
        self.main_layout.addWidget(self.game_path_info_label)

        self.main_layout.addWidget(craft_list_label)
        self.main_layout.addWidget(self.craft_list_ql)

        self.main_layout.addWidget(api_token_label)
        self.main_layout.addWidget(self.api_token_tb)
        self.main_layout.addWidget(api_token_info_label)

        self.main_layout.addWidget(name_label)
        self.main_layout.addWidget(self.name_tb)

        self.main_layout.addWidget(self.description_label)
        self.main_layout.addWidget(self.description_tb)

        self.main_layout.addWidget(tags_label)
        tag_h_layout = QtGui.QHBoxLayout()
        tag_h_layout.addWidget(ksp_tag_label)
        tag_h_layout.addWidget(self.tags_tb)
        self.main_layout.addLayout(tag_h_layout)

        self.craft_list_ql.currentRowChanged.connect(self.updateList)
        self.main_layout.addWidget(self.upload_btn)
        self.main_layout.addWidget(self.status_info_label)
        self.setLayout(self.main_layout)

        # Build manager and set ui
        self.manager = KSP2Skfb(self.game_dir, True)
        self.update_game_ui(self.game_dir)
        self.enable_skfb_ui(False)
        QtCore.QObject.connect(self.manager.emitter, QtCore.SIGNAL('building(QString, int, int)'), self.update_upload_btn)
        QtCore.QObject.connect(self.manager.emitter, QtCore.SIGNAL('converting(QString)'), self.update_upload_lb)

        # If bad path at launch, pop up the filedialog to locate it
        if not os.path.exists(self.game_dir):
            QtGui.QMessageBox.information(self, "Game directory not found", "Please set your game directory")
            self.search_game_directory()

    def get_user_data(self):
        if os.path.exists('userdata.json'):
            with open('userdata.json', 'r') as f:
                try:
                    self.user_data = json.load(f)
                    print(self.user_data)
                except:
                    os.remove('userdata.json')

    def dump_user_data(self):
        with open('userdata.json', 'w') as f:
            json.dump(self.user_data, f)

    def update_upload_lb(self, text):
        self.status_info_label.setText(text)

    def update_upload_btn(self, text, val, total):
        if total > 0:
            percent = int(float(val)/total*100)
            self.upload_btn.setText("{} {}%".format(text, percent))
        else:
            self.upload_btn.setText("{}".format(text))

        self.repaint()

    def set_upload_btn_state(self, state=None):
        ''' Update the upload btn status '''
        if state == 'upload':
            self.upload_btn.setText('Uploading...')
            self.upload_btn.setStyleSheet("background-color: rgb(28, 170, 217); color: white;")
        elif state == 'building':
            self.upload_btn.setEnabled(True)
            self.upload_btn.setText('Building zip archive...')
            self.upload_btn.setStyleSheet("background-color: rgb(170, 170, 170); color: white;")
        elif state =='publish':
            self.upload_btn.setEnabled(True)
            self.upload_btn.setText('Publish to Sketchfab')
            self.upload_btn.setStyleSheet("background-color: rgb(28, 170, 217); color: white;")

        self.repaint()

    def description_input_limit(self):
        if len(self.description_tb.toPlainText()) > 1024:
            self.description_tb.setText(self.description_tb.toPlainText())
        self.description_label.setText('Description ({}/1024 characters)'.format(len(self.description_tb.toPlainText())))

    def strip_craft_name(self, index):
        return self.craft_list[index].split('.')[1].strip()

    def updateList(self, index):
        ''' Update Gui when list element is changed'''
        self.upload_btn.setEnabled(True)
        self.upload_btn.setText('Publish to Sketchfab')
        self.status_info_label.setText('')
        self.enable_skfb_ui(True)
        self.name_tb.setText('{}'.format(self.strip_craft_name(index)))

    def update_status(self, status):
        ''' Updates the upload status gui'''
        self.upload_status = status
        print(self.upload_status)
        if self.upload_status.startswith('http'):
            self.status_info_label.setText('<a href=\"{}\">See your model here</a>'.format(self.upload_status))
            self.status_info_label.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
            self.status_info_label.setOpenExternalLinks(True)
        else:
            self.status_info_label.setText('Error : {}'.format(self.upload_status))

    def start_upload(self):
        if not len(self.api_token_tb.text()) == 32:
            QtGui.QMessageBox.information(self, "Missing informations", 'Please set or check your Sketchfab API token')
            return
        self.upload_status = 'Building ...'
        self.set_upload_btn_state('building')
        self.enable_skfb_ui(False)
        self.repaint()
        try:
            to_utf8 = lambda qstring: unicode(qstring.toUtf8(), encoding='utf8').encode('utf8')
            self.uploader, self.reply = self.manager.upload(
                self.craft_list_ql.currentRow(),
                name=to_utf8(self.name_tb.text()),
                description=to_utf8(self.description_tb.toPlainText()),
                tags='KSP ' + to_utf8(self.tags_tb.text()),
                token=to_utf8(self.api_token_tb.text()))
        except Exception as e:
            # QtGui.QMessageBox.critical(self, "Error", '{}'.format(e))
            QtGui.QMessageBox.critical(self, "Unhandled error", '{}: {}'.format(type(e).__name__, e))
            self.set_upload_btn_state('publish')
            return

        progress = QtGui.QProgressDialog("Uploading...", "Cancel", 0, 100, self)
        self.set_upload_btn_state('upload')
        self.enable_skfb_ui(True)
        progress.setWindowTitle("Sketchfab upload")
        progress.setWindowModality(QtCore.Qt.WindowModal)
        progress.show()

        def upload_finished():
            if not progress.wasCanceled():
                http_response = self.reply.readAll()
                print(http_response)
                self.status_info_label.setText('Finished')
                data = json.loads(str(http_response))
                if 'uid' in data:
                    url = SKETCHFAB_MODEL_URL + '/' + data['uid']
                    self.update_status(url)
                    QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))

                    # Save the sketchfab api token in user_data
                    to_utf8 = lambda qstring: unicode(qstring.toUtf8(), encoding='utf8').encode('utf8')
                    self.user_data['api'] = to_utf8(self.api_token_tb.text())
                    self.dump_user_data()
                else:
                    self.update_status(data['detail'])

                progress.close()
            self.status_info_label.setText('Finished')
            self.set_upload_btn_state('publish')

        def upload_error():
            progress.cancel()
            rawData = str(self.reply.readAll())
            data = dict()
            try:
                data = json.loads(rawData)
                QtGui.QMessageBox.critical(self, "Upload error", data["detail"])
                self.update_status(data['detail'])
            except ValueError:
                print('Cancelled')
                QtGui.QMessageBox.warning(self, "Upload error", "Cancelled by the user")
                return
            progress.close()
            self.reply = None
            self.set_upload_btn_state('publish')

        def upload_progress(value, max):
            progress.setValue(value)
            progress.setMaximum(max + 1)
            if value == max:
                progress.setLabelText('Processing...')

        def upload_canceled():
            self.reply.abort()
            self.reply = None
            self.status_info_label.setText('Cancelled')
            self.set_upload_btn_state('publish')
            self.manager.clear_tmp_files()

        def ssl_errors(err_list):
            for err in err_list:
                print(err.errorString())
            self.reply.ignoreSslErrors()

        ## Connections
        self.reply.finished.connect(upload_finished)
        self.reply.error.connect(upload_error)
        self.reply.uploadProgress.connect(upload_progress)
        self.reply.sslErrors.connect(ssl_errors)
        progress.canceled.connect(upload_canceled)

    def enable_skfb_ui(self, bool_value):
        self.api_token_tb.setEnabled(bool_value)
        self.name_tb.setEnabled(bool_value)
        self.description_tb.setEnabled(bool_value)
        self.tags_tb.setEnabled(bool_value)

    def set_craft_list(self):
        self.craft_list_ql.clear()
        self.craft_list = self.manager.get_craft_list()
        if self.craft_list:
            self.craft_list_ql.addItems(self.craft_list)
            self.craft_list_ql.setEnabled(True)

        return self.craft_list

    def update_game_ui(self, game_dir):
        ''' Check if the game dir exists and if it contains crafts'''
        self.game_dir = game_dir
        self.game_path_tb.setText(self.game_dir)
        if os.path.exists(game_dir):
            self.manager.set_game_dir(str(game_dir))
            if self.set_craft_list():
                self.game_path_info_label.hide()
                self.upload_btn.setEnabled(True)
                self.user_data['path'] = '{}'.format(self.game_dir)
                self.dump_user_data()
            else:
                self.craft_list_ql.setEnabled(False)
                self.craft_list = []
                self.craft_list_ql.clear()
                self.game_path_info_label.show()
                self.enable_skfb_ui(False)
        else:
            self.game_path_info_label.show()
            self.game_path_info_label.setStyleSheet("color: rgb(150, 0, 0);")
            self.craft_list_ql.setEnabled(False)

    def search_game_directory(self):
        ''' Open a filedialog to locate game directory'''
        dialog = QtGui.QFileDialog()
        dialog.setFileMode(QtGui.QFileDialog.Directory)
        dialog.setOption(QtGui.QFileDialog.ShowDirsOnly)
        self.update_game_ui(dialog.getExistingDirectory())
