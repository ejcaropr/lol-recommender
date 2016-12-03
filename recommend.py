import sqlite3
import pandas as pd
import numpy as np

conn = sqlite3.connect('lol.db')

player_champs = pandas.read_sql("""select player_id, champion_id,
								totalSessionsplayed from players_stats""", conn)

player_champs = player_champs.pivot(index='player_id', columns='champion_id', values='totalSessionsPlayed')
player_champs = player_champs.div(player_champs[0], axis='index')


