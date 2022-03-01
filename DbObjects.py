import mariadb


class DbObject:
    def __init__(self, self_id=None):
        self.id = self_id


class League(DbObject):
    def __init__(self, self_id=None, name=None):
        super().__init__(self_id)
        self.name = name


class Matchup(DbObject):
    def __init__(self, self_id, start_date=None, week_id=None, user_id_1=None, user_id_2=None):
        super().__init__(self_id)
        self.startDate = start_date
        self.weekId = week_id
        self.userId_1 = user_id_1
        self.userId_2 = user_id_2


class PlayerPoints(DbObject):
    def __init__(self, self_id=None, player_id=None, week=None, cs=None, kills=None, deaths=None, assists=None,
                 double_kills=None, triple_kills=None, quadra_kills=None, penta_kills=None, first_bloods=None,
                 first_towers=None, towers=None, drakes=None, heralds=None, barons=None, wins=None, quick_wins=None,
                 souls=None, drake_steals=None, soul_steals=None, herald_steals=None, baron_steals=None):
        super().__init__(self_id)
        self.playerId = player_id
        self.week = week
        self.cs = cs
        self.kills = kills
        self.deaths = deaths
        self.assists = assists
        self.doubleKills = double_kills
        self.tripleKills = triple_kills
        self.quadraKills = quadra_kills
        self.pentaKills = penta_kills
        self.firstBloods = first_bloods
        self.firstTowers = first_towers
        self.towers = towers
        self.drakes = drakes
        self.heralds = heralds
        self.barons = barons
        self.wins = wins
        self.quickWins = quick_wins
        self.souls = souls
        self.drakeSteals = drake_steals
        self.soulSteals = soul_steals
        self.heraldSteals = herald_steals
        self.baronSteals = baron_steals


class Player(DbObject):
    def __init__(self, self_id, name=None, user_id=None, league_team_id=None, position=None, league_id=None):
        super().__init__(self_id)
        self.name = name
        self.userId = user_id
        self.leagueTeamId = league_team_id
        self.position = position
        self.leagueId = league_id


class PlayerTeam(DbObject):
    def __init__(self, self_id, name=None):
        super().__init__(self_id)
        self.name = name


class Trade(DbObject):
    def __init__(self, self_id, user_id_1=None, user_id_2=None, player_id_1=None, player_id_2=None, trade_time=None):
        super().__init__(self_id)
        self.userId_1 = user_id_1
        self.userId_2 = user_id_2
        self.playerId_1 = player_id_1
        self.playerId_2 = player_id_2
        self.tradeTime = trade_time


class User(DbObject):
    def __init__(self, self_id, name):
        super().__init__(self_id)
        self.name = name


class UserTeam(DbObject):
    def __init__(self, self_id, user_id, player_id_1=None, player_id_2=None, player_id_3=None, player_id_4=None, player_id_5=None,
                 player_id_6=None, player_id_7=None, player_id_8=None, player_id_9=None, player_id_10=None):
        super().__init__(self_id)
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
    def __init__(self, self_id, start_date=None, end_date=None):
        super().__init__(self_id)
        self.startDate = start_date
        self.endDate = end_date
