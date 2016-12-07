from flask import Flask, render_template, request, url_for
from recommend import *
DBNAME = 'lol.db'
app = Flask(__name__)

player_champs = get_player_champ_data(DBNAME)

@app.route('/', methods=['GET', 'POST'])
def load_pred():

    return render_template('index.html')


@app.route('/load_table', methods=['GET', 'POST'])
def load_table():
    degree = request.form.get('degree')
    profile = request.form.getlist('item[]')
    print(degree)
    #if not profile:
    #    profile = [22,13]
    if not degree:
    	degree = 10
    profile = [int(p) for p in profile]
    degree = int(degree)/10
    print(profile)
    print(degree)

    preds = get_pred(player_champs, profile, degree)
    return render_template('table.html', list1=profile, list2=preds.index)

if __name__ == "__main__":
    app.run(debug=True)

