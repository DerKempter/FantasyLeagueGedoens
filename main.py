import mwclient
import time
import datetime as dt
from datetime import date, timedelta

date_temp = "2022-01-12"
date = dt.datetime.strptime(date_temp, "%Y-%m-%d").date()

site = mwclient.Site('lol.fandom.com', path='/')
response = site.api('cargoquery',
                    limit="max",
                    tables="ScoreboardGames=SG, ScoreboardPlayers=SP",
                    join_on="SG.GameId=SP.GameId",
                    fields="SG.Tournament, SG.DateTime_UTC, SG.Team1, SG.Team2, SG.Winner, SG.Patch, SP.Link, SP.Team, SP.Champion, SP.SummonerSpells, SP.KeystoneMastery, SP.KeystoneRune, SP.Role, SP.UniqueGame, SP.Side",
                    where="SG.DateTime_UTC >= '" + str(date) + " 00:00:00' AND SG.DateTime_UTC <= '" + str(date+dt.timedelta(1)) + " 00:00:00'"
                    )

data = response.get('cargoquery')
print(response)
