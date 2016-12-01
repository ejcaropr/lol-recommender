import sqlite3
import time
import requests

import secret_key

DBNAME = 'lol.db'
DEV_KEY = secret_key.DEV_KEY
REGION = "na"
API_Ver = "v1.2"
SNEAKY = 51405


base_url = {'static':"https://na.api.pvp.net/api/lol/static-data",
            'other': "https://na.api.pvp.net/api/lol"}

apis = {"summoner": "/".join([base_url['other'], REGION, "v1.4", "summoner/by-name"]),
        "champion": "/".join([base_url['static'], REGION, API_Ver, "champion"]),
        "master_league": "/".join([base_url['other'], REGION, "v2.5", "league/master"]),
        "challenger_league": "/".join([base_url['other'], REGION, "v2.5", "league/challenger"]),
        "stats": "/".join([base_url['other'], REGION, "v1.3", "stats/by-summoner/{summonerId}/summary"]),
        "stats_champ": "/".join([base_url['other'], REGION, "v1.3", "stats/by-summoner/{summonerId}/ranked"])}

params = {'api_key':DEV_KEY}

def api_url(api, static='static'):
    return "/".join([base_url[static], REGION, API_Ver, api])

def create_champion_db(db):
    conn = sqlite3.connect(db)
    tables = ['champions', 'spells', 'info', 'stats', 'tags']

    for table in tables:
        try:
            conn.execute('Drop table ' + table)
        except sqlite3.OperationalError:
            print('No '+ table +' to delete')

    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE champions (id integer primary key,
                                              name text)""")
    cursor.execute("""CREATE TABLE tags (champion_id integer, tag text,
                   priority integer,
                   FOREIGN KEY(champion_id) REFERENCES champions(id))""")

    cursor.execute("""CREATE TABLE info (champion_id integer, attack integer,
                   defense integer, difficulty integer, magic integer,
                   FOREIGN KEY(champion_id) REFERENCES champions(id))""")

    cursor.execute("""CREATE TABLE stats (champion_id integer,
                   attackspeedperlevel real, spellblock real, 
                   attackspeedoffset real, mpregen real, hpregen real,
                   critperlevel real, mp real, hpregenperlevel real,
                   hp real, attackdamage real, armor real, movespeed real,
                   attackdamageperlevel real, attackrange real, mpperlevel real,
                   armorperlevel real, spellblockperlevel real, mpregenperlevel real,
                   hpperlevel real, crit real,
                   FOREIGN KEY(champion_id) REFERENCES champions(id))""")

    conn.commit()

    return conn

def create_players_db(db):
    conn = sqlite3.connect(db)
    tables = ['players', 'players_stats']

    for table in tables:
        try:
            conn.execute('Drop table ' + table)
        except sqlite3.OperationalError:
            print('No '+ table +' to delete')

    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE players (player_id integer PRIMARY KEY,
                   losses integer, wins integer, isFreshBlood integer, isVeteran integer,
                   player_name text, division text, isHotStreak integer, isInactive integer,
                  leaguePoints integer, league text)""")

    cursor.execute("""CREATE TABLE players_stats (player_id integer, champion_id integer,
                   averageAssists integer, averageChampionsKilled integer,
                   averageCombatPlayerScore integer, averageNodeCapture integer,
                   averageNodeCaptureAssist integer, averageNodeNeutralize integer,
                   averageNodeNeutralizeAssist integer, averageNumDeaths integer,
                   averageObjectivePlayerScore integer, averageTeamObjective integer,
                   averageTotalPlayerScore integer, botGamesPlayed integer, killingSpree integer, 
                   maxAssists integer, maxChampionsKilled integer, maxCombatPlayerScore integer,
                   maxLargestCriticalStrike integer, maxLargestKillingSpree integer, 
                   maxNodeCapture integer, maxNodeCaptureAssist integer, maxNodeNeutralize integer,
                   maxNodeNeutralizeAssist integer, maxNumDeaths integer,
                   maxObjectivePlayerScore integer, maxTeamObjective integer, maxTimePlayed integer, 
                   maxTimeSpentLiving integer, maxTotalPlayerScore integer,
                   mostChampionKillsPerSession integer, mostSpellsCast integer, 
                   normalGamesPlayed integer, rankedPremadeGamesPlayed integer, 
                   rankedSoloGamesPlayed integer, totalAssists integer, totalChampionKills integer, 
                   totalDamageDealt integer, totalDamageTaken integer, totalDeathsPerSession integer,
                   totalDoubleKills integer, totalFirstBlood integer, totalGoldEarned integer, 
                   totalHeal integer, totalMagicDamageDealt integer, totalMinionKills integer, 
                   totalNeutralMinionsKilled integer, totalNodeCapture integer,
                   totalNodeNeutralize integer, totalPentaKills integer, 
                   totalPhysicalDamageDealt integer, totalQuadraKills integer, 
                   totalSessionsLost integer, totalSessionsPlayed integer, totalSessionsWon integer, 
                   totalTripleKills integer, totalTurretsKilled integer, totalUnrealKills integer,
                   FOREIGN KEY(player_id) REFERENCES players(player_id),
                   FOREIGN KEY(champion_id) REFERENCES champions(id))""")

    conn.commit()

    return conn

###Populate functions for tables ###################################

def populate_champions(conn, data):
    cursor = conn.cursor()
    for champ in data:
        add_champion(cursor, data[champ])
        add_tag(cursor, data[champ])
        add_info(cursor, data[champ])
        add_stats(cursor, data[champ])
    conn.commit()

def populate_players(conn, data):
    cursor = conn.cursor()
    for league in data:
        for player in data[league]:
            add_player(cursor, player, league)
    conn.commit()

def populate_players_stats(conn, pl_list):
    cursor = conn.cursor()
    for player in pl_list:
        pl_stats = get_player_stats(player)
        time.sleep(6/5) #limiting for api rate
        for champ in pl_stats:
            add_player_champ_stats(cursor, player, champ)
    conn.commit()

###Adder functions for records in each table ########################

def add_player(cursor, player, league):
    player_keys = ['playerOrTeamId',
                   'losses',
                   'wins',
                   'isFreshBlood',
                   'isVeteran',
                   'playerOrTeamName',
                   'division',
                   'isHotStreak',
                   'isInactive',
                   'leaguePoints']

    cursor.execute('INSERT INTO players VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                   [player[field] for field in player_keys] + [league])

def add_champion(cursor, champ):
    cursor.execute('INSERT INTO champions VALUES (?,?)',
                   [champ[field] for field in ['id', 'name']])

def add_tag(cursor, champ):
    for priority, tag in enumerate(champ['tags']):
        cursor.execute('INSERT INTO tags VALUES (?,?,?)',
                       [champ['id'], tag, priority+1])

def add_info(cursor, champ):
    cursor.execute('INSERT INTO info VALUES (?,?,?,?,?)',
                   [champ['id']] + [champ['info'][field] for
                                    field in ['attack', 'defense', 'difficulty', 'magic']])

def add_stats(cursor, champ):
    stat_keys = ['attackspeedperlevel',
                 'spellblock',
                 'attackspeedoffset',
                 'mpregen',
                 'hpregen',
                 'critperlevel',
                 'mp',
                 'hpregenperlevel',
                 'hp',
                 'attackdamage',
                 'armor',
                 'movespeed',
                 'attackdamageperlevel',
                 'attackrange',
                 'mpperlevel',
                 'armorperlevel',
                 'spellblockperlevel',
                 'mpregenperlevel',
                 'hpperlevel',
                 'crit']

    cursor.execute('INSERT INTO stats VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                   [champ['id']] + [champ['stats'][field] for field in stat_keys])

def add_player_champ_stats(cursor, player_id, champ):
    pl_stats_keys = ['averageAssists', 'averageChampionsKilled',
                     'averageCombatPlayerScore', 'averageNodeCapture',
                     'averageNodeCaptureAssist', 'averageNodeNeutralize',
                     'averageNodeNeutralizeAssist', 'averageNumDeaths',
                     'averageObjectivePlayerScore', 'averageTeamObjective',
                     'averageTotalPlayerScore', 'botGamesPlayed', 'killingSpree',
                     'maxAssists', 'maxChampionsKilled', 'maxCombatPlayerScore',
                     'maxLargestCriticalStrike', 'maxLargestKillingSpree',
                     'maxNodeCapture', 'maxNodeCaptureAssist', 'maxNodeNeutralize',
                     'maxNodeNeutralizeAssist', 'maxNumDeaths',
                     'maxObjectivePlayerScore', 'maxTeamObjective', 'maxTimePlayed',
                     'maxTimeSpentLiving', 'maxTotalPlayerScore',
                     'mostChampionKillsPerSession', 'mostSpellsCast',
                     'normalGamesPlayed', 'rankedPremadeGamesPlayed',
                     'rankedSoloGamesPlayed', 'totalAssists', 'totalChampionKills',
                     'totalDamageDealt', 'totalDamageTaken', 'totalDeathsPerSession',
                     'totalDoubleKills', 'totalFirstBlood', 'totalGoldEarned',
                     'totalHeal', 'totalMagicDamageDealt', 'totalMinionKills',
                     'totalNeutralMinionsKilled', 'totalNodeCapture',
                     'totalNodeNeutralize', 'totalPentaKills',
                     'totalPhysicalDamageDealt', 'totalQuadraKills',
                     'totalSessionsLost', 'totalSessionsPlayed', 'totalSessionsWon',
                     'totalTripleKills', 'totalTurretsKilled', 'totalUnrealKills']

    cursor.execute("""INSERT INTO players_stats VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,
                   ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
                   ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", [player_id, champ['id']]
                   + [champ['stats'].get(field) for field in pl_stats_keys])#56 + 2 values

### Getter functions to extract data from Riot api ##################

def get_champ_data():
    #global TOTAL_REQUESTS

    ch_params = params.copy()
    ch_params['champData'] = 'all'
    req = requests.get(apis['champion'], params=ch_params)

    #TOTAL_REQUESTS += 1
    #print("Total requests: {number}".format(number=TOTAL_REQUESTS))

    return req.json()['data']

def get_league_data(league='master'):
    #global TOTAL_REQUESTS

    pl_params = params.copy()
    pl_params['type'] = 'RANKED_SOLO_5x5'
    req = requests.get(apis[league + '_league'], params=pl_params)

    #TOTAL_REQUESTS += 1
    #print("Total requests: {number}".format(number=TOTAL_REQUESTS))

    return req.json()['entries']

def get_player_stats(summonerId):
    global TOTAL_REQUESTS

    req = requests.get(apis['stats_champ'].format(summonerId=summonerId), params=params)

    TOTAL_REQUESTS += 1
    print("Total requests: {number}".format(number=TOTAL_REQUESTS))

    return req.json()['champions']

def get_player_data():
    return {league:get_league_data(league) for league in ['master', 'challenger']}

### Query created tables so far #####################################

def get_players_list(conn):
    conn.row_factory = sqlite3.Row
    query = conn.execute('select player_id from players')
    return [r[0] for r in query]

### Main Code to create databases ###################################

if __name__ == "__main__":
    TOTAL_REQUESTS = 0
    myconn = create_champion_db(DBNAME)
    champ_data = get_champ_data()
    populate_champions(myconn, champ_data)

    myconn = create_players_db(DBNAME)
    pl_data = get_player_data()
    populate_players(myconn, pl_data)

    players = get_players_list(myconn)
    #n = 400
    #for i in range(0, len(pl_list), n):
    #    populate_players_stats(conn, pl_list[i:i+n])
    #    time.sleep()
    populate_players_stats(myconn, players)
