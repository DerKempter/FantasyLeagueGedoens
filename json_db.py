import json

with open("db.json", "a") as json_file:
    db = json.load(json_file)


def generate_json_str():
    """
{
  "Fantasy_gedoens": {
    "fantasy_hub": {
      "Teams":{
        "Team_x": {
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
          "reserv_3": ""
        },
        "Team_y": {
          "name": "ralf",
          "team_name": "Schalke-04",
          "player_1": "",
          "player_2": "",
          "player_3": "",
          "player_4": "",
          "player_5": "",
          "team_player": "G2",
          "sub_player": "",
          "reserv_1": "",
          "reserv_2": "",
          "reserv_3": ""}
      },
      "Matchups":{
        "week_x":{
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
        "week_y":{
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
      "Trades":{
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
      },
      "Standings":{
        "team_x": {
          "name": "aaa",
          "points": 0.0,
          "wins": 0,
          "losses": 0
        },
        "team_y": {
          "name": "bbb",
          "points": 0.0,
          "wins": 0,
          "losses": 0
        }
      }
    },
    "lec_players": {},
    "lcs_players": {}
  }
}
    """