import mwclient
import datetime as dt
import gspread
import pandas as pd
from gspread import worksheet

SPREADSHEET_NAME = "High Society Kranichfeld"
WEEKS = [("L", "18"), ("L", "22"), ("L", "26"), ("L", "30"), ("P", "18"),
         ("P", "22"), ("P", "26"), ("P", "30"), ("T", "18"), ("T", "22")]
SPREAD_STRING_BUILDER = ['F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S']


def inc_letter(letter: chr, increment_int) -> chr:
    return_val = chr(ord(letter) + increment_int)
    return return_val


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


def get_game_stats_and_update_spread(date_string: str, week_index: int, tournament: str, team1: str = None, team2: str = None,
                                     get_players=True, get_teams=True, prev_matches_ws=None):
    if not get_players and not get_teams:
        print("updating nothing")
        return "Updating nothing"
    hour_string = "00:00:00"
    date_arr = [date_string, hour_string]
    date_time_string = ' '.join(date_arr)
    date = dt.datetime.strptime(convert_to_berlin_time(date_time_string), "%Y-%m-%d %H:%M:%S")

    site = mwclient.Site('lol.fandom.com', path='/')
    if team1 == '' or team2 == '':
        if get_players:
            player_response = site.api('cargoquery',
                                       limit="max",
                                       tables="ScoreboardGames=SG, ScoreboardPlayers=SP",
                                       join_on="SG.GameId=SP.GameId",
                                       fields="SG.Tournament, SG.DateTime_UTC, SG.Team1, SG.Team2, SG.Winner, "
                                              "SG.Patch, SG.Team1Dragons, SG.Team2Dragons, SG.Team1Barons, "
                                              "SG.Team2Barons, SG.Team1Towers, SG.Team2Towers, SG.RiotPlatformGameId, "
                                              "SP.Link, SP.Team, SP.Champion, SP.SummonerSpells, SP.KeystoneMastery, "
                                              "SP.KeystoneRune, SP.Role, SP.Side, SP.Assists, SP.Kills, "
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
                                              "SP.KeystoneMastery, SP.KeystoneRune, SP.Role, "
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
                                            "SG.Team1Towers, SG.Team2Towers, SG.Team1RiftHeralds, SG.Team2RiftHeralds",
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
        update_spreadsheet_player_points(score_to_update, tournament, week_index)
        add_match_to_prev_matches(matches_to_add=games_to_add_to_sheet)
        return f"updated {score_to_update}"
    else:
        return f"Either didn't find any games or \nall games found through given arguments have already been updated."


def update_single_player_points_for_week(player_string: str, date_string: str, week_index: int,
                                         league: str, spreadsheets: [], is_team: bool = False, players_list=None,
                                         update_player_list: bool = True):
    hour_string = "00:00:00"
    date_arr = [date_string, hour_string]
    date_time_string = ' '.join(date_arr)
    date = dt.datetime.strptime(convert_to_berlin_time(date_time_string), "%Y-%m-%d %H:%M:%S")

    site = mwclient.Site('lol.fandom.com', path='/')

    response = None

    if not is_team:
        response = site.api('cargoquery',
                            limit="max",
                            tables="ScoreboardGames=SG, ScoreboardPlayers=SP",
                            join_on="SG.GameId=SP.GameId",
                            fields="SG.Tournament, SG.DateTime_UTC, SG.Team1, SG.Team2, SG.Winner, "
                                   "SG.Patch, SG.Team1Dragons, SG.Team2Dragons, SG.Team1Barons, "
                                   "SG.Team2Barons, SG.Team1Towers, SG.Team2Towers, SG.RiotPlatformGameId, "
                                   "SP.Link, SP.Team, SP.Champion, SP.SummonerSpells, SP.KeystoneMastery, "
                                   "SP.KeystoneRune, SP.Role, SP.Side, SP.Assists, SP.Kills, "
                                   "SP.Deaths, SP.CS",
                            where=f"(SG.DateTime_UTC >= '{str(date)}' AND SG.DateTime_UTC <= "
                                  f"'{str(date + dt.timedelta(hours=24*5))}') AND (SG.Tournament = 'LCS 2022 Spring' OR"
                                  f" SG.Tournament = 'LEC 2022 Spring' OR SG.Tournament = 'LCS 2022 Lock In' OR"
                                  f" SG.Tournament = 'LCS 2022 Spring Playoffs' OR"
                                  f" SG.Tournament = 'LEC 2022 Spring Playoffs') AND SP.Link = '{player_string}'"
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
                                  f"(SG.Tournament = 'LCS 2022 Spring' OR SG.Tournament = 'LEC 2022 Spring' OR"
                                  f" SG.Tournament = 'LCS 2022 Lock In' OR SG.Tournament = 'LCS 2022 Spring Playoffs'"
                                  f" OR SG.Tournament = 'LEC 2022 Spring Playoffs') AND (SG.Team1 = '{player_string}' "
                                  f"OR SG.Team2 = '{player_string}')"
                            )

    if response is None:
        return [f"Wrong api-request.", players_list]

    player_data = response.get('cargoquery')

    spread_string_builder_lec = ['65', '124']
    spread_string_builder_lcs = ['81', '156']

    spread_string_index = SPREAD_STRING_BUILDER[week_index]
    spread_string_lec = f"D{spread_string_builder_lec[0]}:{spread_string_index}{spread_string_builder_lec[1]}"
    spread_string_lcs = f"D{spread_string_builder_lcs[0]}:{spread_string_index}{spread_string_builder_lcs[1]}"

    spread_string = ""
    spread_string_update = ""
    temp_sum = 0
    games_played_so_far = len(player_data)
    if len(player_data) == 0 and not update_player_list:
        return_string = f"No New Games Found for {player_string}"
        return return_string, players_list

    lec_players, lcs_players = spreadsheets
    if players_list is None and league == "lec":
        lec_players: worksheet = lec_players
        spread_string = spread_string_lec
        players_list = lec_players.get(spread_string)
    elif players_list is None and league == "lcs":
        spread_string = spread_string_lcs
        players_list = lcs_players.get(spread_string)
    elif players_list is None:
        return f"wrong league String provided: {league}. \nAccepted strings are 'lec' and 'lcs'."

    for game_dict_key in player_data:
        game_dict = game_dict_key.get('title')
        if is_team:
            points = calc_points(game_dict, 'team', player_string)[0][0]
        else:
            points = calc_points(game_dict, 'player')[0][0]
        temp_sum += points

    if len(player_data) > 0:
        temp_sum = temp_sum/games_played_so_far*2
        temp_sum = float("{:.2f}".format(temp_sum))

    old_points = 0.0

    score_list_to_update = []

    for player in players_list:
        if player[0] == player_string:
            if type(player[-1]) == str:
                old_points = float(player[-1].replace(',', '.'))
                player[-1] = temp_sum
                score_list_to_update.append([temp_sum])
            else:
                old_points = float(player[-1])
                player[-1] = temp_sum
                score_list_to_update.append([temp_sum])
        else:
            if type(player[-1]) is str:
                score_list_to_update.append([float(player[-1].replace(',', '.'))])
            elif type(player[-1]) is float:
                score_list_to_update.append([player[-1]])
        if type(player[-1]) == str:
            player[-1] = float(player[-1].replace(',', '.'))

        for i in range(len(player)):
            if i == 0 or i == len(player) + 1:
                continue
            if type(player[i]) == str:
                player[i] = float(player[i].replace(',', '.'))

    if old_points != temp_sum:
        return_string = f"updated points for Player/Team: {player_string} \nfrom {old_points} to {temp_sum}"
    else:
        return_string = f"No New Games Found for {player_string}"
    print(return_string)
    if update_player_list and league == 'lec':
        spread_string_update = spread_string_lec.replace('D', spread_string_index)
        lec_players.update(spread_string_update, score_list_to_update)
    elif update_player_list and league == 'lcs':
        spread_string_update = spread_string_lcs.replace('D', spread_string_index)
        lcs_players.update(spread_string_update, score_list_to_update)
    # return return_string
    return [return_string, players_list]


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
        print(f"Punkte f??r {player}: {assists}+{kills}+{farm}{deaths} = {sum}")

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
            print(f"Punkte f??r {team2}: {sum2}")

        elif team is not None and team == team1:
            sums = [(sum1, team1)]
            print(f"Punkte f??r {team1}: {sum1}")

        else:
            sums = [(sum1, team1), (sum2, team2)]
            print(f"Punkte f??r {team1}: {sum1}")
            print(f"Punkte f??r {team2}: {sum2}")

    return sums


def update_spreadsheet_player_points(scores_to_update: [], league: str, week_index: int):
    lec_players, lcs_players = open_spreadsheet(to_use=['lec_players', 'lcs_players'])
    spread_string_builder_lec = ['65', '124']
    spread_string_builder_lcs = ['81', '156']

    if league == "LEC 2022 Spring":
        spread_string_index = SPREAD_STRING_BUILDER[week_index]
        spread_string = f'D{spread_string_builder_lec[0]}:{spread_string_index}{spread_string_builder_lec[1]}'
        lec_players_list = lec_players.get(spread_string)
        for score, player_string in scores_to_update:
            for player in lec_players_list:
                if player[0] == player_string:
                    if type(player[-1]) == str:
                        player[-1] = float(player[-1].replace(',', '.')) + score
                    else:
                        player[-1] = float(player[-1]) + score
                elif type(player[-1]) == str:
                    player[-1] = float(player[-1].replace(',', '.'))

                for i in range(len(player)):
                    if i == 0 or i == len(player):
                        continue
                    if type(player[i]) == str:
                        player[i] = float(player[i].replace(',', '.'))

        lec_players.update(spread_string, lec_players_list)
    elif league == "LCS 2022 Lock In" or league == "LCS 2022 Spring":
        spread_string_index = SPREAD_STRING_BUILDER[week_index]
        spread_string = f'D{spread_string_builder_lcs[0]}:{spread_string_index}{spread_string_builder_lcs[1]}'
        lcs_players_list = lcs_players.get(spread_string)
        for score, player_string in scores_to_update:
            for player in lcs_players_list:
                if player[0] == player_string:
                    if type(player[-1]) == str:
                        player[-1] = float(player[-1].replace(',', '.')) + score
                    else:
                        player[-1] = float(player[-1]) + score
                elif type(player[-1]) == str:
                    player[-1] = float(player[-1].replace(',', '.'))
        lcs_players.update(spread_string, lcs_players_list)
    else:
        print("wrongly formatted league string!")


def grab_points_for_matchup(fantasy_hub, match_week_date, sel_week: str):
    match_table = []
    for letter, number in WEEKS:
        week_string = fantasy_hub.acell(f"{letter}{number}").value
        if week_string == sel_week:
            start_cell = f"{letter}{int(number) + 1}"
            end_cell = f"{inc_letter(letter, 3)}{int(number) + 3}"
            match_table = fantasy_hub.get(f"{start_cell}:{end_cell}")
            break
    return_string = generate_return_string_from_match_table(match_table, match_week_date)
    return return_string


def update_points_for_matchup(spreadsheets: [], match_week_date, sel_week: str, week_index: int):
    fantasy_hub, lec_players, lcs_players = spreadsheets

    spread_string_builder_lec = ['2', '61']
    spread_string_builder_lcs = ['2', '77']

    spread_string_index = SPREAD_STRING_BUILDER[week_index]
    spread_string_lec = f"A{spread_string_builder_lec[0]}:{spread_string_index}{spread_string_builder_lec[1]}"
    spread_string_lcs = f"A{spread_string_builder_lcs[0]}:{spread_string_index}{spread_string_builder_lcs[1]}"

    lec_players_list = lec_players.get(spread_string_lec)
    lcs_players_list = lcs_players.get(spread_string_lcs)

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

            for j in range(len(lec_players_list)):
                player_name = lec_players_list[j][0]
                player_full_score = lec_players_list[j][-1]
                if player_string == player_name:
                    temp_sum += float(player_full_score.replace(',', '.'))
                    break
            for j in range(len(lcs_players_list)):
                player_name = lcs_players_list[j][0]
                player_full_score = lcs_players_list[j][-1]
                if player_string == player_name:
                    temp_sum += float(player_full_score.replace(',', '.'))
                    break
        sums.append((f"{letter}3", temp_sum))
    # print(sums)
    sums_with_names = []
    match_table = []
    for coord, score in sums:
        name = fantasy_hub.acell(coord).value
        sums_with_names.append((name, score))
    for letter, number in WEEKS:
        week_string = fantasy_hub.acell(f"{letter}{number}").value
        if week_string == sel_week:
            start_cell_get = f"{inc_letter(letter, 0)}{int(number) + 1}"
            start_cell_set = f"{inc_letter(letter, 1)}{int(number) + 1}"
            end_cell_get = f"{inc_letter(letter, 3)}{int(number) + 3}"
            end_cell_set = f"{inc_letter(letter, 2)}{int(number) + 3}"
            match_table = fantasy_hub.get(f"{start_cell_get}:{end_cell_get}")
            for row in match_table:
                for name, score in sums_with_names:
                    if row[0] == name:
                        row[1] = score
                    elif row[3] == name:
                        row[2] = score
            # print(match_table)
            condensed_match_table = condense_match_table_no_names(match_table)
            fantasy_hub.update(f"{start_cell_set}:{end_cell_set}", condensed_match_table)
            break
    return_string = generate_return_string_from_match_table(match_table, match_week_date)
    return return_string


def condense_match_table_no_names(match_table: []):
    condensed_match_table = []
    for row in match_table:
        new_row = [row[1], row[2]]
        condensed_match_table.append(new_row)
    return condensed_match_table


def generate_return_string_from_match_table(match_table: [], match_week_date: str):
    return_string = f"Matchtable for Match-Week starting on {match_week_date}:\n\n"
    for row in match_table:
        if type(row[1]) is str or type(row[2]) is str:
            row[1] = float("{:.2f}".format(float(row[1].replace(',', '.'))))
            row[2] = float("{:.2f}".format(float(row[2].replace(',', '.'))))
        else:
            row[1] = float("{:.2f}".format(row[1]))
            row[2] = float("{:.2f}".format(row[2]))
        return_string += f"{row[0]} vs {row[3]} \n"
        return_string += f"{row[1]} Pkt : {row[2]} Pkt \n\n"
    return return_string


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
                               "SP.Role, SP.Side, SP.Assists, SP.Kills, SP.Deaths, SP.CS",
                        where=f"(SG.DateTime_UTC >= '{str(date)}' AND SG.DateTime_UTC <= "
                              f"'{str(date + dt.timedelta(hours=(24 * 5)))}') AND (SG.Tournament = 'LCS 2022 Spring' OR"
                              f" SG.Tournament = 'LEC 2022 Spring' OR SG.Tournament = 'LCS 2022 Lock In')"
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


def update_player_agency(ws: []):
    fantasy_hub, lec_players, lcs_players = ws
    players_of_players = []
    for i in range(0, 6):
        letter = chr(ord('M') + i)
        start_cell = letter + '3'
        end_cell = letter + '14'
        players = fantasy_hub.get(f"{start_cell}:{end_cell}")
        temp_players_of_players = [player for sublist in players for player in sublist]
        players_of_players.append(temp_players_of_players)
        print(temp_players_of_players)

    spread_string_builder_lec = ['2', '61']
    spread_string_builder_lcs = ['2', '77']

    spread_string_lec = f"A{spread_string_builder_lec[0]}:D{spread_string_builder_lec[1]}"
    spread_string_lcs = f"A{spread_string_builder_lcs[0]}:D{spread_string_builder_lcs[1]}"

    lec_players_list = lec_players.get(spread_string_lec)
    lcs_players_list = lcs_players.get(spread_string_lcs)

    lec_lcs_players_list = [lec_players_list, lcs_players_list]

    changed_agencies = ""

    for players_list in lec_lcs_players_list:
        for player in players_list:
            if player[0] in players_of_players[0]:
                if player[3] != players_of_players[0][0]:
                    changed_agencies += f"{player[0]} changed agency from {player[3]} to {players_of_players[0][0]}\n"
                    player[3] = players_of_players[0][0]
            elif player[0] in players_of_players[1]:
                if player[3] != players_of_players[1][0]:
                    changed_agencies += f"{player[0]} changed agency from {player[3]} to {players_of_players[1][0]}\n"
                    player[3] = players_of_players[1][0]
            elif player[0] in players_of_players[2]:
                if player[3] != players_of_players[2][0]:
                    changed_agencies += f"{player[0]} changed agency from {player[3]} to {players_of_players[2][0]}\n"
                    player[3] = players_of_players[2][0]
            elif player[0] in players_of_players[3]:
                if player[3] != players_of_players[3][0]:
                    changed_agencies += f"{player[0]} changed agency from {player[3]} to {players_of_players[3][0]}\n"
                    player[3] = players_of_players[3][0]
            elif player[0] in players_of_players[4]:
                if player[3] != players_of_players[4][0]:
                    changed_agencies += f"{player[0]} changed agency from {player[3]} to {players_of_players[4][0]}\n"
                    player[3] = players_of_players[4][0]
            elif player[0] in players_of_players[5]:
                if player[3] != players_of_players[5][0]:
                    changed_agencies += f"{player[0]} changed agency from {player[3]} to {players_of_players[5][0]}\n"
                    player[3] = players_of_players[5][0]
            else:
                player[3] = 'FA'

    lec_players.update(spread_string_lec, lec_lcs_players_list[0])
    lcs_players.update(spread_string_lcs, lec_lcs_players_list[1])

    return changed_agencies


def grab_player_and_points_for_user(ws: [], user, coordinates: str, week_index: int):
    fantasy_hub, lec_players, lcs_players = ws

    spread_string_builder_lec = ['2', '61']
    spread_string_builder_lcs = ['2', '77']

    spread_string_index = SPREAD_STRING_BUILDER[week_index]
    spread_string_lec = f"A{spread_string_builder_lec[0]}:{spread_string_index}{spread_string_builder_lec[1]}"
    spread_string_lcs = f"A{spread_string_builder_lcs[0]}:{spread_string_index}{spread_string_builder_lcs[1]}"

    lec_players_list = lec_players.get(spread_string_lec)
    lcs_players_list = lcs_players.get(spread_string_lcs)

    players_of_user = fantasy_hub.get(coordinates)
    res_arr = []
    temp_sum = 0

    for player in players_of_user:
        player_string = player[0]
        if players_of_user.index(player) < 2:
            res_arr.append(player_string)
            continue

        for j in range(len(lec_players_list)):
            player_name = lec_players_list[j][0]
            player_full_score = lec_players_list[j][-1]
            if player_string == player_name:
                res_arr.append([player, player_full_score])
                temp_sum += float(player_full_score.replace(',', '.'))
                break
        for j in range(len(lcs_players_list)):
            player_name = lcs_players_list[j][0]
            player_full_score = lcs_players_list[j][-1]
            if player_string == player_name:
                res_arr.append([player, player_full_score])
                temp_sum += float(player_full_score.replace(',', '.'))
                break
    res_arr.append(temp_sum)
    return generate_res_string_single_player_week(res_arr, user)


def generate_res_string_single_player_week(res_array: [], user) -> str:
    res_string = ""
    res_string += f"Current Points for {user} in the selected week:\n"
    res_string += f"{res_array[1]}\n\n"
    for player_part in res_array:
        if res_array.index(player_part) in [0, 1] or player_part is res_array[-1]:
            continue
        player, score = player_part
        res_string += f"{player[0]}: {score} Points.\n"
    res_string += f"\nCurrent sum-total for {user} is {res_array[-1]}\n"

    return res_string

def grab_current_standings(fantasy_hub):
    standing_coords = "V36:Y42"
    raw_standings_grab = fantasy_hub.get(standing_coords)
    raw_standings = raw_standings_grab[1:]
    converted_standings = []
    for row in raw_standings:
        temp_row = []
        for cell in row:
            try:
                cell = float(cell.replace(',', '.'))
                temp_row.append(cell)
            except ValueError as e:
                temp_row.append(cell)
                continue
        converted_standings.append(temp_row)
    raw_standings_colls = raw_standings_grab[0]
    standings_df = pd.DataFrame(converted_standings, columns=raw_standings_colls)
    standings = standings_df.sort_values([raw_standings_colls[2], raw_standings_colls[1]], ascending=[False, False])
    return_string = standings.to_string(index=False)
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
    #                            "SP.Role, SP.Side, SP.Assists, SP.Kills, SP.Deaths, SP.CS",
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
                               "SP.KeystoneRune, SP.Role, SP.Side, SP.Assists, SP.Kills, "
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
