import sqlite3
from scipy.stats import rankdata
import numpy as np
import pandas as pd

def get_player_champ_data(db_name):
    conn = sqlite3.connect(db_name)
    player_champs = pd.read_sql("""select player_id, champion_id,
    								totalSessionsplayed from players_stats""", conn)

    player_champs = player_champs.pivot(index='player_id', columns='champion_id',
                                        values='totalSessionsPlayed')
    conn.close()

    return player_champs.div(player_champs[0], axis='index')

def rank_dist_df(dframe, index, profile):
    ranked = rankdata(-dframe.loc[index], method='max')
    mysum = 0
    for i, k in enumerate(profile):
        pos = np.where(dframe.columns == k)
        mysum += abs(i - ranked[pos]+1)
    return int(mysum)

def get_weights(dframe, profile, degree=1):
    return (pd.Series({i:rank_dist_df(dframe, i, profile) for i in dframe.index}, 
                      name='weights') + 10e-6)**degree

def normalize_df(dframe):
    return dframe.div(dframe.sum(axis=1), axis=0)

def get_pred(dframe, profile, degree=1):
    weights = get_weights(dframe, profile, degree)
    X = normalize_df(dframe.drop([0]+profile, axis=1))
    prod = X.mul(1/weights, axis=0)
    pred = prod.sum(axis=0).sort_values()
    return pred/sum(pred)

if __name__ == "__main__":
    DBNAME = 'lol.py'

    profile = [22,1]

    player_champs = get_player_champ_data(DBNAME)
    weights = get_weights(player, profile)
    preds = get_pred(player_champs, profile)
