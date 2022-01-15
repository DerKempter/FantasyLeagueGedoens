import sys
import main


from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow


class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.week_selector = None
        self.setGeometry(0, 0, 720, 720)
        self.setWindowTitle("FantasyLeague")
        self.update_matchup_points = None
        self.label = None
        self.fantasy_hub, self.lec_players, self.lcs_players = main.open_spreadsheet()
        self.initUi()

    def initUi(self):
        self.label = QtWidgets.QLabel(self)
        self.label.setText("Select Week to update")
        self.label.adjustSize()
        self.label.move(50, 25)

        self.week_selector = QtWidgets.QComboBox(self)
        self.weeks, self.matchup_dates = self.gen_week_for_dropdown()
        self.week_selector.addItems(self.weeks)
        self.week_selector.move(50, 50)

        self.update_matchup_points = QtWidgets.QPushButton(self)
        self.update_matchup_points.setText("Update Matchups")
        self.update_matchup_points.clicked.connect(self.update_matchup_points_button)
        self.update_matchup_points.move(150, 50)

    def update_matchup_points_button(self):
        week = self.week_selector.currentText()
        week_index = self.weeks.index(week)
        print(week, week_index, self.matchup_dates[week_index])
        main.update_points_for_matchup(self.matchup_dates[week_index], week)

    def gen_week_for_dropdown(self):
        weeks_coord = [("L", "18"), ("L", "22"), ("L", "26"), ("L", "30"), ("P", "18")]
        weeks = []
        week_dates = []
        for letter, number in weeks_coord:
            week_string = self.fantasy_hub.acell(f"{letter}{number}").value
            week_date = self.fantasy_hub.acell(f"{main.inc_letter(letter, 1)}{number}").value
            weeks.append(week_string)
            week_dates.append(week_date)
        return weeks, week_dates

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MyWindow()

    win.show()
    sys.exit(app.exec_())
