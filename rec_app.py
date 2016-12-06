from flask import Flask, render_template
from recommend import *
DBNAME = 'lol.db'
app = Flask(__name__)

@app.route('/')
def load_pred():
    profile = [22,13]

    player_champs = get_player_champ_data(DBNAME)
    weights = get_weights(player_champs, profile)
    preds = get_pred(player_champs, profile)


    return render_template('index.html', list1=profile, list2=preds.index)