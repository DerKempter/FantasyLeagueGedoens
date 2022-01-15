import sys
import main
import datetime as dt

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow


class MyWindow(QMainWindow):
    lec_teams = ['Astralis', 'Excel Esports', 'Fnatic', 'G2 Esports', 'MAD Lions', 'Misfits Gaming',
                 'Rogue (European Team)', 'SK Gaming', 'Team BDS', 'Team Vitality']
    lcs_teams = ['100 Thieves', 'CLG', 'Cloud9', 'Dignitas', 'Evil Geniuses', 'FlyQuest', 'Golden Guardians',
                 'Immortals', 'Team Liquid', 'TSM']

    def __init__(self):
        super(MyWindow, self).__init__()
        self.player_cb = None
        self.day_label = None
        self.day_selector = None
        self.team_cb = None
        self.update_table_points_button = None
        self.matchup_dates = None
        self.weeks = None
        self.week_selector = None
        self.setGeometry(0, 0, 500, 500)
        self.setWindowTitle("FantasyLeague")
        self.update_matchup_points_button = None
        self.week_label = None
        self.fantasy_hub, self.lec_players, self.lcs_players = main.open_spreadsheet()
        self.initUi()

    def initUi(self):
        self.week_label = QtWidgets.QLabel(self)
        self.week_label.setText("Select Week to update")
        self.week_label.adjustSize()
        self.week_label.move(50, 35)

        self.day_label = QtWidgets.QLabel(self)
        self.day_label.setText("Select Weekday for updating")
        self.day_label.adjustSize()
        self.day_label.move(50, 85)

        self.week_selector = QtWidgets.QComboBox(self)
        self.weeks, self.matchup_dates = self.gen_week_for_dropdown()
        self.week_selector.addItems(self.weeks)
        self.week_selector.adjustSize()
        self.week_selector.move(50, 50)

        self.day_selector = QtWidgets.QComboBox(self)
        self.day_selector.addItems(['1', '2', '3', '4'])
        self.day_selector.adjustSize()
        self.day_selector.move(50, 100)

        self.update_matchup_points_button = QtWidgets.QPushButton(self)
        self.update_matchup_points_button.setText("Update Matchups")
        self.update_matchup_points_button.adjustSize()
        self.update_matchup_points_button.clicked.connect(self.update_matchup_points)
        self.update_matchup_points_button.move(150, 50)

        self.update_table_points_button = QtWidgets.QPushButton(self)
        self.update_table_points_button.setText("Update Player-Tables")
        self.update_table_points_button.adjustSize()
        self.update_table_points_button.clicked.connect(self.update_table_points)
        self.update_table_points_button.move(50, 250)

        self.update_table_points_label = QtWidgets.QLabel(self)
        self.update_table_points_label.setText("")
        self.update_table_points_label.move(50, 275)

        self.lec_lcs_cb = QtWidgets.QComboBox(self)
        self.lec_lcs_cb.addItems(["don't use specific Teams", 'use LEC-Teams', 'use LCS-Teams'])
        self.lec_lcs_cb.adjustSize()
        self.lec_lcs_cb.currentIndexChanged.connect(self.lec_lcs_combobox_changed_action)
        self.lec_lcs_cb.move(50, 125)

        self.team_cb = QtWidgets.QCheckBox(self)
        self.team_cb.setText("update Teams")
        self.team_cb.adjustSize()
        self.team_cb.move(50, 185)

        self.player_cb = QtWidgets.QCheckBox(self)
        self.player_cb.setText("update Players")
        self.player_cb.adjustSize()
        self.player_cb.move(150, 185)

        self.tournamend_cb = QtWidgets.QComboBox(self)
        self.tournamend_cb.addItems(['LEC 2022 Spring', 'LCS 2022 Spring', 'LCS 2022 Lock In'])
        self.tournamend_cb.adjustSize()
        self.tournamend_cb.move(50, 225)

        self.lec_lcs_team_selector_team_1 = QtWidgets.QComboBox(self)
        self.lec_lcs_team_selector_team_1.move(50, 150)

        self.lec_lcs_team_selector_team_2 = QtWidgets.QComboBox(self)
        self.lec_lcs_team_selector_team_2.move(150, 150)

    def lec_lcs_combobox_changed_action(self, index):
        if index == 0:
            self.lec_lcs_team_selector_team_1.clear()
            self.lec_lcs_team_selector_team_2.clear()
        elif index == 1:
            self.lec_lcs_team_selector_team_1.clear()
            self.lec_lcs_team_selector_team_2.clear()
            self.lec_lcs_team_selector_team_1.addItems(self.lec_teams)
            self.lec_lcs_team_selector_team_2.addItems(self.lec_teams)
        elif index == 2:
            self.lec_lcs_team_selector_team_1.clear()
            self.lec_lcs_team_selector_team_2.clear()
            self.lec_lcs_team_selector_team_1.addItems(self.lcs_teams)
            self.lec_lcs_team_selector_team_2.addItems(self.lcs_teams)

    def update_matchup_points(self):
        week = self.week_selector.currentText()
        week_index = self.weeks.index(week)
        print(week, week_index, self.matchup_dates[week_index])
        main.update_points_for_matchup(self.matchup_dates[week_index], week)

    def update_table_points(self):
        week = self.week_selector.currentText()
        week_index = self.weeks.index(week)
        week_date = self.matchup_dates[week_index]
        week_date = dt.datetime.strptime(week_date, "%Y-%m-%d").date()
        day_adjustment_int = int(self.day_selector.currentText()) - 1
        adjusted_week_date = str(week_date + dt.timedelta(day_adjustment_int))
        tournament = self.tournamend_cb.currentText()
        print("update button clicked")
        print(week, week_index, week_date, adjusted_week_date)
        response = main.get_game_stats_and_update_spread(adjusted_week_date, tournament,
                                              self.lec_lcs_team_selector_team_1.currentText(),
                                              self.lec_lcs_team_selector_team_2.currentText(),
                                              self.player_cb.isChecked(), self.team_cb.isChecked())
        self.update_table_points_label.setText(response)
        self.update_table_points_label.adjustSize()

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
