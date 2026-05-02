from flask import Flask, render_template
import sqlite3
from pathlib import Path


app = Flask(__name__)

def get_db_connection():
    db = Path(__file__).parent / "database/database_sv_ebb.db"  # kurai datubazei
    conn = sqlite3.connect(db)  # konekcija datubazie
    conn.row_factory = sqlite3.Row  # kā vārdnīca parādas
    return conn


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/powers")
def powers():
    return render_template("powers.html")

@app.route("/teams")
def teams_index():
    conn = get_db_connection()
    
    teams = conn.execute(
       """
        SELECT
            teams.id AS team_id,
            teams.team AS team_name,
            teams.site,
            teams.image,
            heroes.id AS hero_id,
            heroes.hero_name AS hero_name
        FROM teams
        LEFT JOIN hero_teams ON teams.id = hero_teams.team_id
        LEFT JOIN heroes ON hero_teams.hero_id = heroes.id
        ORDER BY teams.team
        """
    ).fetchall()
    
    teams_data = {}
    
    
    for team in teams:
        team_id = team["team_id"]
        if team_id not in teams_data:
            teams_data[team_id] = {
                "name": team["team_name"],
                "image": team["image"],
                "site": team["site"],
                "heroes": []
            }
        
        if team["hero_name"]:
            teams_data[team_id]["heroes"].append(team["hero_name"])
    
    return render_template("teams.html", teams=teams_data.values())


@app.route("/merch")
def merch_index():
    conn = get_db_connection()  # piesledzies datubāzei

    merch = conn.execute(
        "SELECT * FROM merch"
    ).fetchall()  # izpilda sql vaicājumu, kas atalasa visus productus

    conn.close()  # aizver savienojumu ar datubāzi

    return render_template("merch.html", merch=merch)


@app.route("/merch/<int:merch_id>")
def merch_show(merch_id):
    conn = get_db_connection()

    merch = conn.execute(
        """
        SELECT
            merch.*,
            heroes.hero_name AS hero_name,
            teams.team AS team_name
        FROM merch
        LEFT JOIN heroes ON merch.hero_id = heroes.id
        LEFT JOIN teams ON merch.team_id = teams.id
        WHERE merch.id = ?
        """,
        (merch_id,),
    ).fetchone()

    conn.close()

    return render_template("merch_show.html", merch=merch)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

if __name__=="__main__": 
    app.run(debug=True)