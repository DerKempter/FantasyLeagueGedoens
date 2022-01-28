import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow

import GUI


class UpdaterWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.curr_ver_label = QtWidgets.QLabel(self)
        self.curr_ver_label.setText(self.get_curr_ver())
        self.curr_ver_label.adjustSize()

    def get_curr_ver(self):
        return 'geht noch net...'

    def check_for_new_version(self):
        return True

    def update_to_new_version(self):
        return None


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = UpdaterWindow()

    win.show()
    app.exec()
    print('Booting up main application...')
    GUI.bootstrap()
