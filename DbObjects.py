import mariadb


class DbObject:
    def __init__(self):
        self.id = None


class League(DbObject):
    def __init__(self):
        super().__init__()
        self.name = None


class Matchup(DbObject):
    def __init__(self):
        super().__init__()
        self.startDate = None
        self.weekId = None
        self.userId_1 = None
        self.userId_2 = None


class PlayerPoints(DbObject):
    def __init__(self):
        super().__init__()
        self.playerId = None
        self.week = None
        self.cs = None
        self.kills = None
        self.deaths = None
        self.assists = None
        self.doubleKills = None
        self.tripleKills = None
        self.quadraKills = None
        self.pentaKills = None
        self.firstBloods = None
        self.firstTowers = None
        self.towers = None
        self.drakes = None
        self.heralds = None
        self.barons = None
        self.wins = None
        self.quickWins = None
        self.souls = None
        self.drakeSteals = None
        self.soulSteals = None
        self.heraldSteals = None
        self.baronSteals = None


class Player(DbObject):
    def __init__(self):
        super().__init__()
        self.name = None
        self.userId = None
        self.leagueTeamId = None
        self.position = None
        self.laegueId = None


class PlayerTeam(DbObject):
    def __init__(self):
        super().__init__()
        self.name = None


class Trade(DbObject):
    def __init__(self):
        super().__init__()
        self.userId_1 = None
        self.userId_2 = None
        self.playerId_1 = None
        self.playerId_2 = None
        self.tradeTime = None


class User(DbObject):
    def __init__(self):
        super().__init__()
        self.name = None


class UserTeam(DbObject):
    def __init__(self):
        super().__init__()
        self.userId = None
        self.playerId_1 = None
        self.playerId_2 = None
        self.playerId_3 = None
        self.playerId_4 = None
        self.playerId_5 = None
        self.playerIdTeam = None
        self.playerIdSub = None
        self.playerIdReserve_1 = None
        self.playerIdReserve_2 = None
        self.playerIdReserve_3 = None


class Week(DbObject):
    def __init__(self):
        super().__init__()
