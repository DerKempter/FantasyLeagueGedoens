import mwclient
import datetime as dt
import gspread

SPREADSHEET_NAME = "High Society Kranichfeld"


def inc_letter(letter: chr, increment_int) -> chr:
    return chr(ord(letter) + increment_int)


def open_spreadsheet(use_prev=False, only_use_prev=False, only_use_hub=False, to_use=None):
    if to_use is None:
        to_use = ['fantasy_hub', 'lec_players', 'lcs_players']
    sa = gspread.service_account('service_account.json')
    sh = sa.open(SPREADSHEET_NAME)
    return_arr = []
    if only_use_hub:
        fantasy_hub = sh.worksheet("Fantasy-HUB")
        return fantasy_hub
    if 'fantasy_hub' in to_use:
        return_arr.append(sh.worksheet("Fantasy-HUB"))
    if 'lec_players' in to_use:
        return_arr.append(sh.worksheet("LEC-Spieler"))
    if 'lcs_players' in to_use:
        return_arr.append(sh.worksheet("LCS-Spieler"))
    if use_prev:
        return_arr.append(sh.worksheet("Prev Matches"))
        if only_use_prev:
            return sh.worksheet("Prev Matches")
    return return_arr


def get_game_stats_and_update_spread(date_string: str, tournament: str, team1: str = None, team2: str = None,
                                     get_players=True, get_teams=True, prev_matches_ws=None):
    if not get_players and not get_teams:
        print("updating nothing")
        return "Updating nothing"
    hour_string = "00:00:00"
    date_arr = [date_string, hour_string]
    date_time_string = ' '.join(date_arr)
    date = dt.datetime.strptime(convert_to_berlin_time(date_time_string), "%Y-%m-%d %H:%M:%S")

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
                                       where=f"(SG.DateTime_UTC >= '{str(date)}' AND SG.DateTime_UTC <= "
                                             f"'{str(date + dt.timedelta(1))}') AND (SG.Tournament = '{tournament}')"
                                       )
        else:
            player_response = None
        if get_teams:
            team_response = site.api('cargoquery',
                                     limit="max",
                                     tables="ScoreboardGames=SG",
                                     fields="SG.Tournament, SG.DateTime_UTC, SG.Team1, SG.Team2, SG.Winner, SG.Patch, "
                                            "SG.Team1Dragons, SG.Team2Dragons, SG.Team1Barons, SG.Team2Barons, "
                                            "SG.Team1Towers, SG.Team2Towers, SG.Team1RiftHeralds, SG.Team2RiftHeralds, "
                                            "SG.RiotPlatformGameId, SG.RiotGameId",
                                     where=f"(SG.DateTime_UTC >= '{str(date)}' AND SG.DateTime_UTC <= "
                                           f"'{str(date + dt.timedelta(hours=24))}') AND (SG.Tournament = '{tournament}')"
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
                                       where=f"(SG.DateTime_UTC >= '{str(date)}' AND SG.DateTime_UTC <= "
                                             f"'{str(date + dt.timedelta(hours=24))}') AND (SG.Tournament = '{tournament}') "
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
                                            "SG.Team1Towers, SG.Team2Towers, SG.Team1RiftHeralds, SG.Team2RiftHeralds, "
                                            "SG.RiotPlatformGameId, SG.RiotGameId",
                                     where=f"(SG.DateTime_UTC >= '{str(date)}' AND SG.DateTime_UTC <= "
                                           f"'{str(date + dt.timedelta(hours=24))}') AND (SG.Tournament = "
                                           f"'{tournament}') "
                                           f"AND ((SG.Team1 = '{team1}' AND SG.Team2 = '{team2}') "
                                           f"OR (SG.Team1 = '{team2}' AND SG.Team2 = '{team1}'))"
                                     )
        else:
            team_response = None

    score_to_update = []
    games_to_add_to_sheet = []
    if prev_matches_ws is None:
        prev_matches_ws = open_spreadsheet(True, True)

    if player_response is not None:
        player_data = player_response.get('cargoquery')
        skipper = 0
        for game_dict_key in player_data:
            if skipper > 0:
                skipper -= 1
                continue
            game_dict = game_dict_key.get('title')

            if check_if_game_was_updated_already(game_dict, prev_matches_ws):
                skipper = 9
                continue

            points, player = calc_points(game_dict, 'player')[0]
            score_to_update.append((points, player))
            game_to_add_to_sheet = [game_dict.get('Team1'),
                                    game_dict.get('Team2'),
                                    game_dict.get('DateTime UTC').split(' ')[0]]
            if game_to_add_to_sheet not in games_to_add_to_sheet:
                games_to_add_to_sheet.append(game_to_add_to_sheet)
    print(score_to_update)
    print(games_to_add_to_sheet)

    if team_response is not None:
        team_data = team_response.get('cargoquery')
        for game_dict_key in team_data:
            game_dict = game_dict_key.get('title')

            if check_if_game_was_updated_already(game_dict, prev_matches_ws):
                continue

            team_points = calc_points(game_dict, 'team')
            for points in team_points:
                score_to_update.append(points)
            game_to_add_to_sheet = [game_dict.get('Team1'),
                                    game_dict.get('Team2'),
                                    game_dict.get('DateTime UTC').split(' ')[0]]
            if game_to_add_to_sheet not in games_to_add_to_sheet:
                games_to_add_to_sheet.append(game_to_add_to_sheet)
    print(score_to_update)
    print(games_to_add_to_sheet)

    if len(score_to_update) > 0 and len(games_to_add_to_sheet) > 0:
        update_spreadsheet_player_points(score_to_update, tournament)
        add_match_to_prev_matches(matches_to_add=games_to_add_to_sheet)
        return f"updated {score_to_update}"
    else:
        return f"Either didn't find any games or all games found through given arguments have already been updated."


def update_single_player_points_for_week(player_string: str, date_string: str, league: str, is_team: bool = False):
    hour_string = "00:00:00"
    date_arr = [date_string, hour_string]
    date_time_string = ' '.join(date_arr)
    date = dt.datetime.strptime(convert_to_berlin_time(date_time_string), "%Y-%m-%d %H:%M:%S")

    site = mwclient.Site('lol.fandom.com', path='/')

    response = None

    if not is_team:
        response = site.api('cargoquery',
                            limit="3",
                            tables="ScoreboardGames=SG, ScoreboardPlayers=SP",
                            join_on="SG.GameId=SP.GameId",
                            fields="SG.Tournament, SG.DateTime_UTC, SG.Team1, SG.Team2, SG.Winner, "
                                   "SG.Patch, SG.Team1Dragons, SG.Team2Dragons, SG.Team1Barons, "
                                   "SG.Team2Barons, SG.Team1Towers, SG.Team2Towers, SG.RiotPlatformGameId, "
                                   "SP.Link, SP.Team, SP.Champion, SP.SummonerSpells, SP.KeystoneMastery, "
                                   "SP.KeystoneRune, SP.Role, SP.UniqueGame, SP.Side, SP.Assists, SP.Kills, "
                                   "SP.Deaths, SP.CS",
                            where=f"(SG.DateTime_UTC >= '{str(date)}' AND SG.DateTime_UTC <= "
                                  f"'{str(date + dt.timedelta(hours=24*5))}') AND (SG.Tournament = 'LCS 2022 Spring' OR"
                                  f" SG.Tournament = 'LEC 2022 Spring' OR SG.Tournament = 'LCS 2022 Lock In') "
                                  f"AND SP.Link = '{player_string}'"
                            )

    if is_team:
        response = site.api('cargoquery',
                            limit="max",
                            tables="ScoreboardGames=SG",
                            fields="SG.Tournament, SG.DateTime_UTC, SG.Team1, SG.Team2, SG.Winner, SG.Patch, "
                                   "SG.Team1Dragons, SG.Team2Dragons, SG.Team1Barons, SG.Team2Barons, "
                                   "SG.Team1Towers, SG.Team2Towers, SG.Team1RiftHeralds, SG.Team2RiftHeralds, "
                                   "SG.RiotPlatformGameId, SG.RiotGameId",
                            where=f"(SG.DateTime_UTC >= '{str(date)}' AND SG.DateTime_UTC <= "
                                  f"'{str(date + dt.timedelta(hours=24*5))}') AND "
                                  f"(SG.Tournament = 'LCS 2022 Spring' OR SG.Tournament = 'LEC 2022 Spring' OR "
                                  f"SG.Tournament = 'LCS 2022 Lock In') AND (SG.Team1 = '{player_string}' "
                                  f"OR SG.Team2 = '{player_string}')"
                            )

    if response is None:
        return f"Wrong api-request."

    player_data = response.get('cargoquery')
    spread_string = ""
    players_list = []
    temp_sum = 0
    lec_players, lcs_players = open_spreadsheet(to_use=['lec_players', 'lcs_players'])
    if league == "lec":
        spread_string = 'F65:G124'
        players_list = lec_players.get(spread_string)
    elif league == "lcs":
        spread_string = 'F80:G155'
        players_list = lcs_players.get(spread_string)
    else:
        return f"wrong league String provided: {league}. \nAccepted strings are 'lec' and 'lcs'."

    for game_dict_key in player_data:
        game_dict = game_dict_key.get('title')
        if is_team:
            points = calc_points(game_dict, 'team', player_string)[0][0]
        else:
            points = calc_points(game_dict, 'player')[0][0]
        temp_sum += points

    old_points = 0.0

    for player in players_list:
        if player[0] == player_string:
            if type(player[1]) == str:
                old_points = player[1]
                player[1] = temp_sum
            else:
                old_points = player[1]
                player[1] = temp_sum
        elif type(player[1]) == str:
            player[1] = float(player[1].replace(',', '.'))
    return_string = f"updated points for Player/Team: {player_string} \nfrom {old_points} to {temp_sum}"
    print(return_string)
    if league == 'lec':
        lec_players.update(spread_string, players_list)
    elif league == 'lcs':
        lcs_players.update(spread_string, players_list)
    return return_string


def calc_points(game_dictionary, category='player', team=None):
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

        if team is not None and team == team2:
            sums = [(sum2, team2)]
            print(f"Punkte für {team2}: {sum2}")

        elif team is not None and team == team1:
            sums = [(sum1, team1)]
            print(f"Punkte für {team1}: {sum1}")

        else:
            sums = [(sum1, team1), (sum2, team2)]
            print(f"Punkte für {team1}: {sum1}")
            print(f"Punkte für {team2}: {sum2}")

    return sums


def update_spreadsheet_player_points(scores_to_update: [], league: str):
    lec_players, lcs_players = open_spreadsheet(to_use=['lec_players', 'lcs_players'])
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
        spread_string = 'F80:G155'
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
    spread_string_lcs = 'F80:H155'
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
    match_table = []
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
    return f"matchtable for Match-Week starting {match_week_date}: {match_table}"


def get_points_from_match_week_players(date_string):
    hour_string = "00:00:00"
    date_arr = [date_string, hour_string]
    date_time_string = ' '.join(date_arr)
    date = dt.datetime.strptime(convert_to_berlin_time(date_time_string), "%Y-%m-%d %H:%M:%S")

    site = mwclient.Site('lol.fandom.com', path='/')
    response = site.api('cargoquery',
                        limit="max",
                        tables="ScoreboardGames=SG, ScoreboardPlayers=SP",
                        join_on="SG.GameId=SP.GameId",
                        fields="SG.Tournament, SG.DateTime_UTC, SG.Team1, SG.Team2, SG.Winner, SG.Patch, "
                               "SP.Link, SP.Team, SP.Champion, SP.SummonerSpells, SP.KeystoneMastery, SP.KeystoneRune, "
                               "SP.Role, SP.UniqueGame, SP.Side, SP.Assists, SP.Kills, SP.Deaths, SP.CS",
                        where=f"SG.DateTime_UTC >= '{str(date)}' AND SG.DateTime_UTC <= "
                              f"'{str(date + dt.timedelta(hours=(24 * 5)))}' AND SG.Tournament = 'LCS 2022 Spring' OR "
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
    hour_string = "00:00:00"
    date_arr = [date_string, hour_string]
    date_time_string = ' '.join(date_arr)
    date = dt.datetime.strptime(convert_to_berlin_time(date_time_string), "%Y-%m-%d %H:%M:%S")

    site = mwclient.Site('lol.fandom.com', path='/')
    response = site.api('cargoquery',
                        limit="max",
                        tables="ScoreboardGames=SG",
                        fields="SG.Tournament, SG.DateTime_UTC, SG.Team1, SG.Team2, SG.Winner, SG.Patch, "
                               "SG.Team1Dragons, SG.Team2Dragons, SG.Team1Barons, SG.Team2Barons, SG.Team1Towers, "
                               "SG.Team2Towers, SG.RiotPlatformGameId, SG.RiotGameId",
                        where=f"SG.DateTime_UTC >= '{str(date)}' AND SG.DateTime_UTC <= "
                              f"'{str(date + dt.timedelta(hours=(24 * 5)))}' AND SG.Tournament = 'LCS 2022 Spring' OR "
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


def convert_to_berlin_time(date_string):
    date = dt.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
    date_string = str(date + dt.timedelta(hours=-1))
    return date_string


def check_if_game_was_updated_already(game_dictionary: dict, prev_matches_ws):
    team1 = game_dictionary.get('Team1') if type(game_dictionary.get('Team1')) == str else 0
    team2 = game_dictionary.get('Team2') if type(game_dictionary.get('Team2')) == str else 0
    team_arr = [team1, team2]
    date_string: str = game_dictionary.get('DateTime UTC')
    date = dt.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
    date_string = str(date + dt.timedelta(hours=1))
    date_string = date_string.split(' ')[0]
    prev_matches_size_string = 'E2'
    prev_matches_cells = prev_matches_ws.acell(prev_matches_size_string).value
    prev_matches = prev_matches_ws.get(prev_matches_cells)
    for match in prev_matches:
        match_team1 = match[0]
        match_team2 = match[1]
        match_date = match[2]
        if date_string == match_date and match_team1 in team_arr and match_team2 in team_arr:
            print(f"match {team_arr} at {date_string} was already updated")
            return True
    print(f"match {team_arr} at {date_string} was not already updated")
    return False


def add_match_to_prev_matches(game_dictionary=None, matches_to_add=None):
    # if check_if_game_was_updated_already(game_dictionary):
    #      return "Was already updated"

    prev_matches_size_string = 'E2'
    prev_matches_ws = open_spreadsheet(use_prev=True, only_use_prev=True)
    prev_matches_cells = prev_matches_ws.acell(prev_matches_size_string).value
    prev_matches = prev_matches_ws.get(prev_matches_cells)

    if matches_to_add is None:
        matches_to_add = []

    if game_dictionary is None and len(matches_to_add) > 0:
        for match_list in matches_to_add:
            prev_matches.append(match_list)
        return_string = f"updated prev matches and added {matches_to_add}"
        prev_matches_cells_split = prev_matches_cells.split('C')
        prev_matches_cells_split[-1] = str(int(prev_matches_cells_split[-1]) + len(matches_to_add))
        prev_matches_cells = 'C'.join(prev_matches_cells_split)

    elif game_dictionary is not None and len(matches_to_add) == 0:
        team1 = game_dictionary.get('Team1') if type(game_dictionary.get('Team1')) == str else 0
        team2 = game_dictionary.get('Team2') if type(game_dictionary.get('Team2')) == str else 0
        match_arr = [team1, team2]
        date_string: str = game_dictionary.get('DateTime UTC')
        date_string = date_string.split(' ')[0]
        match_arr.append(date_string)
        prev_matches.append(match_arr)
        return_string = f"updated prev matches and added {match_arr}"
        prev_matches_cells_split = prev_matches_cells.split('C')
        prev_matches_cells_split[-1] = str(int(prev_matches_cells_split[-1]) + 1)
        prev_matches_cells = 'C'.join(prev_matches_cells_split)

    else:
        return_string = "No matches to update supplied"
    prev_matches_ws.update(prev_matches_cells, prev_matches)
    prev_matches_ws.update(prev_matches_size_string, prev_matches_cells)
    print(return_string)
    return return_string


def get_game_stats(date_string: str, tournament: str):
    date = dt.datetime.strptime(date_string, "%Y-%m-%d").date()

    site = mwclient.Site('lol.fandom.com', path='/')
    # response = site.api('cargoquery',
    #                     limit="max",
    #                     tables="ScoreboardGames=SG",
    #                     fields="SG.Tournament, SG.DateTime_UTC, SG.Team1, SG.Team2, SG.Winner, SG.Patch, "
    #                            "SG.Team1Dragons, SG.Team2Dragons, SG.Team1Barons, SG.Team2Barons, SG.Team1Towers, "
    #                            "SG.Team2Towers, SG.RiotPlatformGameId, SG.RiotGameId",
    #                     where=f"SG.DateTime_UTC >= '{str(date)} 00:00:00' AND SG.DateTime_UTC <= "
    #                           f"'{str(date + dt.timedelta(1))} 00:00:00' AND SG.Tournament = '{tournament}' "
    #                     )
    # response = site.api('cargoquery',
    #                     limit="max",
    #                     tables="ScoreboardGames=SG, ScoreboardPlayers=SP",
    #                     join_on="SG.GameId=SP.GameId",
    #                     fields="SG.Tournament, SG.DateTime_UTC, SG.Team1, SG.Team2, SG.Winner, SG.Patch, "
    #                            "SP.Link, SP.Team, SP.Champion, SP.SummonerSpells, SP.KeystoneMastery, SP.KeystoneRune, "
    #                            "SP.Role, SP.UniqueGame, SP.Side, SP.Assists, SP.Kills, SP.Deaths, SP.CS",
    #                     where=f"SG.DateTime_UTC >= '{str(date)} 00:00:00' AND SG.DateTime_UTC <= "
    #                           f"'{str(date + dt.timedelta(hours=(24*5)))} 00:00:00' AND SG.Tournament = 'LCS 2022 Spring' OR "
    #                           f"SG.Tournament = 'LEC 2022 Spring' OR SG.Tournament = 'LCS 2022 Lock In'"
    #                     )

    response = site.api('cargoquery',
                        limit="max",
                        tables="ScoreboardGames=SG, ScoreboardPlayers=SP",
                        join_on="SG.GameId=SP.GameId",
                        fields="SG.Tournament, SG.DateTime_UTC, SG.Team1, SG.Team2, SG.Winner, "
                               "SG.Patch, SG.Team1Dragons, SG.Team2Dragons, SG.Team1Barons, "
                               "SG.Team2Barons, SG.Team1Towers, SG.Team2Towers, SG.RiotPlatformGameId, "
                               "SP.Link, SP.Team, SP.Champion, SP.SummonerSpells, SP.KeystoneMastery, "
                               "SP.KeystoneRune, SP.Role, SP.UniqueGame, SP.Side, SP.Assists, SP.Kills, "
                               "SP.Deaths, SP.CS",
                        where=f"SG.DateTime_UTC >= '{str(date)}' AND SG.DateTime_UTC <= "
                              f"'{str(date + dt.timedelta(1))}' AND SG.Tournament = '{tournament}' "
                        )
    data = response.get('cargoquery')
    for game_dict in data:
        was_updated = add_match_to_prev_matches(game_dict.get('title'))
        print(was_updated)
    print(data)

# get_game_stats_and_update_spread("2022-01-16", "LEC 2022 Spring", get_teams=True, get_players=True)

# update_points_for_matchup("2022-01-14", "W1")

# get_game_stats("2022-01-14", "LCS 2022 Lock In")

# get_points_from_match_week_teams("2022-01-14")

# get_points_from_match_week_players("2022-01-14")

# update_single_player_points_for_week('Vulcan (Philippe Laflamme)', '2022-01-14', 'lcs')
