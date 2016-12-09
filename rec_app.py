from flask import Flask, render_template, request, url_for
import recommend as rec
DBNAME = 'lol.db'
app = Flask(__name__)

player_champs = rec.get_player_champ_data(DBNAME)
champ_dict = rec.get_champ_dict(DBNAME)

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

    preds = rec.get_pred(player_champs, profile, degree)

    profile = champ_dict.loc[profile, :]
    preds = champ_dict.loc[preds.index, :]

    return render_template('table.html', list1=profile.iterrows(), list2=preds.iterrows())

if __name__ == "__main__":
    app.run(debug=True)

