import sqlite3
import pandas as pd
import numpy as np

from scipy.stats import rankdata

conn = sqlite3.connect('lol.db')

player_champs = pandas.read_sql("""select player_id, champion_id,
								totalSessionsplayed from players_stats""", conn)

player_champs = player_champs.pivot(index='player_id', columns='champion_id', values='totalSessionsPlayed')
player_champs = player_champs.div(player_champs[0], axis='index')

def compare_profile(profile):
#profile is dictionary with [0,1] for rated champions
	X = player_champs.loc[:,profile]
	row_filter = X.notnull().all(axis=1)
	X = X.loc[row_filter]

	profile_df = pd.DataFrame(profile, index=[0])

	return ((X - profile_df.values[0])**2).sum(axis=1)**0.5

def l2_dist(x,y):
	return ((x-y)**2).sum()

def rank_dist(list1, list2):
	mysum = 0
	for i,k in enumerate(list1):
		mysum += abs(i-list2.index(k))
	return mysum

def rank_dist_df(df, index, profile):
	ranked = rankdata(-df.loc[index],method='max')
	mysum = 0
	for i,k in enumerate(profile):
		pos = np.where(df.columns == k)
		mysum += abs(i - ranked[pos]+1)
	return int(mysum)

rank_dists = {i:rank_dist_df(player_champs,i,profile) for i in player_champs.index}

def normalize_df(df):
	return df.div(x.sum(axis=1), axis=0)