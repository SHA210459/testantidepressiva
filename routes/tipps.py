import os
import mysql.connector
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

tippsbp = Blueprint('tipps', __name__)

# Datenbankverbindung
db = mysql.connector.connect(
    host=os.environ.get('MYSQL_HOST', 'db'),
    user=os.environ.get('MYSQL_USER', 'root'),
    password=os.environ.get('MYSQL_PASSWORD', 'password'),
    database=os.environ.get('MYSQL_DATABASE', 'antidepressiva')
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
