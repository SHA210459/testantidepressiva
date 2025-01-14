from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, db

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
            flash("Login erfolgreich!", "success")
            return redirect(url_for('main.home'))
        else:
            flash('Ungültiger Benutzername oder Passwort', 'error')

    return render_template("login.html")
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        color = request.form.get('color', '#ff6600')  # Standardfarbe verwenden, falls nicht gesetzt

        # Überprüfen, ob der Benutzername bereits existiert
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user_data = cursor.fetchone()
        cursor.close()

        if user_data:
            flash("Benutzername bereits vergeben!", "error")
            return redirect(url_for('auth.register'))

        # Passwort hashen und neuen Benutzer hinzufügen
        hashed_password = generate_password_hash(password)
        profile_image = 'static/profile_images/default_profile_image.png'  # Standardbild
        role = 'user'  # Rolle automatisch auf 'user' setzen

        cursor = db.cursor()
        cursor.execute("INSERT INTO users (username, password, color, profile_image, role) VALUES (%s, %s, %s, %s, %s)",
                       (username, hashed_password, color, profile_image, role))
        db.commit()
        user_id = cursor.lastrowid
        cursor.close()

        # Benutzer automatisch anmelden
        user = User(id=user_id, username=username, color=color, profile_image=profile_image)
        login_user(user)
        flash("Registrierung erfolgreich! Willkommen!", "success")
        return redirect(url_for('main.home'))

    return render_template('register.html')

    return render_template('register.html')
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Du hast dich erfolgreich abgemeldet.", "success")
    return redirect(url_for('auth.login'))
