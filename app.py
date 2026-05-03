from flask import Flask, render_template, request, redirect
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
    conn = get_db_connection()
    
    heroes = conn.execute(
    
    """
    SELECT 
        heroes.id AS hero_id,
        heroes.hero_name,
        heroes.image,
        heroes.civilian_name,
        heroes.description AS hero_description,
        powers.power_name,
        powers.power_description
        
    FROM heroes
    LEFT JOIN hero_powers ON heroes.id = hero_powers.hero_id
    LEFT JOIN powers ON hero_powers.power_id = powers.id
    """
    ).fetchall()
    
    heroes_dict = {}
    
    for hero in heroes:
        hero_id = hero["hero_id"]
        
        if hero_id not in heroes_dict:
            heroes_dict[hero_id] = {
                "hero_name": hero["hero_name"],
                "image": hero["image"],
                "hero_description": hero["hero_description"],
                "civilian_name": hero["civilian_name"],
                "powers": []
            }
            
        if hero["power_name"]:
            heroes_dict[hero_id]["powers"].append({
                "name": hero["power_name"],
                "description": hero["power_description"]
            })
            
    heroes = list(heroes_dict.values())
    
    return render_template("index.html", heroes=heroes)

@app.route("/reviews")
def reviews():
    conn = get_db_connection()
    reviews = conn.execute("""
        SELECT 
            reviews.*,
            heroes.hero_name
        FROM reviews
        LEFT JOIN heroes ON reviews.hero_id = heroes.id
    """).fetchall()
    
    conn.close()
    
    return render_template("review.html", reviews=reviews)

@app.route("/addreview", methods=["GET", "POST"])
def addreview():
    conn = get_db_connection()
    
    if request.method == "POST":
        title = request.form.get("title")
        text = request.form.get("review_text")
        rating = request.form.get("rating")
        hero_id = request.form.get("hero_id")

        conn.execute(
            "INSERT INTO reviews (title, review_text, rating, hero_id) VALUES (?, ?, ?, ?)",
            (title, text, rating, hero_id)
        )
        conn.commit()
        conn.close()

        return redirect("/reviews")

    heroes = conn.execute("SELECT id, hero_name FROM heroes").fetchall()
    conn.close()

    return render_template("addreview.html", heroes=heroes)

@app.route("/edit_review/<int:id>")
def edit_review(id):
    conn = get_db_connection()
    
    review = conn.execute(
        "SELECT * FROM reviews WHERE id = ?", (id,)
    ).fetchone()

    heroes = conn.execute(
        "SELECT id, hero_name FROM heroes"
    ).fetchall()

    conn.close()

    return render_template("edit_review.html", review=review, heroes=heroes)

@app.route("/update_review/<int:id>", methods=["POST"])
def update_review(id):
    title = request.form["title"]
    text = request.form["review_text"]
    rating = request.form["rating"]
    hero_id = request.form.get("hero_id")

    conn = get_db_connection()
    conn.execute(
        "UPDATE reviews SET title=?, review_text=?, rating=?, hero_id=? WHERE id=?",
        (title, text, rating, hero_id, id)
    )
    conn.commit()
    conn.close()

    return redirect("/reviews")

@app.route("/delete_review/<int:id>")
def delete_review(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM reviews WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return redirect("/reviews")

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