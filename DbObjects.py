import mariadb


class DbObject:
    def __init__(self):
        self.id = None


class League(DbObject):
    def __init__(self, name):
        super().__init__()
        self.name = None


class Matchup(DbObject):
    def __init__(self, start_date, week_id, user_id_1, user_id_2):
        super().__init__()
        self.startDate = start_date
        self.weekId = week_id
        self.userId_1 = user_id_1
        self.userId_2 = user_id_2


class PlayerPoints(DbObject):
    def __init__(self, player_id, week_id, cs, kills, deaths, assists, doubles, triples, quadras, pentas, fb, ft,
                 towers, drakes, heralds, barons, wins, qwins, souls, drake_steals, soul_steals, herald_steals,
                 baron_steals):
        super().__init__()
        self.playerId = player_id
        self.week = week_id
        self.cs = cs
        self.kills = kills
        self.deaths = deaths
        self.assists = assists
        self.doubleKills = doubles
        self.tripleKills = triples
        self.quadraKills = quadras
        self.pentaKills = pentas
        self.firstBloods = fb
        self.firstTowers = ft
        self.towers = towers
        self.drakes = drakes
        self.heralds = heralds
        self.barons = barons
        self.wins = wins
        self.quickWins = qwins
        self.souls = souls
        self.drakeSteals = drake_steals
        self.soulSteals = soul_steals
        self.heraldSteals = herald_steals
        self.baronSteals = baron_steals


class Player(DbObject):
    def __init__(self, name, user_id, league_team_id, position, league_id):
        super().__init__()
        self.name = name
        self.userId = user_id
        self.leagueTeamId = league_team_id
        self.position = position
        self.leagueId = league_id


class PlayerTeam(DbObject):
    def __init__(self, name):
        super().__init__()
        self.name = name


class Trade(DbObject):
    def __init__(self, user_id_1, user_id_2, player_id_1, player_id_2, trade_time):
        super().__init__()
        self.userId_1 = user_id_1
        self.userId_2 = user_id_2
        self.playerId_1 = player_id_1
        self.playerId_2 = player_id_2
        self.tradeTime = trade_time


class User(DbObject):
    def __init__(self, name):
        super().__init__()
        self.name = name


class UserTeam(DbObject):
    def __init__(self, user_id, player_id_1, player_id_2, player_id_3, player_id_4, player_id_5, player_id_6,
                 player_id_7, player_id_8, player_id_9, player_id_10):
        super().__init__()
        self.userId = user_id
        self.playerId_1 = player_id_1
        self.playerId_2 = player_id_2
        self.playerId_3 = player_id_3
        self.playerId_4 = player_id_4
        self.playerId_5 = player_id_5
        self.playerIdTeam = player_id_6
        self.playerIdSub = player_id_7
        self.playerIdReserve_1 = player_id_8
        self.playerIdReserve_2 = player_id_9
        self.playerIdReserve_3 = player_id_10


class Week(DbObject):
    def __init__(self):
        super().__init__()
