import sys
import configparser

from PyQt5.QtWidgets import QApplication

from GUI import MyWindow


class Bootstrapper:
    def bootstrap(self):
        app = QApplication(sys.argv)

        win = MyWindow(self.check_for_config())

        win.show()

        sys.exit(app.exec_())

    def check_for_config(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        if not config.has_section('DB-Login'):
            return False
        else:
            return True


if __name__ == '__main__':
    bootstrapper = Bootstrapper()
    bootstrapper.bootstrap()
