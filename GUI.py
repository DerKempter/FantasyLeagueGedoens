import datetime
import sys

from PyQt5.QtCore import *

import Logic
import Logic as logic
import datetime as dt

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QScrollArea, QWidget, QVBoxLayout, QLabel

__VERSION__ = '0.2.2-beta'

import Threading


class MyWindow(QMainWindow):
    lec_teams = ['Astralis', 'Excel Esports', 'Fnatic', 'G2 Esports', 'MAD Lions', 'Misfits Gaming',
                 'Rogue (European Team)', 'SK Gaming', 'Team BDS', 'Team Vitality']
    lcs_teams = ['100 Thieves', 'Counter Logic Gaming', 'Cloud9', 'Dignitas', 'Evil Geniuses.NA', 'FlyQuest',
                 'Golden Guardians', 'Immortals', 'Team Liquid', 'TSM']

    def __init__(self):
        super(MyWindow, self).__init__()

        self.threadpool = QThreadPool()
        print(f"Multithreading with maximum {self.threadpool.maxThreadCount()} threads")

        self.signals = Threading.WorkerSignals()
        self.signals.return_string.connect(self.handle_return_string_signal)
        self.signals.get_worksheets.connect(self.handle_get_worksheets_signal)
        self.signals.get_dates_lists.connect(self.handle_get_dates_lists_signal)

        self.curr_ws = None
        self.current_rtr_str = None

        self.update_player_agency = None
        self.lcs_player_list = None
        self.update_all_player_and_teams = None
        self.update_single_player_team_btn = None
        self.player_league_cb = None
        self.player_selector_to_update = None
        self.text_output_label = None
        self.lec_player_list = None
        self.matchup_dates = None
        self.weeks = None
        self.week_selector = None
        self.setGeometry(0, 0, 500, 500)
        self.setWindowTitle("FantasyLeague")
        self.update_matchup_points_button = None
        self.week_label = None
        self.show_matchup_points_button = None
        self.progress_bar = None
        self.user_selector_cb = None
        self.show_user_player_points_for_week_btn = None
        self.user_names = None
        self.fantasy_hub, self.lec_players, self.lcs_players, self.prev_matches = None, None, None, None
        self.init_ui()

        # All out commented are deprecated for now
        # self.lec_lcs_team_selector_team_2 = None
        # self.lec_lcs_team_selector_team_1 = None
        # self.lec_lcs_cb = None
        # self.player_cb = None
        # self.day_label = None
        # self.day_selector = None
        # self.team_cb = None
        # self.update_table_points_button = None
        # self.tournament_cb = None

    def handle_return_string_signal(self, rtr_str: str):
        self.current_rtr_str = rtr_str

    def handle_get_worksheets_signal(self, rtr_ws: []):
        self.curr_ws = rtr_ws

    def handle_get_dates_lists_signal(self, weeks, week_dates):
        self.weeks = weeks
        self.matchup_dates = week_dates
        self.week_selector.clear()
        self.week_selector.addItems(self.weeks)
        self.week_selector.adjustSize()

    def init_ui(self):
        self.week_label = QtWidgets.QLabel(self)
        self.week_label.setText("Select Week to update")
        self.week_label.adjustSize()
        self.week_label.move(50, 35)

        self.week_selector = QtWidgets.QComboBox(self)
        self.week_selector.move(50, 50)
        self.week_selector.addItems(['Loading...'])
        self.week_selector.adjustSize()
        self.gen_week_for_dropdown_thread()

        self.update_matchup_points_button = QtWidgets.QPushButton(self)
        self.update_matchup_points_button.setText("Update Matchups")
        self.update_matchup_points_button.adjustSize()
        self.update_matchup_points_button.clicked.connect(self.update_matchup_points_thread)
        self.update_matchup_points_button.move(150, 50)

        self.show_matchup_points_button = QtWidgets.QPushButton(self)
        self.show_matchup_points_button.setText("Show Matchups")
        self.show_matchup_points_button.adjustSize()
        self.show_matchup_points_button.clicked.connect(self.show_matchup_points)
        self.show_matchup_points_button.move(250, 50)

        self.text_output_label = ScrollLabel(self)
        self.text_output_label.setText("")
        self.text_output_label.move(400, 50)
        self.text_output_label.resize(275, 400)
        self.resize(750, 500)

        self.player_selector_to_update = QtWidgets.QComboBox(self)
        self.player_selector_to_update.move(220, 85)
        self.player_selector_to_update.adjustSize()

        self.player_league_cb = QtWidgets.QComboBox(self)
        self.player_league_cb.addItems(['Please select from dropdown',
                                        'use LEC-Players and Teams',
                                        'use LCS-Players and Teams'])
        self.player_league_cb.adjustSize()
        self.player_league_cb.currentIndexChanged.connect(self.player_league_combobox_changed_action_thread)
        self.player_league_cb.move(50, 85)

        self.update_single_player_team_btn = QtWidgets.QPushButton(self)
        self.update_single_player_team_btn.setText('Update selected player for selected Week')
        self.update_single_player_team_btn.adjustSize()
        self.update_single_player_team_btn.move(50, 110)
        self.update_single_player_team_btn.clicked.connect(self.update_single_player_team_button_clicked_thread)

        self.update_all_player_and_teams = QtWidgets.QPushButton(self)
        self.update_all_player_and_teams.setText('Update all Player and Teams')
        self.update_all_player_and_teams.adjustSize()
        self.update_all_player_and_teams.move(50, 150)
        self.update_all_player_and_teams.clicked.connect(self.update_all_players_and_teams_button_clicked_thread)

        self.update_player_agency = QtWidgets.QPushButton(self)
        self.update_player_agency.setText('Update which player belongs to whom')
        self.update_player_agency.adjustSize()
        self.update_player_agency.clicked.connect(self.update_player_agency_btn_clicked_thread)
        self.update_player_agency.move(50, 200)

        self.user_selector_cb = QtWidgets.QComboBox(self)
        self.user_selector_cb.addItems(['Loading...'])
        self.user_selector_cb.adjustSize()
        self.user_selector_cb.move(50, 275)
        self.fill_user_selector_cb_thread()

        self.show_user_player_points_for_week_btn = QtWidgets.QPushButton(self)
        self.show_user_player_points_for_week_btn.setText('Show Points From All Players For Selected User')
        self.show_user_player_points_for_week_btn.adjustSize()
        self.show_user_player_points_for_week_btn.move(50, 300)
        self.show_user_player_points_for_week_btn.clicked.connect(self.show_user_player_points_for_week_btn_clicked)

        self.progress_bar = QtWidgets.QProgressBar(self)
        self.progress_bar.setMaximum(100)
        self.progress_bar.move(400, 455)
        self.progress_bar.resize(self.text_output_label.frameGeometry().width(), 25)
        self.progress_bar.setVisible(False)

        # Deprecated
        # self.day_label = QtWidgets.QLabel(self)
        # self.day_label.setText("Select Weekday for updating")
        # self.day_label.adjustSize()
        # self.day_label.move(50, 85)
        # self.day_label.setVisible(False)

        # self.day_selector = QtWidgets.QComboBox(self)
        # self.day_selector.addItems(['1', '2', '3', '4'])
        # self.day_selector.adjustSize()
        # self.day_selector.move(50, 100)
        # self.day_selector.setVisible(False)

        # self.update_table_points_button = QtWidgets.QPushButton(self)
        # self.update_table_points_button.setText("Update Player-Tables")
        # self.update_table_points_button.adjustSize()
        # self.update_table_points_button.clicked.connect(self.update_table_points_thread)
        # self.update_table_points_button.move(50, 225)
        # self.update_table_points_button.setVisible(False)

        # self.lec_lcs_cb = QtWidgets.QComboBox(self)
        # self.lec_lcs_cb.addItems(["don't use specific Teams", 'use LEC-Teams', 'use LCS-Teams'])
        # self.lec_lcs_cb.adjustSize()
        # self.lec_lcs_cb.currentIndexChanged.connect(self.lec_lcs_combobox_changed_action_thread)
        # self.lec_lcs_cb.move(50, 125)
        # self.lec_lcs_cb.setVisible(False)

        # self.team_cb = QtWidgets.QCheckBox(self)
        # self.team_cb.setText("update Teams")
        # self.team_cb.adjustSize()
        # self.team_cb.move(50, 185)
        # self.team_cb.setVisible(False)

        # self.player_cb = QtWidgets.QCheckBox(self)
        # self.player_cb.setText("update Players")
        # self.player_cb.adjustSize()
        # self.player_cb.move(150, 185)
        # self.player_cb.setVisible(False)

        # self.tournament_cb = QtWidgets.QComboBox(self)
        # self.tournament_cb.addItems(['LEC 2022 Spring', 'LCS 2022 Spring', 'LCS 2022 Lock In'])
        # self.tournament_cb.adjustSize()
        # self.tournament_cb.move(50, 205)
        # self.tournament_cb.setVisible(False)

        # self.lec_lcs_team_selector_team_1 = QtWidgets.QComboBox(self)
        # self.lec_lcs_team_selector_team_1.move(50, 150)
        # self.lec_lcs_team_selector_team_1.setVisible(False)

        # self.lec_lcs_team_selector_team_2 = QtWidgets.QComboBox(self)
        # self.lec_lcs_team_selector_team_2.move(150, 150)
        # self.lec_lcs_team_selector_team_2.setVisible(False)

    def update_player_agency_btn_clicked_thread(self):
        kwargs = {}
        worker = Threading.Worker(self.update_player_agency_btn_clicked, **kwargs)
        self.threadpool.start(worker)

    def update_player_agency_btn_clicked(self):
        if self.fantasy_hub is None or self.lec_players is None or self.lcs_players is None:
            self.fantasy_hub, self.lec_players, self.lcs_players = logic.open_spreadsheet()
        worksheets = [self.fantasy_hub, self.lec_players, self.lcs_players]
        self.progress_bar.setVisible(False)
        return_string = logic.update_player_agency(worksheets)

        if return_string == "":
            return_string = "No Agencies updated"

        self.text_output_label.setText(return_string)

        return return_string

    def update_all_players_and_teams_button_clicked_thread(self):
        kwargs = {}
        worker = Threading.Worker(self.update_all_players_and_teams_button_clicked, **kwargs)
        self.threadpool.start(worker)

    def update_all_players_and_teams_button_clicked(self):
        if self.fantasy_hub is None or self.lec_players is None or self.lcs_players is None:
            self.fantasy_hub, self.lec_players, self.lcs_players = logic.open_spreadsheet()
        if self.lcs_player_list is None and self.lec_player_list is None:
            self.lec_player_list = self.grab_players_to_display(self.lec_players, 1)
            self.lcs_player_list = self.grab_players_to_display(self.lcs_players, 2)
        if self.week_selector.currentText().startswith('loading'):
            return self.wait_for_week_dropdown()
        return_string = ""
        league_to_update = self.player_league_cb.currentText()
        if 'LEC' in league_to_update:
            league_to_update = 'lec'
            target_player_list = self.lec_player_list
        elif 'LCS' in league_to_update:
            league_to_update = 'lcs'
            target_player_list = self.lcs_player_list
        else:
            self.text_output_label.setText("Please Select A League From The Dropdown Menu")
            return 1

        sel_week = self.week_selector.currentText()
        week_index = self.weeks.index(sel_week)
        week_date_to_update = self.matchup_dates[week_index]

        temp_players_list = None
        update_player_list = False

        progress = 0
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(target_player_list))
        self.progress_bar.setValue(progress)

        for player in target_player_list:
            progress += 1
            temp_update_string = return_string + f"Updating Points for {player}..."
            self.text_output_label.setText(temp_update_string)

            player_to_update = player

            is_team = False
            if player_to_update in self.lec_teams or player_to_update in self.lcs_teams:
                is_team = True

            if player_to_update == "" or league_to_update == "" or week_date_to_update == "":
                return_string = "Wrong league selected."
                break

            if target_player_list[-1] == player:
                update_player_list = True

            dummy_return = logic.update_single_player_points_for_week(player_to_update,
                                                                      week_date_to_update,
                                                                      week_index,
                                                                      league_to_update,
                                                                      [self.lec_players,
                                                                       self.lcs_players],
                                                                      is_team,
                                                                      temp_players_list,
                                                                      update_player_list)
            temp_players_list = dummy_return[1]
            temp_return_string = dummy_return[0]
            if not temp_return_string.startswith('N'):
                return_string += temp_return_string
                return_string += "\n"
            self.progress_bar.setValue(progress)
            self.text_output_label.setText(return_string)

        if return_string != "":
            self.text_output_label.setText(return_string)
        else:
            self.text_output_label.setText('No Points updated.')

        return return_string

    def wait_for_week_dropdown(self):
        while self.week_selector.currentText().startswith('loading'):
            label_string = 'Week Dropdown-Menu is still loading.\n'
            label_string += 'Please Wait until loading is complete and select a week which you want to update.'
            self.text_output_label.setText(label_string)
        return 1

    def update_single_player_team_button_clicked_thread(self):
        kwargs = {}
        worker = Threading.Worker(self.update_single_player_team_button_clicked, **kwargs)
        self.threadpool.start(worker)

    def update_single_player_team_button_clicked(self):
        if self.fantasy_hub is None or self.lec_players is None or self.lcs_players is None:
            self.fantasy_hub, self.lec_players, self.lcs_players = logic.open_spreadsheet()
        if self.week_selector.currentText().startswith('loading'):
            return self.wait_for_week_dropdown()
        self.progress_bar.setVisible(False)
        player_to_update = self.player_selector_to_update.currentText()
        league_to_update = self.player_league_cb.currentText()
        return_string = ""
        if 'LEC' in league_to_update:
            league_to_update = 'lec'
        elif 'LCS' in league_to_update:
            league_to_update = 'lcs'
        else:
            self.text_output_label.setText("Please Select A League From The Dropdown Menu")
            return 1
        sel_week = self.week_selector.currentText()
        week_index = self.weeks.index(sel_week)
        week_date_to_update = self.matchup_dates[week_index]

        is_team = False
        if player_to_update in self.lec_teams or player_to_update in self.lcs_teams:
            is_team = True

        if player_to_update == "" or league_to_update == "" or week_date_to_update == "":
            return 1

        temp_update_string = return_string + f"Updating Points for {player_to_update}"
        self.text_output_label.setText(temp_update_string)

        return_string, players_list = logic.update_single_player_points_for_week(player_to_update, week_date_to_update,
                                                                                 week_index, league_to_update,
                                                                                 [self.lec_players, self.lcs_players],
                                                                                 is_team)
        self.text_output_label.setText(return_string)

    def player_league_combobox_changed_action_thread(self, index):
        kwargs = {'index': index}
        worker = Threading.Worker(self.player_league_combobox_changed_action, **kwargs)
        self.threadpool.start(worker)

    def player_league_combobox_changed_action(self, index):
        if self.lec_players is None or self.lcs_players is None:
            self.lec_players, self.lcs_players = logic.open_spreadsheet(to_use=['lcs_players', 'lec_players'])
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

    def grab_players_to_display_thread(self, worksheet, index):
        kwargs = {'ws': worksheet, 'index': index}
        worker = Threading.Worker(self.grab_players_to_display, **kwargs)
        self.threadpool.start(worker)

    @staticmethod
    def grab_players_to_display(worksheet, index):
        ws_strings = ['A2:A61', 'A2:A77']
        player_list = worksheet.get(ws_strings[index - 1])
        return [item for sublist in player_list for item in sublist]

    # Deprecated Don't Use
    def lec_lcs_combobox_changed_action_thread(self, index):
        kwargs = {'index': index}
        worker = Threading.Worker(self.lec_lcs_combobox_changed_action, **kwargs)
        self.threadpool.start(worker)

    # Deprecated Don't Use
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

    def update_matchup_points_thread(self):
        kwargs = {}
        worker = Threading.Worker(self.update_matchup_points, **kwargs)
        self.threadpool.start(worker)

    def update_matchup_points(self):
        if self.fantasy_hub is None or self.lec_players is None or self.lcs_players is None:
            self.fantasy_hub, self.lec_players, self.lcs_players = logic.open_spreadsheet()
        self.progress_bar.setVisible(False)
        spreadsheets = [self.fantasy_hub, self.lec_players, self.lcs_players]
        week = self.week_selector.currentText()
        week_index = self.weeks.index(week)
        today = datetime.datetime.today()
        week_date = datetime.datetime(1, 1, 1, 1, 1, 1)
        for letter, number in logic.WEEKS:
            week_number = self.fantasy_hub.acell(f"{letter}{number}").value
            if week_number == week:
                week_string = self.fantasy_hub.acell(f"{Logic.inc_letter(letter, 1)}{number}").value
                week_date = dt.datetime.strptime(week_string, "%Y-%m-%d")
                break
        if (today - week_date) > datetime.timedelta(days=3):
            return_string = f'Week {week_index + 1} has closed.'
            self.text_output_label.setText(return_string)
            return return_string
        print(week, week_index, self.matchup_dates[week_index])
        response = logic.update_points_for_matchup(spreadsheets, self.matchup_dates[week_index], week, week_index)
        self.text_output_label.setText(response)

    def show_matchup_points_thread(self):
        kwargs = {}
        worker = Threading.Worker(self.show_matchup_points, **kwargs)
        self.threadpool.start(worker)

    def show_matchup_points(self):
        if self.fantasy_hub is None:
            self.fantasy_hub = logic.open_spreadsheet(to_use=['fantasy_hub'])
        self.progress_bar.setVisible(False)
        spreadsheet = self.fantasy_hub
        week = self.week_selector.currentText()
        week_index = self.weeks.index(week)
        print(week, week_index, self.matchup_dates[week_index])
        response = logic.grab_points_for_matchup(spreadsheet, self.matchup_dates[week_index], week)

        self.text_output_label.setText(response)

    # Deprecated Don't Use
    def update_table_points_thread(self):
        kwargs = {}
        worker = Threading.Worker(self.update_table_points, **kwargs)
        self.threadpool.start(worker)

    # Deprecated Don't Use
    def update_table_points(self):
        if self.prev_matches is None:
            self.prev_matches = logic.open_spreadsheet(use_prev=True, only_use_prev=True)
        self.progress_bar.setVisible(False)
        week = self.week_selector.currentText()
        week_index = self.weeks.index(week)
        week_date = self.matchup_dates[week_index]
        week_date = dt.datetime.strptime(week_date, "%Y-%m-%d").date()
        day_adjustment_int = int(self.day_selector.currentText()) - 1
        adjusted_week_date = str(week_date + dt.timedelta(day_adjustment_int))
        tournament = self.tournamend_cb.currentText()
        print("update button clicked")
        print(week, week_index, week_date, adjusted_week_date)
        response = logic.get_game_stats_and_update_spread(adjusted_week_date, week_index, tournament,
                                                          self.lec_lcs_team_selector_team_1.currentText(),
                                                          self.lec_lcs_team_selector_team_2.currentText(),
                                                          self.player_cb.isChecked(), self.team_cb.isChecked(),
                                                          self.prev_matches)
        self.text_output_label.setText(response)

    def gen_week_for_dropdown_thread(self):
        kwargs = {}
        worker = Threading.Worker(self.gen_week_for_dropdown, **kwargs)
        self.threadpool.start(worker)

    def gen_week_for_dropdown(self):
        if not self.fantasy_hub:
            self.fantasy_hub = logic.open_spreadsheet(only_use_hub=True)
        weeks_coord = [("L", "18"), ("L", "22"), ("L", "26"), ("L", "30"), ("P", "18"),
                       ("P", "22"), ("P", "26"), ("P", "30"), ("T", "18"), ("T", "22")]
        weeks = []
        week_dates = []
        for letter, number in weeks_coord:
            week_string = self.fantasy_hub.acell(f"{letter}{number}").value
            week_date = self.fantasy_hub.acell(f"{logic.inc_letter(letter, 1)}{number}").value
            weeks.append(week_string)
            week_dates.append(week_date)
        self.signals.get_dates_lists.emit(weeks, week_dates)
        return weeks, week_dates

    def fill_user_selector_cb(self):
        if self.fantasy_hub is None or self.lec_players is None or self.lcs_players is None:
            self.fantasy_hub, self.lec_players, self.lcs_players = logic.open_spreadsheet()
        name_coord_x = ['M', 'N', 'O', 'P', 'Q', 'R']
        name_coord_y = '3'
        names = []
        for letter in name_coord_x:
            coord = letter + name_coord_y
            user_name = self.fantasy_hub.acell(coord).value
            names.append(user_name)
        self.user_selector_cb.clear()
        if len(names) > 0:
            self.user_selector_cb.addItems(names)
            self.user_selector_cb.adjustSize()
            self.user_names = names
        else:
            self.user_selector_cb.addItems(['Error'])
            self.user_selector_cb.adjustSize()
            self.text_output_label.setText("Please Restart App and contact admin if it still doesn't work")
            self.text_output_label.adjustSize()

    def fill_user_selector_cb_thread(self):
        kwargs = {}
        worker = Threading.Worker(self.fill_user_selector_cb, **kwargs)
        self.threadpool.start(worker)

    def show_user_player_points_for_week_btn_clicked(self):
        if self.fantasy_hub is None or self.lec_players is None or self.lcs_players is None:
            self.fantasy_hub, self.lec_players, self.lcs_players = logic.open_spreadsheet()
        sel_week = self.week_selector.currentText()
        week_index = self.weeks.index(sel_week)
        name_coordinates_x = ['M', 'N', 'O', 'P', 'Q', 'R']
        name_coordinates_y = ['3', '11']
        user_string = self.user_selector_cb.currentText()
        user_index = self.user_names.index(user_string)
        name_player_coordinates = f"{name_coordinates_x[user_index]}{name_coordinates_y[0]}:" \
                                  f"{name_coordinates_x[user_index]}{name_coordinates_y[1]}"
        worksheets = [self.fantasy_hub, self.lec_players, self.lcs_players]
        return_string = logic.grab_player_and_points_for_user(worksheets, user_string, name_player_coordinates,
                                                              week_index)

        self.text_output_label.setText(return_string)


class ScrollLabel(QScrollArea):

    # constructor
    def __init__(self, *args, **kwargs):
        QScrollArea.__init__(self, *args, **kwargs)

        # making widget resizable
        self.setWidgetResizable(True)

        # making q-widget object
        content = QWidget(self)
        self.setWidget(content)

        # vertical box layout
        lay = QVBoxLayout(content)

        # creating label
        self.label = QLabel(content)

        # setting alignment to the text
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # making label multi-line
        self.label.setWordWrap(True)

        # adding label to the layout
        lay.addWidget(self.label)

    # the setText method
    # noinspection PyPep8Naming
    def setText(self, text):
        # setting text to the label
        self.label.setText(text)


def bootstrap():
    app = QApplication(sys.argv)
    win = MyWindow()

    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    bootstrap()
