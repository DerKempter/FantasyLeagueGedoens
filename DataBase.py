import json

import mariadb

# import Logic as logic
import DbObjects


class DatabaseHandler:

    def __init__(self, user, pw, host, port, db):
        self.database = None
        self.changes_made = False

        self.database = self.init_db(user, pw, host, port, db)

    def __del__(self):
        if self.changes_made:
            self.save_db()

    def save_db(self):
        return 1

    def init_db(self, user, password, host,
                port, db):
        try:
            conn = mariadb.connect(
                user=user,
                password=password,
                host=host,
                port=port,
                database=db
            )
            conn.autocommit = False
        except mariadb.Error as e:
            return f"Error connecting to MariaDB Platform: {e}"
        return conn

    # def generate_sql_insert_players(self):
    #     fantasy_hub, lec_players, lcs_players = logic.open_spreadsheet()
    #
    #     spread_string_builder_lec = ['2', '61']
    #     spread_string_builder_lcs = ['2', '77']
    #
    #     spread_string_index = 'D'
    #     spread_string_lec = f"A{spread_string_builder_lec[0]}:{spread_string_index}{spread_string_builder_lec[1]}"
    #     spread_string_lcs = f"A{spread_string_builder_lcs[0]}:{spread_string_index}{spread_string_builder_lcs[1]}"
    #
    #     lec_players_list = lec_players.get(spread_string_lec)
    #     lcs_players_list = lcs_players.get(spread_string_lcs)
    #     player_lists = [lec_players_list, lcs_players_list]
    #
    #     temp_cursor = self.database.cursor()
    #
    #     sql_base = f"INSERT INTO players (name, userId, leagueTeamId, position, leagueId) VALUES(%s, %s, %s, %s, %s)"
    #     vals = []
    #     for player_list in player_lists:
    #         for player in player_list:
    #             name = player[0]
    #             team = player[1]
    #             role = player[2]
    #             agency = player[3]
    #             vals.append([name, self.convert_agency_to_id(agency), self.convert_team_to_id(team),
    #                          self.convert_role_to_int(role), player_lists.index(player_list) + 1])
    #
    #     if len(vals) <= 0:
    #         return f"no vals generated"
    #     temp_cursor.executemany(sql_base, vals)
    #     self.database.commit()
    #     return 0

    def convert_role_to_int(self, role_to_convert: str) -> int:
        roles = ['top', 'jungle', 'mid', 'bot', 'support', 'team']
        for role in roles:
            if role_to_convert.lower() == role:
                return roles.index(role)

    def convert_agency_to_id(self, agency_to_convert: str) -> int:
        if agency_to_convert == "FA":
            agency_to_convert = "Market"
        temp_cursor = self.database.cursor()
        sql = f"SELECT user.userId FROM user WHERE userName = '{agency_to_convert}'"
        temp_cursor.execute(sql)
        res = []
        for value in temp_cursor:
            res.append(value)
        return res[0][0]

    def convert_team_to_id(self, team_to_convert: str) -> int:
        temp_cursor = self.database.cursor()
        sql = f"SELECT playerteams.teamId FROM playerteams WHERE teamName = '{team_to_convert}'"
        temp_cursor.execute(sql)
        res = []
        for value in temp_cursor:
            res.append(value)
        return res[0][0]

    def grab_player_id_from_name_str(self, name_list: []) -> []:
        sql_str_base = "SELECT playerId, name FROM `players` WHERE `players`.`name` REGEXP '%s'"
        player_str_base = ""
        res = []

        for player in name_list:
            player_str_base += f"{player}|"

        sql_statement = sql_str_base.replace('%s', player_str_base[:-1])

        cursor = self.database.cursor()
        cursor.execute(sql_statement)

        for player_id, name in cursor:
            res.append((player_id, name))

        return res

    def check_if_player_points_is_in_week(self, player_points: DbObjects.PlayerPoints):
        cursor = self.database.cursor()
        sql_base = "SELECT * FROM `playerpoints` WHERE `playerpoints`.`week` = %0 AND `playerpoints`.`playerId` = %1"
        week_id = player_points.week
        player_id = player_points.playerId
        sql_statement = sql_base.replace('%0', str(week_id)).replace('%1', str(player_id))

        cursor.execute(sql_statement)
        res = []

        for val in cursor:
            res.append(val)

        if len(res) == 0:
            return False
        elif len(res) > 1:
            return "more than one entry found!"
        else:
            return res

    def other_stuff(self, sql="", val=""):
        # sql = "INSERT INTO `playerteams` (teamName) VALUES(%s)"
        # val = [['100 Thieves'], ['Counter Logic Gaming'], ['Cloud9'], ['Dignitas'], ['Evil Geniuses.NA'], ['FlyQuest'],
        #       ['Golden Guardians'], ['Immortals'], ['Team Liquid'], ['TSM']]

        cursor = self.database.cursor()
        cursor.executemany(sql, val)
        self.database.commit()

# database = DatabaseHandler()
# database.populate_db_from_gsheet()
#
# print(database)
# del database
