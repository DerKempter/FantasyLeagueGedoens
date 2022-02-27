import json

import mariadb
import Logic



def other_stuff():
    sql = "INSERT INTO `playerTeams` (teamName) VALUES(%s)"
    val = [['100 Thieves'], ['Counter Logic Gaming'], ['Cloud9'], ['Dignitas'], ['Evil Geniuses.NA'], ['FlyQuest'],
           ['Golden Guardians'], ['Immortals'], ['Team Liquid'], ['TSM']]

    cursor.executemany(sql, val)

    mydb.commit()

    for x in cursor:
        print(x)


def generate_sql_insert_players(db):
    fantasy_hub, lec_players, lcs_players = Logic.open_spreadsheet()

    spread_string_builder_lec = ['2', '61']
    spread_string_builder_lcs = ['2', '77']

    spread_string_index = 'D'
    spread_string_lec = f"A{spread_string_builder_lec[0]}:{spread_string_index}{spread_string_builder_lec[1]}"
    spread_string_lcs = f"A{spread_string_builder_lcs[0]}:{spread_string_index}{spread_string_builder_lcs[1]}"

    lec_players_list = lec_players.get(spread_string_lec)
    lcs_players_list = lcs_players.get(spread_string_lcs)
    player_lists = [lec_players_list, lcs_players_list]

    sql_base = f"INSERT INTO players (name, userId, leagueTeamId, position, leagueId) VALUES(%s, %s, %s, %s, %s)"
    vals = []
    for player_list in player_lists:
        for player in player_list:
            name = player[0]
            team = player[1]
            role = player[2]
            agency = player[3]
            vals.append((name, convert_agency_to_id(agency, db), convert_team_to_id(team, db),
                         convert_role_to_int(role), player_lists.index(player_list)))
    temp_cursor = db.cursor()
    if len(vals) <= 0:
        return f"no vals generated"
    temp_cursor.executemany(sql_base, vals)
    db.commit()
    return 0


def convert_role_to_int(role_to_convert: str) -> int:
    roles = ['top', 'jungle', 'mid', 'bot', 'support', 'team']
    for role in roles:
        if role_to_convert.lower() == role:
            return roles.index(role)


def convert_agency_to_id(agency_to_convert: str, db) -> int:
    if agency_to_convert == "FA":
        agency_to_convert = "Market"
    temp_cursor = db.cursor()
    sql = f"SELECT user.userId FROM user WHERE userName = '{agency_to_convert}'"
    temp_cursor.execute(sql)
    res = []
    for value in temp_cursor:
        res.append(value)
    return res[0][0]


def convert_team_to_id(team_to_convert: str, db) -> int:
    temp_cursor = db.cursor()
    sql = f"SELECT playerTeams.teamId FROM playerTeams WHERE teamName = '{team_to_convert}'"
    temp_cursor.execute(sql)
    res = []
    for value in temp_cursor:
        res.append(value)
    return res[0][0]

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
