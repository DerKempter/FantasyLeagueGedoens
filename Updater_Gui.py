import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow

import GUI


class UpdaterWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.curr_version = ""
        self.open_main = False

        self.setGeometry(0, 0, 400, 300)
        self.setWindowTitle("FantasyLeague-Updater")

        self.curr_ver_label_text = QtWidgets.QLabel(self)
        self.curr_ver_label_text.setText('Current Version:')
        self.curr_ver_label_text.adjustSize()
        self.curr_ver_label_text.move(25, 25)

        self.curr_ver_label = QtWidgets.QLabel(self)
        self.curr_ver_label.setText(self.get_curr_ver())
        self.curr_ver_label.adjustSize()
        self.curr_ver_label.move(25, 50)

        self.start_main_app = QtWidgets.QCheckBox(self)
        self.start_main_app.setText('Start Main Application after closing Updater?')
        self.start_main_app.adjustSize()
        self.start_main_app.stateChanged.connect(self.open_main_checkbox_state_changed)
        self.start_main_app.move(25, 125)

    def get_curr_ver(self):
        with open('GUI.py') as f:
            for line in f:
                line = line.strip()
                if '__VERSION__' in line:
                    _, current_version = line.split('=', maxsplit=1)
                    self.curr_version = current_version.strip().replace("'", "")
                    break
        return self.curr_version

    def open_main_checkbox_state_changed(self, state: bool):
        self.open_main = state

    def check_for_new_version(self):
        return True

    def update_to_new_version(self):
        return None


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = UpdaterWindow()

    win.show()
    app.exec()
    bootstrap = win.open_main
    if bootstrap:
        print('Booting up main application...')
        GUI.bootstrap()
    else:
        print('not bootstrapping, shutting down')
