import mwclient
import datetime as dt
import gspread

SPREADSHEET_NAME = "High Society Kranichfeld"


def inc_letter(letter: chr, increment_int) -> chr:
    return chr(ord(letter) + increment_int)


def open_spreadsheet():
    sa = gspread.service_account('service_account.json')
    sh = sa.open(SPREADSHEET_NAME)

    fantasy_hub = sh.worksheet("Fantasy-HUB")
    lec_players = sh.worksheet("LEC-Spieler")
    lcs_players = sh.worksheet("LCS-Spieler")

    return fantasy_hub, lec_players, lcs_players


def get_game_stats_and_update_spread(date_string: str, tournament: str, team1: str = None, team2: str = None,
                                     get_players=True, get_teams=True):
    if not get_players and not get_teams:
        print("updating nothing")
        return "Updating nothing"
    date = dt.datetime.strptime(date_string, "%Y-%m-%d").date()

    site = mwclient.Site('lol.fandom.com', path='/')
    if team1 is None or team2 is None:
        if get_players:
            player_response = site.api('cargoquery',
                                       limit="max",
                                       tables="ScoreboardGames=SG, ScoreboardPlayers=SP",
                                       join_on="SG.GameId=SP.GameId",
                                       fields="SG.Tournament, SG.DateTime_UTC, SG.Team1, SG.Team2, SG.Winner, "
                                              "SG.Patch, SG.Team1Dragons, SG.Team2Dragons, SG.Team1Barons, "
                                              "SG.Team2Barons, SG.Team1Towers, SG.Team2Towers, SG.RiotPlatformGameId, "
                                              "SP.Link, SP.Team, SP.Champion, SP.SummonerSpells, SP.KeystoneMastery, "
                                              "SP.KeystoneRune, SP.Role, SP.UniqueGame, SP.Side, SP.Assists, SP.Kills, "
                                              "SP.Deaths, SP.CS",
                                       where=f"SG.DateTime_UTC >= '{str(date)} 00:00:00' AND SG.DateTime_UTC <= "
                                             f"'{str(date + dt.timedelta(1))} 00:00:00' AND SG.Tournament = '{tournament}' "
                                       )
        else:
            player_response = None
        if get_teams:
            team_response = site.api('cargoquery',
                                     limit="max",
                                     tables="ScoreboardGames=SG",
                                     fields="SG.Tournament, SG.DateTime_UTC, SG.Team1, SG.Team2, SG.Winner, SG.Patch, "
                                            "SG.Team1Dragons, SG.Team2Dragons, SG.Team1Barons, SG.Team2Barons, "
                                            "SG.Team1Towers, SG.Team2Towers, SG.RiotPlatformGameId, SG.RiotGameId",
                                     where=f"SG.DateTime_UTC >= '{str(date)} 00:00:00' AND SG.DateTime_UTC <= "
                                           f"'{str(date + dt.timedelta(1))} 00:00:00' AND SG.Tournament = '{tournament}'"
                                     )
        else:
            team_response = None
    else:
        if get_players:
            player_response = site.api('cargoquery',
                                       limit="10",
                                       tables="ScoreboardGames=SG, ScoreboardPlayers=SP",
                                       join_on="SG.GameId=SP.GameId",
                                       fields="SG.Tournament, SG.DateTime_UTC, SG.Team1, SG.Team2, SG.Winner, "
                                              "SG.Patch, SP.Link, SP.Team, SP.Champion, SP.SummonerSpells, "
                                              "SP.KeystoneMastery, SP.KeystoneRune, SP.Role, SP.UniqueGame, "
                                              "SP.Side, SP.Assists, SP.Kills, SP.Deaths, SP.CS",
                                       where=f"SG.DateTime_UTC >= '{str(date)} 00:00:00' AND SG.DateTime_UTC <= "
                                             f"'{str(date + dt.timedelta(1))} 00:00:00' AND SG.Tournament = '{tournament}' "
                                             f"AND ((SG.Team1 = '{team1}' AND SG.Team2 = '{team2}') "
                                             f"OR (SG.Team1 = '{team2}' AND SG.Team2 = '{team1}'))"
                                       )
        else:
            player_response = None
        if get_teams:
            team_response = site.api('cargoquery',
                                     limit="max",
                                     tables="ScoreboardGames=SG",
                                     fields="SG.Tournament, SG.DateTime_UTC, SG.Team1, SG.Team2, SG.Winner, SG.Patch, "
                                            "SG.Team1Dragons, SG.Team2Dragons, SG.Team1Barons, SG.Team2Barons, "
                                            "SG.Team1Towers, SG.Team2Towers, SG.RiotPlatformGameId, SG.RiotGameId",
                                     where=f"SG.DateTime_UTC >= '{str(date)} 00:00:00' AND SG.DateTime_UTC <= "
                                           f"'{str(date + dt.timedelta(1))} 00:00:00' AND SG.Tournament = "
                                           f"'{tournament}' "
                                           f"AND ((SG.Team1 = '{team1}' AND SG.Team2 = '{team2}') "
                                           f"OR (SG.Team1 = '{team2}' AND SG.Team2 = '{team1}'))"
                                     )
        else:
            team_response = None

    score_to_update = []

    if player_response is not None:
        player_data = player_response.get('cargoquery')
        for game_dict_key in player_data:
            game_dict = game_dict_key.get('title')

            points, player = calc_points(game_dict, 'player')[0]
            score_to_update.append((points, player))
    print(score_to_update)

    if team_response is not None:
        team_data = team_response.get('cargoquery')
        for game_dict_key in team_data:
            game_dict = game_dict_key.get('title')

            team_points = calc_points(game_dict, 'team')
            for points in team_points:
                score_to_update.append(points)
    print(score_to_update)

    if len(score_to_update) > 0:
        update_spreadsheet_player_points(score_to_update, tournament)
        return f"updated {score_to_update}"


def calc_points(game_dictionary, category: str):
    kill = 3
    tod = -1
    assist = 2
    cs = 0.01

    fb = baron = elder = 2
    turm = drake = herald = win = 1
    steal_factor = 2

    if category == 'player':
        champ = game_dictionary.get('Champion')
        team = game_dictionary.get('Team')
        player = game_dictionary.get('Link')
        assists: float = float(game_dictionary.get('Assists')) * assist
        kills: float = float(game_dictionary.get('Kills')) * kill
        farm: float = float(game_dictionary.get('CS')) * cs
        deaths: float = float(game_dictionary.get('Deaths')) * tod

        # doubles = game_dict.get('DoubleKills')                # TODO somehow implement this from Riot Data
        # triples = game_dict.get('TripleKills')
        # quads = game_dict.get('QuadraKills')
        # pentas = game_dict.get('PentaKills')

        sum = assists + kills + farm + deaths
        print(f"Punkte für {player}: {assists}+{kills}+{farm}{deaths} = {sum}")

        sums = [(sum, player)]

    else:
        team1 = game_dictionary.get('Team1') if type(game_dictionary.get('Team1')) == str else 0
        team2 = game_dictionary.get('Team2') if type(game_dictionary.get('Team2')) == str else 0
        towers1 = int(game_dictionary.get('Team1Towers')) if type(game_dictionary.get('Team1Towers')) == str else 0
        towers2 = int(game_dictionary.get('Team2Towers')) if type(game_dictionary.get('Team2Towers')) == str else 0
        dragons1 = int(game_dictionary.get('Team1Dragons')) if type(game_dictionary.get('Team1Dragons')) == str else 0
        dragons2 = int(game_dictionary.get('Team2Dragons')) if type(game_dictionary.get('Team2Dragons')) == str else 0
        barons1 = int(game_dictionary.get('Team1Barons')) if type(game_dictionary.get('Team1Barons')) == str else 0
        barons2 = int(game_dictionary.get('Team2Barons')) if type(game_dictionary.get('Team2Barons')) == str else 0
        heralds1 = int(game_dictionary.get('Team1RiftHeralds')) if type(
            game_dictionary.get('Team1RiftHeralds')) == str else 0
        heralds2 = int(game_dictionary.get('Team2RiftHeralds')) if type(
            game_dictionary.get('Team2RiftHeralds')) == str else 0

        sum1 = towers1 * turm + dragons1 * drake + barons1 * baron + heralds1 * herald
        sum2 = towers2 * turm + dragons2 * drake + barons2 * baron + heralds2 * herald

        sums = [(sum1, team1), (sum2, team2)]
        print(f"Punkte für {team1}: {sum1}")
        print(f"Punkte für {team2}: {sum2}")

    return sums


def update_spreadsheet_player_points(scores_to_update: [], league: str):
    fantasy_hub, lec_players, lcs_players = open_spreadsheet()
    if league == "LEC 2022 Spring":
        spread_string = 'F65:G124'
        lec_players_list = lec_players.get(spread_string)
        for score, player_string in scores_to_update:
            for player in lec_players_list:
                if player[0] == player_string:
                    if type(player[1]) == str:
                        player[1] = float(player[1].replace(',', '.')) + score
                    else:
                        player[1] = float(player[1]) + score
                elif type(player[1]) == str:
                    player[1] = float(player[1].replace(',', '.'))
        lec_players.update(spread_string, lec_players_list)
    elif league == "LCS 2022 Lock In" or league == "LCS 2022 Spring":
        spread_string = 'F80:G154'
        lcs_players_list = lcs_players.get(spread_string)
        for score, player_string in scores_to_update:
            for player in lcs_players_list:
                if player[0] == player_string:
                    if type(player[1]) == str:
                        player[1] = float(player[1].replace(',', '.')) + score
                    else:
                        player[1] = float(player[1]) + score
                elif type(player[1]) == str:
                    player[1] = float(player[1].replace(',', '.'))
        lcs_players.update(spread_string, lcs_players_list)
    else:
        print("wrongly formatted league string!")


def update_points_for_matchup(match_week_date, sel_week: str):
    fantasy_hub, lec_players, lcs_players = open_spreadsheet()
    spread_string_lec = 'F65:H124'
    spread_string_lcs = 'F80:H154'
    lec_players_list = lec_players.get(spread_string_lec)
    lcs_players_list = lcs_players.get(spread_string_lcs)
    player_scores: dict = get_points_from_match_week_players(match_week_date)
    team_scores: dict = get_points_from_match_week_teams(match_week_date)
    sums = []
    for i in range(0, 6):
        letter = chr(ord('M') + i)
        start_cell = letter + '5'
        end_cell = letter + '11'
        players = fantasy_hub.get(f"{start_cell}:{end_cell}")
        # print(players)
        temp_sum = 0.0
        for player in players:
            player_string = player[0]
            for player_name, player_score in player_scores.items():
                if player_string == player_name:
                    temp_sum = temp_sum + player_score
                    break
            for team_name, team_score in team_scores.items():
                if player_string == team_name:
                    temp_sum = temp_sum + team_score
                    break
        sums.append((f"{letter}3", temp_sum))
    # print(sums)
    weeks = [("L", "18"), ("L", "22"), ("L", "26"), ("L", "30"), ("P", "18")]
    sums_with_names = []
    for coord, score in sums:
        name = fantasy_hub.acell(coord).value
        sums_with_names.append((name, score))
    for letter, number in weeks:
        week_string = fantasy_hub.acell(f"{letter}{number}").value
        if week_string == sel_week:
            start_cell = f"{letter}{int(number) + 1}"
            end_cell = f"{inc_letter(letter, 3)}{int(number) + 3}"
            match_table = fantasy_hub.get(f"{start_cell}:{end_cell}")
            for row in match_table:
                for name, score in sums_with_names:
                    if row[0] == name:
                        row[1] = score
                    elif row[3] == name:
                        row[2] = score
            # print(match_table)
            fantasy_hub.update(f"{start_cell}:{end_cell}", match_table)
            break


def get_points_from_match_week_players(date_string):
    date = dt.datetime.strptime(date_string, "%Y-%m-%d").date()

    site = mwclient.Site('lol.fandom.com', path='/')
    response = site.api('cargoquery',
                        limit="max",
                        tables="ScoreboardGames=SG, ScoreboardPlayers=SP",
                        join_on="SG.GameId=SP.GameId",
                        fields="SG.Tournament, SG.DateTime_UTC, SG.Team1, SG.Team2, SG.Winner, SG.Patch, "
                               "SP.Link, SP.Team, SP.Champion, SP.SummonerSpells, SP.KeystoneMastery, SP.KeystoneRune, "
                               "SP.Role, SP.UniqueGame, SP.Side, SP.Assists, SP.Kills, SP.Deaths, SP.CS",
                        where=f"SG.DateTime_UTC >= '{str(date)} 00:00:00' AND SG.DateTime_UTC <= "
                              f"'{str(date + dt.timedelta(5))} 00:00:00' AND SG.Tournament = 'LCS 2022 Spring' OR "
                              f"SG.Tournament = 'LEC 2022 Spring' OR SG.Tournament = 'LCS 2022 Lock In'"
                        )
    data = response.get('cargoquery')
    player_scores = []

    for game_dict_key in data:
        game_dict = game_dict_key.get('title')

        points, player = (calc_points(game_dict, 'player'))[0]
        player_scores.append((player, points))
    score_per_player = {}
    for team_combo in player_scores:
        player1 = {team_combo[0]: team_combo[1]}
        if team_combo[0] in score_per_player:
            score_per_player[team_combo[0]] = score_per_player.get(team_combo[0]) + team_combo[1]
        else:
            score_per_player.update(player1)
    return score_per_player


def get_points_from_match_week_teams(date_string):
    date = dt.datetime.strptime(date_string, "%Y-%m-%d").date()

    site = mwclient.Site('lol.fandom.com', path='/')
    response = site.api('cargoquery',
                        limit="max",
                        tables="ScoreboardGames=SG",
                        fields="SG.Tournament, SG.DateTime_UTC, SG.Team1, SG.Team2, SG.Winner, SG.Patch, "
                               "SG.Team1Dragons, SG.Team2Dragons, SG.Team1Barons, SG.Team2Barons, SG.Team1Towers, "
                               "SG.Team2Towers, SG.RiotPlatformGameId, SG.RiotGameId",
                        where=f"SG.DateTime_UTC >= '{str(date)} 00:00:00' AND SG.DateTime_UTC <= "
                              f"'{str(date + dt.timedelta(5))} 00:00:00' AND SG.Tournament = 'LCS 2022 Spring' OR "
                              f"SG.Tournament = 'LEC 2022 Spring' OR SG.Tournament = 'LCS 2022 Lock In'"
                        )
    data = response.get('cargoquery')
    team_scores = []

    for game_dict_key in data:
        game_dict = game_dict_key.get('title')

        temp_team_scores = calc_points(game_dict, 'team')
        for team in temp_team_scores:
            team_scores.append(team)
    score_per_team = {}
    for team_combo in team_scores:
        team1 = {team_combo[1]: team_combo[0]}
        if team_combo[0] in score_per_team:
            score_per_team[team_combo[0]] = score_per_team.get(team_combo[0]) + team_combo[1]
        else:
            score_per_team.update(team1)
    return score_per_team


def get_game_stats(date_string: str, tournament: str):
    date = dt.datetime.strptime(date_string, "%Y-%m-%d").date()

    site = mwclient.Site('lol.fandom.com', path='/')
    response = site.api('cargoquery',
                        limit="max",
                        tables="ScoreboardGames=SG",
                        fields="SG.Tournament, SG.DateTime_UTC, SG.Team1, SG.Team2, SG.Winner, SG.Patch, "
                               "SG.Team1Dragons, SG.Team2Dragons, SG.Team1Barons, SG.Team2Barons, SG.Team1Towers, "
                               "SG.Team2Towers, SG.RiotPlatformGameId, SG.RiotGameId",
                        where=f"SG.DateTime_UTC >= '{str(date)} 00:00:00' AND SG.DateTime_UTC <= "
                              f"'{str(date + dt.timedelta(1))} 00:00:00' AND SG.Tournament = '{tournament}' "
                        )
    data = response.get('cargoquery')
    print(data)

# get_game_stats_and_update_spread("2022-01-15", "LCS 2022 Lock In", get_teams=True, get_players=True)

# update_points_for_matchup("2022-01-14", "W1")

# get_game_stats("2022-01-14", "LCS 2022 Lock In")

# get_points_from_match_week_teams("2022-01-14")

# get_points_from_match_week_players("2022-01-14")
