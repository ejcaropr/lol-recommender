import requests
import sqlite3

import secret_key

DBNAME = 'lol.db'
DEV_KEY = secret_key.DEV_KEY
REGION = "na"
API_Ver = "v1.2"

base_url = {'static':"https://na.api.pvp.net/api/lol/static-data",
            'other': "https://na.api.pvp.net/api/lol"}

apis = {"summoner": "/".join([base_url['other'], REGION, "/v1.4/summoner/by-name"]),
        "champion": "/".join([base_url['static'], REGION, "champion"])}
params = {'api_key':DEV_KEY}

def api_url(api, static='static'):
    return "/".join([base_url[static], REGION, API_Ver, api])

def create_db(db):
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

def add_champion(cursor, champ):
    cursor.execute('INSERT INTO champions VALUES (?,?)',
                   [champ[field] for field in ['id', 'name']])

def add_tag(cursor, champ):
    priority = 1
    for tag in champ['tags']:
        cursor.execute('INSERT INTO tags VALUES (?,?,?)',
                   [champ['id'],tag, priority])
        priority += 1

def add_info(cursor, champ):
    cursor.execute('INSERT INTO info VALUES (?,?,?,?,?)',
                   [champ['id']] + [champ['info'][field] for 
                                    field in ['attack', 'defense','difficulty', 'magic']])

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

def populate_champions(conn, data):
    cursor = conn.cursor()
    for champ in data:
        add_champion(cursor, data[champ])
        add_tag(cursor, data[champ])
        add_info(cursor, data[champ])
        add_stats(cursor, data[champ])
    conn.commit()


params['champData'] = 'all'
req = requests.get(apis['champion'], params = params)