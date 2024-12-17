from flask import Blueprint, render_template
import mysql.connector

# Blueprint für Tipps erstellen
tippsbp = Blueprint('tipps', __name__)

# MySQL-Verbindung einrichten
db = mysql.connector.connect(
    host="localhost",
    user="root",  # Dein MySQL-Benutzername
    password="",  # Dein MySQL-Passwort
    database="antidepressiva"  # Dein MySQL-Datenbankname
)


@tippsbp.route('/')
def show_tipps():
    try:
        # Verbindung zur Datenbank herstellen und Tipps abrufen
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT tippsID, text, created_at FROM tipps")
        tipps = cursor.fetchall()
        cursor.close()

        # Render die HTML-Seite mit den Tipps
        return render_template('tipps.html', tipps=tipps)
    except mysql.connector.Error as err:
        return f"Fehler beim Abrufen der Tipps: {err}"
