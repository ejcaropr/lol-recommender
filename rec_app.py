from flask import Flask, render_template, request
from recommend import *
DBNAME = 'lol.db'
app = Flask(__name__)

player_champs = get_player_champ_data(DBNAME)

@app.route('/', methods=['GET', 'POST'])
def load_pred():
#    if request.method == 'POST':
#        profile = request.values.getlist('results')
        #profile =[22,13]
#        print(profile)
#    else:
#        profile = []
    profile = request.form.getlist('profile[]')
    if not profile:
        profile = [22,13]
    print(profile)

    weights = get_weights(player_champs, profile)
    preds = get_pred(player_champs, profile)

    return render_template('index.html', list1=profile, list2=preds.index)