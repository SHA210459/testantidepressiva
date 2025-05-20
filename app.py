import os

from flask import Flask, redirect, url_for, render_template, g
from flask_login import LoginManager, login_required, current_user
from extensions import socketio
from routes.about_us import about_us_bp
from routes.admin import admin_bp
from routes.chat import chat_bp
from routes.auth import auth_bp
from routes.main import main_bp
from routes.profile import profile_bp
from routes.tipps import tippsbp
import mysql.connector
import secrets
from models import User

# Flask-Anwendung erstellen
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')

# Flask-Login Konfiguration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = "Bitte logge dich ein, um fortzufahren."
login_manager.login_message_category = "info"


# Datenbankverbindung pro Anfrage
def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host=os.environ.get('MYSQL_HOST', 'db'),
            user=os.environ.get('MYSQL_USER', 'root'),
            password=os.environ.get('MYSQL_PASSWORD', 'Rootroot1'),
            database=os.environ.get('MYSQL_DATABASE', 'antidepressiva')
        )
    return g.db


@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    if user_data:
        return User(
            id=user_data['id'],
            username=user_data['username'],
            color=user_data['color'],
            profile_image=user_data.get('profile_image'),
            role=user_data.get('role', 'user'),
            is_banned=user_data.get('is_banned', False)
        )
    return None


# Blueprints registrieren
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(main_bp, url_prefix='/')
app.register_blueprint(chat_bp, url_prefix='/chat')
app.register_blueprint(profile_bp, url_prefix='/profile')
app.register_blueprint(tippsbp, url_prefix='/tipps')
app.register_blueprint(about_us_bp, url_prefix='/about')
app.register_blueprint(admin_bp, url_prefix='/admin')

# SocketIO initialisieren
socketio.init_app(app, cors_allowed_origins="*")


# Fehlerbehandlung
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500


# Hauptroute
@app.route('/')
def index():
    return redirect(url_for('main.home'))


@app.route('/profile/view')
@login_required
def view_profile():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT username, color, profile_image FROM users WHERE id = %s", (current_user.id,))
    user_data = cursor.fetchone()
    cursor.close()

    # Profilbild als Base64-String aus der Datenbank laden
    profile_image = user_data['profile_image'] if user_data['profile_image'] else None

    return render_template('profile.html', user=user_data, profile_image=profile_image)


# Neue Route für private Chats
@app.route('/chat/private')
@login_required
def private_chats():
    # Hier kannst du die Logik für private Chats implementieren
    # Zum Beispiel: Liste der privaten Chats aus der Datenbank holen
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Beispiel: Holen aller privaten Nachrichten für den aktuellen Benutzer
    cursor.execute("""
        SELECT DISTINCT u.id, u.username, u.color, u.profile_image 
        FROM users u
        JOIN private_messages pm ON (u.id = pm.sender_id OR u.id = pm.receiver_id)
        WHERE (pm.sender_id = %s OR pm.receiver_id = %s) AND u.id != %s
    """, (current_user.id, current_user.id, current_user.id))

    chat_partners = cursor.fetchall()
    cursor.close()

    return render_template('private_chats.html', chat_partners=chat_partners)

