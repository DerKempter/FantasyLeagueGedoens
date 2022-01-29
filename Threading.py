import time

from PyQt5.QtCore import QThreadPool, QThread, QRunnable, pyqtSlot, QObject, pyqtSignal


class Worker(QRunnable):

    def __init__(self, function, **kwargs):
        QRunnable.__init__(self)
        self.function = function
        self.kwargs = kwargs
        self.list = [arg for arg in self.kwargs]
        self.return_str = ""

    @pyqtSlot()
    def run(self) -> None:
        self.return_str = self.function(**self.kwargs)


class WorkerSignals(QObject):
    return_string = pyqtSignal()
    get_worksheets = pyqtSignal([])
    get_dates_lists = pyqtSignal(list, list)
