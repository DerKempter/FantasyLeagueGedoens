import json

import mariadb

import Logic
import Logic as logic


class DatabaseHandler:

    def __init__(self):
        self.database = None
        self.changes_made = False

        self.database = self.init_db()

    def __del__(self):
        if self.changes_made:
            self.save_db()

    def save_db(self):
        return 1

    def init_db(self, user="dbzy0gjx_a8gcac7", password="", host="dbzy0gjx.mariadb.hosting.zone",
                port=3306, db="dbzy0gjx"):
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

    def generate_sql_insert_players(self):
        fantasy_hub, lec_players, lcs_players = Logic.open_spreadsheet()

        spread_string_builder_lec = ['2', '61']
        spread_string_builder_lcs = ['2', '77']

        spread_string_index = 'D'
        spread_string_lec = f"A{spread_string_builder_lec[0]}:{spread_string_index}{spread_string_builder_lec[1]}"
        spread_string_lcs = f"A{spread_string_builder_lcs[0]}:{spread_string_index}{spread_string_builder_lcs[1]}"

        lec_players_list = lec_players.get(spread_string_lec)
        lcs_players_list = lcs_players.get(spread_string_lcs)
        player_lists = [lec_players_list, lcs_players_list]

        temp_cursor = self.database.cursor()

        sql_base = f"INSERT INTO players (name, userId, leagueTeamId, position, leagueId) VALUES(%s, %s, %s, %s, %s)"
        vals = []
        for player_list in player_lists:
            for player in player_list:
                name = player[0]
                team = player[1]
                role = player[2]
                agency = player[3]
                vals.append([name, self.convert_agency_to_id(agency), self.convert_team_to_id(team),
                             self.convert_role_to_int(role), player_lists.index(player_list) + 1])

        if len(vals) <= 0:
            return f"no vals generated"
        temp_cursor.executemany(sql_base, vals)
        self.database.commit()
        return 0

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

    def other_stuff(self, sql="", val=""):
        #sql = "INSERT INTO `playerteams` (teamName) VALUES(%s)"
        #val = [['100 Thieves'], ['Counter Logic Gaming'], ['Cloud9'], ['Dignitas'], ['Evil Geniuses.NA'], ['FlyQuest'],
        #       ['Golden Guardians'], ['Immortals'], ['Team Liquid'], ['TSM']]

        cursor = self.database.cursor()
        cursor.executemany(sql, val)
        self.database.commit()

    # def populate_db_from_gsheet(self):
    #     fantasy_hub, lec_players, lcs_players = logic.open_spreadsheet()
    #     self.populate_teams_in_json_db(fantasy_hub)
    #     self.populate_matchups_in_json_db(fantasy_hub)
    #     self.populate_trades_in_json_db(fantasy_hub)
    #     self.populate_standings_in_json_db(fantasy_hub)
    #
    #     self.changes_made = True
    #
    # def populate_teams_in_json_db(self, fantasy_hub):
    #     teams_raw = fantasy_hub.get(f"M3:R14")
    #     teams = [[] for i in range(len(teams_raw[0]))]
    #     for row in teams_raw:
    #         for col in row:
    #             i = row.index(col)
    #             teams[i].append(col)
    #
    #     for team in teams:
    #         print(team)
    #         i = teams.index(team)
    #         temp_team = {"name": team[0], "team_name": team[1], "player_1": team[2], "player_2": team[3],
    #                      "player_3": team[4], "player_4": team[5], "player_5": team[6], "team_player": team[7],
    #                      "sub_player": team[8], "reserve_1": team[9], "reserve_2": team[10], "reserve_3": team[11]}
    #
    #         self.json_db_league["fantasy_league"]["fantasy_hub"]["teams"][f"{i}"] = temp_team

    # def populate_matchups_in_json_db(self, fantasy_hub):
    #     matchups_raw_0 = fantasy_hub.get(f"L18:O33")
    #     matchups_raw_1 = fantasy_hub.get(f"P18:S33")
    #     matchups_raw_2 = fantasy_hub.get(f"T18:W25")
    #     matchups_raw = [matchups_raw_0, matchups_raw_1, matchups_raw_2]
    #     matchups_filtered = []
    #     for raw_matchups in matchups_raw:
    #         # matchup = [raw_matchups[0:4], raw_matchups[4:8], raw_matchups[8:12], raw_matchups[12:-1]]
    #         matchups_filtered.append(raw_matchups[0:4])
    #         matchups_filtered.append(raw_matchups[4:8])
    #         matchups_filtered.append(raw_matchups[8:12])
    #         matchups_filtered.append(raw_matchups[12:])
    #         # matchups_filtered.append(matchup)
    #     for matchup in matchups_filtered:
    #         if len(matchup) == 0:
    #             continue
    #         week = int(matchup[0][0].replace('W', ''))
    #         week_dict = {"start_date": f"{matchup[0][1]}"}
    #         for match in matchup:
    #             index = matchup.index(match)
    #             if index == 0:
    #                 continue
    #             match_dict = {"player_1": match[0], "points_1": match[1], "player_2": match[3], "points_2": match[2]}
    #             week_dict[f"matchup_{index}"] = match_dict
    #         print(matchup)
    #         # self.json_db_league["fantasy_league"]["fantasy_hub"]["matchups"][f"week_{week}"] = week_dict

    # def populate_trades_in_json_db(self, fantasy_hub):
    #     trades_raw = fantasy_hub.get(f"L37:O44")
    #     for trade in trades_raw:
    #         i = trades_raw.index(trade)
    #         for j in range(len(trade)):
    #             if trade[j] == "Markt":
    #                 trade[j] = "market"
    #         trade_dict = {"from": trade[0], "to": trade[1], "player_1": trade[2], "player_2": trade[3],
    #                       "date": "no_date"}
    #         # self.json_db_league["fantasy_league"]["fantasy_hub"]["trades"][i] = trade_dict

    # def populate_standings_in_json_db(self, fantasy_hub):
    #     standings_raw = fantasy_hub.get(f"V37:Y42")
    #     teams = self.json_db_league["fantasy_league"]["fantasy_hub"]["teams"]
    #     for standing in standings_raw:
    #         name = standing[0]
    #         points = standing[1]
    #         wins = standing[2]
    #         losses = standing[3]
    #         for team_index in teams:
    #             team = teams[team_index]
    #             if team["name"] == name:
    #                 self.json_db_league["fantasy_league"]["fantasy_hub"]["teams"][team_index]["points"] = points
    #                 self.json_db_league["fantasy_league"]["fantasy_hub"]["teams"][team_index]["wins"] = wins
    #                 self.json_db_league["fantasy_league"]["fantasy_hub"]["teams"][team_index]["losses"] = losses

    def generate_json_str_league(self):
        json_string_template = """
        {
          "fantasy_league": {
            "fantasy_hub": {
              "teams": {
                "team_x": {
                  "name": "peter",
                  "team_name": "Schalke-04",
                  "player_1": "",
                  "player_2": "",
                  "player_3": "",
                  "player_4": "",
                  "player_5": "",
                  "team_player": "Vit",
                  "sub_player": "",
                  "reserv_1": "",
                  "reserv_2": "",
                  "reserv_3": "",
                  "points": "10",
                  "wins": 1,
                  "losses": 0
                },
                "team_y": {
                  "name": "ralf",
                  "team_name": "Schalke-04",
                  "player_1": "",
                  "player_2": "",
                  "player_3": "",
                  "player_4": "",
                  "player_5": "",
                  "team_player": "Vit",
                  "sub_player": "",
                  "reserv_1": "",
                  "reserv_2": "",
                  "reserv_3": "",
                  "points": "10",
                  "wins": 1,
                  "losses": 0
                }
              },
              "matchups": {
                "week_x": {
                  "start_date": "01-01-2022",
                  "matchup_x": {
                    "player_1": "aaa",
                    "points_1": 0,
                    "player_2": "bbb",
                    "points_2": 0
                  },
                  "matchup_y": {
                    "player_1": "aaa",
                    "points_1": 0,
                    "player_2": "bbb",
                    "points_2": 0
                  }
                },
                "week_y": {
                  "start_date": "08-01-2022",
                  "matchup_x": {
                    "player_1": "aaa",
                    "points_1": 0,
                    "player_2": "bbb",
                    "points_2": 0
                  },
                  "matchup_y": {
                    "player_1": "aaa",
                    "points_1": 0,
                    "player_2": "bbb",
                    "points_2": 0
                  }
                }
              },
              "trades": {
                "trade_x": {
                  "from": "peter",
                  "to": "rolf",
                  "player_1": "abudabi",
                  "player_2": "ZionSpartan",
                  "date": "01-01-2022"
                },
                "trade_y": {
                  "from": "rolf",
                  "to": "market",
                  "player_1": "jakuzi",
                  "player_2": "WunderWear",
                  "date": "03-01-2022"
                }
              }
            },
            "agencies": {
              "lec_players": {
                "player_x": {
                  "name": "abudabi",
                  "agency": "simom"
                }
              },
              "lcs_players": {
                "player_x": {
                  "name": "abudabi",
                  "agency": "simom"
                }
              }
            }
          }
        }
        """
        json_string = json.loads(json_string_template)
        return json_string

    def generate_json_str_points(self):
        json_string_template = """
        {
          "fantasy_league_points": {
                "lec_players": {
              "player_x": {
                "name": "abudabi",
                "team": "99diebs",
                "points": {
                  "sum_total": 15,
                  "week_x": {
                    "week_total": 15,
                    "kda": 15,
                    "doubles": 0,
                    "triples": 0,
                    "quadras": 0,
                    "pentas": 0,
                    "elder": 0,
                    "soul": 0,
                    "first_tower": false,
                    "first_blood": false,
                    "win_below_thirty": false,
                    "steals": {
                      "dragons": 0,
                      "barons": 0,
                      "herald": 0,
                      "elder": 0
                    }
                  }
                }
              }
            },
            "lcs_players": {
              "player_x": {
                "name": "abudabi",
                "team": "99diebs",
                "points": {
                  "sum_total": 18,
                  "week_x": {
                    "week_total": 18,
                    "kda": 18,
                    "doubles": 0,
                    "triples": 0,
                    "quadras": 0,
                    "pentas": 0,
                    "elder": 0,
                    "soul": 0,
                    "first_tower": true,
                    "first_blood": false,
                    "win_below_thirty": false,
                    "steals": {
                      "dragons": 0,
                      "barons": 0,
                      "herald": 0,
                      "elder": 0
                    }
                  }
                }
              }
            }
          }
        }
        """
        json_string = json.loads(json_string_template)
        return json_string


# database = DatabaseHandler()
# database.populate_db_from_gsheet()
#
# print(database)
# del database
