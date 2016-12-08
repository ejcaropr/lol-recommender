import sqlite3
from scipy.stats import rankdata
import numpy as np
import pandas as pd

def get_player_champ_data(db_name):
    """Return dictionary from database with player_id in each row and champion_id in
    each column.
    """
    conn = sqlite3.connect(db_name)
    player_champs = pd.read_sql("""select player_id, champion_id,
    							totalSessionsplayed from players_stats""", conn)

    player_champs = player_champs.pivot(index='player_id', columns='champion_id',
                                        values='totalSessionsPlayed')
    conn.close()

    return player_champs.div(player_champs[0], axis='index')

def get_champ_dict(db_name):
    """Return dictionary with champion and champion_id from database."""
    conn = sqlite3.connect(db_name)
    champ_dict = pd.read_sql("""select id, name from champions""", conn,
                             index_col='id')

    conn.close()

    return champ_dict

def rank_dist_df(dframe, index, profile):
    """Return rank distance: sum of diferrences in ranking between dframe
    and profile for a given index (player).

    profile: order of champions for which a distance will be computed
    dframe: contains a column for each champion and a row for each player
    index: player_id that is being compared to profile

    In case of tie, assigns to all elements the lowest ranking for which
    they are all tied.
    """
    ranked = rankdata(-dframe.loc[index], method='max')
    mysum = 0
    for i, k in enumerate(profile):
        pos = np.where(dframe.columns == k)
        mysum += abs(i - ranked[pos]+1)
    return int(mysum)

def get_weights(dframe, profile, degree=1):
    """Return rank distance for player's profile to each player in dframe.

    Optional parameter 'degree' increases the distances in exponential fashion
    giving less weight to those players farther from input profile.
    """
    return (pd.Series({i:rank_dist_df(dframe, i, profile) for i in dframe.index},
                      name='weights') + 10e-6)**degree

def normalize_df(dframe):
    """Set each row in dframe to sum to 1"""
    return dframe.div(dframe.sum(axis=1), axis=0)

def get_pred(dframe, profile, degree=1):
    """Return vector in which the average champ selection over all players
    is weighted by distance to each player.

    Optional parameter 'degree' increases the distances in exponential fashion
    giving less weight to those players farther from input profile.
    """
    weights = get_weights(dframe, profile, degree)

    #Drop 0 (total) and champions in profile
    X = normalize_df(dframe.drop([0]+profile, axis=1))

    #Multiply normalized matrix by inverse of weights
    prod = X.mul(1/weights, axis=0)

    #Sum all the rows after having the weights applied, this will give a total
    #per champion, normalized for number of players who played this champ
    pred = prod.sum(axis=0).div(prod.notnull().sum(axis=0))
    pred = pred.sort_values(ascending=False)
    return pred/sum(pred)

if __name__ == "__main__":
    DBNAME = 'lol.py'

    my_profile = [22, 1]

    player_champs = get_player_champ_data(DBNAME)
    weights = get_weights(player_champs, my_profile)
    preds = get_pred(player_champs, my_profile)
