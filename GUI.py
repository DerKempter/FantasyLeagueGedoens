import sys
import main
import datetime as dt

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow


class MyWindow(QMainWindow):
    lec_teams = ['Astralis', 'Excel Esports', 'Fnatic', 'G2 Esports', 'MAD Lions', 'Misfits Gaming',
                 'Rogue (European Team)', 'SK Gaming', 'Team BDS', 'Team Vitality']
    lcs_teams = ['100 Thieves', 'Counter Logic Gaming', 'Cloud9', 'Dignitas', 'Evil Geniuses.NA', 'FlyQuest',
                 'Golden Guardians', 'Immortals', 'Team Liquid', 'TSM']

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
        self.fantasy_hub, self.lec_players, self.lcs_players, self.prev_matches = None, None, None, None
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
        self.update_table_points_button.move(50, 225)

        self.update_table_points_label = QtWidgets.QLabel(self)
        self.update_table_points_label.setText("")
        self.update_table_points_label.move(50, 425)

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
        self.tournamend_cb.move(50, 205)

        self.lec_lcs_team_selector_team_1 = QtWidgets.QComboBox(self)
        self.lec_lcs_team_selector_team_1.move(50, 150)

        self.lec_lcs_team_selector_team_2 = QtWidgets.QComboBox(self)
        self.lec_lcs_team_selector_team_2.move(150, 150)

        self.player_selector_to_update = QtWidgets.QComboBox(self)
        self.player_selector_to_update.move(250, 325)

        self.player_league_cb = QtWidgets.QComboBox(self)
        self.player_league_cb.addItems(['Please select from dropdown',
                                        'use LEC-Players and Teams',
                                        'use LCS-Players and Teams'])
        self.player_league_cb.adjustSize()
        self.player_league_cb.currentIndexChanged.connect(self.player_league_combobox_changed_action)
        self.player_league_cb.move(50, 325)

        self.update_single_player_team_btn = QtWidgets.QPushButton(self)
        self.update_single_player_team_btn.setText('Update selected player for selected Week')
        self.update_single_player_team_btn.adjustSize()
        self.update_single_player_team_btn.move(50, 355)
        self.update_single_player_team_btn.clicked.connect(self.update_single_player_team_button_clicked)

        self.update_all_player_and_teams = QtWidgets.QPushButton(self)
        self.update_all_player_and_teams.setText('Update all Player and Teams')
        self.update_all_player_and_teams.adjustSize()
        self.update_all_player_and_teams.move(50, 395)
        self.update_all_player_and_teams.clicked.connect(self.update_all_players_and_teams_button_clicked)

    def update_all_players_and_teams_button_clicked(self):
        if self.fantasy_hub is None and self.lec_players is None and self.lcs_players is None:
            self.fantasy_hub, \
            self.lec_players, \
            self.lcs_players = main.open_spreadsheet()
        if self.lcs_player_list is None and self.lec_player_list is None:
            self.lec_player_list = self.grab_players_to_display(self.lec_players, 1)
            self.lcs_player_list = self.grab_players_to_display(self.lcs_players, 2)
        return_string = ""
        sel_week = self.week_selector.currentText()
        week_index = self.weeks.index(sel_week)
        week_date_to_update = self.matchup_dates[week_index]
        league_to_update = self.player_league_cb.currentText()
        target_player_list = None
        if 'LEC' in league_to_update:
            league_to_update = 'lec'
            target_player_list = self.lec_player_list
        elif 'LCS' in league_to_update:
            league_to_update = 'lcs'
            target_player_list = self.lcs_player_list
        else:
            league_to_update = ""

        for player in target_player_list:
            player_to_update = player

            is_team = False
            if player_to_update in self.lec_teams or player_to_update in self.lcs_teams:
                is_team = True

            if player_to_update == "" or league_to_update == "" or week_date_to_update == "":
                return_string = "Wrong league selected."
                break

            return_string += main.update_single_player_points_for_week(player_to_update, week_date_to_update,
                                                                       league_to_update, is_team)
            return_string += "\n"
        self.update_table_points_label.setText(return_string)
        self.update_table_points_label.adjustSize()
        return return_string

    def update_single_player_team_button_clicked(self):
        if self.fantasy_hub is None and self.lec_players is None and self.lcs_players is None:
            self.fantasy_hub, \
            self.lec_players, \
            self.lcs_players, = main.open_spreadsheet()
        player_to_update = self.player_selector_to_update.currentText()
        league_to_update = self.player_league_cb.currentText()
        if 'LEC' in league_to_update:
            league_to_update = 'lec'
        elif 'LCS' in league_to_update:
            league_to_update = 'lcs'
        else:
            league_to_update = ""
        sel_week = self.week_selector.currentText()
        week_index = self.weeks.index(sel_week)
        week_date_to_update = self.matchup_dates[week_index]

        is_team = False
        if player_to_update in self.lec_teams or player_to_update in self.lcs_teams:
            is_team = True

        if player_to_update == "" or league_to_update == "" or week_date_to_update == "":
            return 1

        return_string = main.update_single_player_points_for_week(player_to_update, week_date_to_update,
                                                                  league_to_update, is_team)
        self.update_table_points_label.setText(return_string)
        self.update_table_points_label.adjustSize()

    def player_league_combobox_changed_action(self, index):
        if self.lec_players is None or self.lcs_players is None:
            self.lec_players, self.lcs_players = main.open_spreadsheet(to_use=['lcs_players', 'lec_players'])
        self.lec_player_list = self.grab_players_to_display(self.lec_players, 1)
        self.lcs_player_list = self.grab_players_to_display(self.lcs_players, 2)
        if index == 0:
            self.player_selector_to_update.clear()
        elif index == 1:
            self.player_selector_to_update.clear()
            self.player_selector_to_update.addItems(self.lec_player_list)
            self.player_selector_to_update.adjustSize()
        elif index == 2:
            self.player_selector_to_update.clear()
            self.player_selector_to_update.addItems(self.lcs_player_list)
            self.player_selector_to_update.adjustSize()

    def grab_players_to_display(self, ws, index):
        ws_strings = ['F65:F124', 'F80:F155']
        player_list = ws.get(ws_strings[index - 1])
        return [item for sublist in player_list for item in sublist]

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
        if week_index < 1:
            return_string = f'Week {week_index + 1} has closed.'
            self.update_table_points_label.setText(return_string)
            return return_string
        print(week, week_index, self.matchup_dates[week_index])
        response = main.update_points_for_matchup(self.matchup_dates[week_index], week)
        self.update_table_points_label.setText(response)
        self.update_table_points_label.adjustSize()

    def update_table_points(self):
        if self.prev_matches is None:
            self.prev_matches = main.open_spreadsheet(use_prev=True, only_use_prev=True)
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
                                                         self.player_cb.isChecked(), self.team_cb.isChecked(),
                                                         self.prev_matches)
        self.update_table_points_label.setText(response)
        self.update_table_points_label.adjustSize()

    def gen_week_for_dropdown(self):
        if not self.fantasy_hub:
            self.fantasy_hub = main.open_spreadsheet(only_use_hub=True)
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
