import mysql.connector
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


mydb = mysql.connector.connect(host="localhost", user="root", database="fantasy_lcs")

cursor = mydb.cursor()

generate_sql_insert_players(mydb)

# convert_agency_to_id("Jonas", mydb)
