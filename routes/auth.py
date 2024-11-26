from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.datastructures import auth
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, db  # User aus der models.py importieren
from routes import main

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Benutzer aus der Datenbank abrufen
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user_data = cursor.fetchone()
        cursor.close()

        # Überprüfen, ob der Benutzer existiert und das Passwort stimmt
        if user_data and check_password_hash(user_data[2], password):
            user = User(id=user_data[0], username=user_data[1], color=user_data[3])
            login_user(user)
            return redirect(url_for('main.home'))  # Weiterleitung zur 'home' Route im 'main' Blueprint
        else:
            flash('Ungültiger Benutzername oder Passwort', 'error')

    return render_template("login.html")

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        color = request.form['color']

        # Überprüfen, ob der Benutzername bereits existiert
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user_data = cursor.fetchone()
        cursor.close()

        if user_data:
            flash("Benutzername bereits vergeben!", "error")
            return redirect(url_for('auth.register'))

        # Passwort hashen
        hashed_password = generate_password_hash(password)

        # Neuen Benutzer erstellen
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (username, password, color) VALUES (%s, %s, %s)", (username, hashed_password, color))
        db.commit()
        cursor.close()

        flash('Registrierung erfolgreich! Du kannst dich jetzt einloggen.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')  # Correct template for registration

@auth_bp.route('/logout')
def logout():
    logout_user()  # Logs the user out
    flash("Du hast dich erfolgreich abgemeldet.", "success")  # Optional flash message
    return redirect(url_for('auth.login'))  # Redirect to login page after logout
