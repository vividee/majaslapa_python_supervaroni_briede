from flask import Flask, render_template
import sqlite3
from pathlib import Path

app = Flask(__name__)

def get_db_connection():
    db = Path(__file__).parent / "database/database_sv_eb.db"  # kurai datubazei
    conn = sqlite3.connect(db)  # konekcija datubazie
    conn.row_factory = sqlite3.Row  # kā vārdnīca parādas
    return conn


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/powers")
def about():
    return render_template("powers.html")

@app.route("/teams")
def about():
    return render_template("teams.html")


@app.route("/merch")
def merch_index():
    conn = get_db_connection()  # piesledzies datubāzei

    merch = conn.execute(
        "SELECT * FROM merch"
    ).fetchall()  # izpilda sql vaicājumu, kas atalasa visus productus

    conn.close  # aizver savienojumu ar datubāzi

    return render_template("products.html", merch=merch)


@app.route("/products/<int:product_id>")
def products_show(product_id):
    conn = get_db_connection()

    product = conn.execute(
        """
        SELECT products.*, manufacturers.name AS manufacturer
        FROM products 
        LEFT JOIN manufacturers ON products.manufacturer_id = manufacturers.id
        WHERE products.id = ? 
        """,
        (product_id,),
    ).fetchone()

    conn.close()

    return render_template("products_show.html", product=product)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

if __name__=="__main__": 
    app.run(debug=True)