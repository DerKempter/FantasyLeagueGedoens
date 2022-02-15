import json
import Logic as logic


class DatabaseHandler:

    def __init__(self):
        self.json_db_league = None
        self.json_db_points = None
        self.changes_made = False

        self.json_db_league, self.json_db_points = self.init_db()

    def __del__(self):
        if self.changes_made:
            self.save_db()

    def save_db(self):
        with open("db_league.json", "w") as json_file:
            json_file.write(json.dumps(self.json_db_league))
        with open("db_points.json", "w") as json_file:
            json_file.write(json.dumps(self.json_db_points))

    def init_db(self):
        try:
            with open("db_league.json", "r") as file_test:
                _ = json.load(file_test)
        except (json.decoder.JSONDecodeError, FileNotFoundError):
            self.initialize_league_db()
        try:
            with open("db_points.json", "r") as file_test:
                _ = json.load(file_test)
        except (json.decoder.JSONDecodeError, FileNotFoundError):
            self.initialize_points_db()

        with open("db_league.json", "r") as json_file:
            database_league = json.load(json_file)

        with open("db_points.json", "r") as json_file:
            database_points = json.load(json_file)

        return database_league, database_points

    def initialize_league_db(self):
        league_json = self.generate_json_str_league()
        with open("db_league.json", "w+") as league_db:
            league_db.write(json.dumps(league_json))

    def initialize_points_db(self):
        league_json = self.generate_json_str_points()
        with open("db_points.json", "w+") as league_db:
            league_db.write(json.dumps(league_json))

    def populate_db_from_gsheet(self):
        fantasy_hub, lec_players, lcs_players = logic.open_spreadsheet()
        self.populate_teams_in_json_db(fantasy_hub)
        self.populate_matchups_in_json_db(fantasy_hub)
        self.populate_trades_in_json_db(fantasy_hub)
        self.populate_standings_in_json_db(fantasy_hub)

        self.changes_made = True

    def populate_teams_in_json_db(self, fantasy_hub):
        teams_raw = fantasy_hub.get(f"M3:R14")
        teams = [[] for i in range(len(teams_raw[0]))]
        for row in teams_raw:
            for col in row:
                i = row.index(col)
                teams[i].append(col)

        for team in teams:
            print(team)
            i = teams.index(team)
            temp_team = {"name": team[0], "team_name": team[1], "player_1": team[2], "player_2": team[3],
                         "player_3": team[4], "player_4": team[5], "player_5": team[6], "team_player": team[7],
                         "sub_player": team[8], "reserve_1": team[9], "reserve_2": team[10], "reserve_3": team[11]}

            self.json_db_league["fantasy_league"]["fantasy_hub"]["teams"][f"{i}"] = temp_team
        del self.json_db_league["fantasy_league"]["fantasy_hub"]["teams"]["team_x"]
        del self.json_db_league["fantasy_league"]["fantasy_hub"]["teams"]["team_y"]

    def populate_matchups_in_json_db(self, fantasy_hub):
        matchups_raw_0 = fantasy_hub.get(f"L18:O33")
        matchups_raw_1 = fantasy_hub.get(f"P18:S33")
        matchups_raw_2 = fantasy_hub.get(f"T18:W25")
        matchups_raw = [matchups_raw_0, matchups_raw_1, matchups_raw_2]
        matchups_filtered = []
        for raw_matchups in matchups_raw:
            # matchup = [raw_matchups[0:4], raw_matchups[4:8], raw_matchups[8:12], raw_matchups[12:-1]]
            matchups_filtered.append(raw_matchups[0:4])
            matchups_filtered.append(raw_matchups[4:8])
            matchups_filtered.append(raw_matchups[8:12])
            matchups_filtered.append(raw_matchups[12:])
            # matchups_filtered.append(matchup)
        for matchup in matchups_filtered:
            if len(matchup) == 0:
                continue
            week = int(matchup[0][0].replace('W', ''))
            week_dict = {"start_date": f"{matchup[0][1]}"}
            for match in matchup:
                index = matchup.index(match)
                if index == 0:
                    continue
                match_dict = {"player_1": match[0], "points_1": match[1], "player_2": match[3], "points_2": match[2]}
                week_dict[f"matchup_{index}"] = match_dict
            print(matchup)
            self.json_db_league["fantasy_league"]["fantasy_hub"]["matchups"][f"week_{week}"] = week_dict
        del self.json_db_league["fantasy_league"]["fantasy_hub"]["matchups"]["week_x"]
        del self.json_db_league["fantasy_league"]["fantasy_hub"]["matchups"]["week_y"]

        # TODO SAFE TEAMS FOR WEEK IN MATCHUP FOR WEEK

    def populate_trades_in_json_db(self, fantasy_hub):
        trades_raw = fantasy_hub.get(f"L37:O44")
        for trade in trades_raw:
            i = trades_raw.index(trade)
            for j in range(len(trade)):
                if trade[j] == "Markt":
                    trade[j] = "market"
            trade_dict = {"from": trade[0], "to": trade[1], "player_1": trade[2], "player_2": trade[3],
                          "date": "no_date"}
            self.json_db_league["fantasy_league"]["fantasy_hub"]["trades"][i] = trade_dict
        del self.json_db_league["fantasy_league"]["fantasy_hub"]["trades"]["trade_x"]
        del self.json_db_league["fantasy_league"]["fantasy_hub"]["trades"]["trade_y"]

    def populate_standings_in_json_db(self, fantasy_hub):
        standings_raw = fantasy_hub.get(f"V37:Y42")
        teams = self.json_db_league["fantasy_league"]["fantasy_hub"]["teams"]
        for standing in standings_raw:
            name = standing[0]
            points = standing[1]
            wins = standing[2]
            losses = standing[3]
            for team_index in teams:
                team = teams[team_index]
                if team["name"] == name:
                    self.json_db_league["fantasy_league"]["fantasy_hub"]["teams"][team_index]["points"] = points
                    self.json_db_league["fantasy_league"]["fantasy_hub"]["teams"][team_index]["wins"] = wins
                    self.json_db_league["fantasy_league"]["fantasy_hub"]["teams"][team_index]["losses"] = losses

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

database = DatabaseHandler()
database.populate_db_from_gsheet()

print(database)
del database
