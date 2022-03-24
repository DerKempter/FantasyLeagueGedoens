import configparser

import DataBase
import DbObjects


def load_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config


def init_db(config):
    db_config = config['DB-Login']
    user = db_config['Username']
    pw = db_config['Password']
    host = db_config['Host']
    port = int(db_config['Port'])
    db = db_config['Database']
    return DataBase.DatabaseHandler(user, pw, host, port, db)


configuration = load_config()

db = init_db(configuration)

player_list = ['carzzy', 'alphari', 'Perkz', 'caps']
temp_obj = DbObjects.PlayerPoints()
temp_obj.playerId = 1
temp_obj.week = 1

id_list = db.grab_player_id_from_name_str(player_list)

obj = db.check_if_player_points_is_in_week(temp_obj)

for object in id_list:
    for key, res in object:
        print(key, res)

# print(id_list)
