from DbObjects import DbObject, League, Matchup, PlayerPoints, Player, PlayerTeam, Trade, User, UserTeam, Week


class DatabaseConverter:
    def __init__(self):
        self.last_obj_to_db = None
        self.last_db_to_obj = None

    def obj_to_db(self, obj: DbObject) -> []:
        if type(obj) is League:
            tar_list = [
                obj.id,
                obj.name
            ]

        elif type(obj) is Matchup:
            tar_list = [
                obj.id,
                obj.startDate,
                obj.weekId,
                obj.userId_1,
                obj.userId_2
            ]

        elif type(obj) is PlayerPoints:
            tar_list = [
                obj.id,
                obj.playerId,
                obj.week,
                obj.cs,
                obj.kills,
                obj.deaths,
                obj.assists,
                obj.doubleKills,
                obj.tripleKills,
                obj.quadraKills,
                obj.pentaKills,
                obj.firstBloods,
                obj.firstTowers,
                obj.towers,
                obj.drakes,
                obj.heralds,
                obj.barons,
                obj.wins,
                obj.quickWins,
                obj.souls,
                obj.drakeSteals,
                obj.soulSteals,
                obj.heraldSteals,
                obj.baronSteals
            ]

        elif type(obj) is Player:
            tar_list = [
                obj.id,
                obj.name,
                obj.userId,
                obj.leagueTeamId,
                obj.position,
                obj.leagueId
            ]

        elif type(obj) is PlayerTeam:
            tar_list = [
                obj.id,
                obj.name
            ]

        elif type(obj) is Trade:
            tar_list = [
                obj.id,
                obj.userId_1,
                obj.userId_2,
                obj.playerId_1,
                obj.playerId_2,
                obj.tradeTime
            ]

        elif type(obj) is User:
            tar_list = [
                obj.id,
                obj.name
            ]

        elif type(obj) is UserTeam:
            tar_list = [
                obj.id,
                obj.userId,
                obj.playerId_1,
                obj.playerId_2,
                obj.playerId_3,
                obj.playerId_4,
                obj.playerId_5,
                obj.playerIdTeam,
                obj.playerIdSub,
                obj.playerIdReserve_1,
                obj.playerIdReserve_2,
                obj.playerIdReserve_3
            ]

        elif type(obj) is Week:
            tar_list = [
                obj.id,
                obj.startDate,
                obj.endDate
            ]

        self.last_obj_to_db = tar_list

        return tar_list

    def db_to_obj(self, params: [], target_obj) -> DbObject:
        tar_obj = target_obj()

        if type(tar_obj) is League:
            tar_obj.id = params[0]
            tar_obj.name = params[1]

        elif type(tar_obj) is Matchup:
            tar_obj.id = params[0]
            tar_obj.startDate = params[1]
            tar_obj.weekId = params[2]
            tar_obj.userId_1 = params[3]
            tar_obj.userId_2 = params[4]

        elif type(tar_obj) is PlayerPoints:
            tar_obj.id = params[0]
            tar_obj.playerId = params[1]
            tar_obj.week = params[2]
            tar_obj.cs = params[3]
            tar_obj.kills = params[4]
            tar_obj.deaths = params[5]
            tar_obj.assists = params[6]
            tar_obj.doubleKills = params[7]
            tar_obj.tripleKills = params[8]
            tar_obj.quadraKills = params[9]
            tar_obj.pentaKills = params[10]
            tar_obj.firstBloods = params[11]
            tar_obj.firstTowers = params[12]
            tar_obj.towers = params[13]
            tar_obj.drakes = params[14]
            tar_obj.heralds = params[15]
            tar_obj.barons = params[16]
            tar_obj.wins = params[17]
            tar_obj.quickWins = params[18]
            tar_obj.souls = params[19]
            tar_obj.drakeSteals = params[20]
            tar_obj.soulSteals = params[21]
            tar_obj.heraldSteals = params[22]
            tar_obj.baronSteals = params[23]

        elif type(tar_obj) is Player:
            tar_obj.id = params[0]
            tar_obj.name = params[1]
            tar_obj.userId = params[2]
            tar_obj.leagueTeamId = params[3]
            tar_obj.position = params[4]
            tar_obj.leagueId = params[5]

        elif type(tar_obj) is PlayerTeam:
            tar_obj.id = params[0]
            tar_obj.name = params[1]

        elif type(tar_obj) is Trade:
            tar_obj.id = params[0]
            tar_obj.userId_1 = params[1]
            tar_obj.userId_2 = params[2]
            tar_obj.playerId_1 = params[3]
            tar_obj.playerId_2 = params[4]
            tar_obj.tradeTime = params[5]

        elif type(tar_obj) is User:
            tar_obj.id = params[0]
            tar_obj.name = params[1]

        elif type(tar_obj) is UserTeam:
            tar_obj.id = params[0]
            tar_obj.userId = params[1]
            tar_obj.playerId_1 = params[2]
            tar_obj.playerId_2 = params[3]
            tar_obj.playerId_3 = params[4]
            tar_obj.playerId_4 = params[5]
            tar_obj.playerId_5 = params[6]
            tar_obj.playerIdTeam = params[7]
            tar_obj.playerIdSub = params[8]
            tar_obj.playerIdReserve_1 = params[9]
            tar_obj.playerIdReserve_2 = params[10]
            tar_obj.playerIdReserve_3 = params[11]

        elif type(tar_obj) is Week:
            tar_obj.id = params[0]
            tar_obj.startDate = params[1]
            tar_obj.endDate = params[2]

        self.last_db_to_obj = tar_obj

        return tar_obj
