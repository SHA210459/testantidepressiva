from flask import Flask, redirect, url_for, render_template
from flask_login import LoginManager, login_required
from extensions import socketio  # Importiere das SocketIO-Objekt
from routes.chat import chat_bp
from routes.auth import auth_bp
from routes.main import main_bp
from routes.profile import profile_bp  # Profil-Blueprint importieren
from routes.tipps import tippsbp
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from models import User  # Stelle sicher, dass du das User-Modell hast

# Flask-Anwendung erstellen
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Wähle hier einen sicheren geheimen Schlüssel

# Flask-Login Konfiguration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Blueprints registrieren
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(main_bp, url_prefix='/')
app.register_blueprint(chat_bp, url_prefix='/chat')
app.register_blueprint(profile_bp, url_prefix='/profile')  # Profil-Blueprint registrieren
app.register_blueprint(tippsbp, url_prefix='/tipps')  # Tipp-Blueprint registrieren


# SocketIO initialisieren
socketio.init_app(app)

# MySQL Verbindung einrichten (optional für user_loader, wenn du MySQL verwendest)
db = mysql.connector.connect(
    host="localhost",
    user="root",
    database="antidepressiva"
)

# User Loader für Flask-Login
@login_manager.user_loader
def load_user(user_id):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    if user_data:
        return User(id=user_data[0], username=user_data[1], color=user_data[3])  # Benutzerobjekt zurückgeben
    return None


# Fehlerbehandlung (optional, aber hilfreich)
@app.errorhandler(404)
def page_not_found(error):
    return "Seite nicht gefunden!", 404


# Fehlerbehandlung für interne Serverfehler (optional)
@app.errorhandler(500)
def internal_server_error(error):
    return "Es gab ein Problem auf dem Server.", 500


# Hauptroute
@app.route('/')
def index():
    return redirect(url_for('main.home'))  # 'main.home' für Blueprint-Endpunkt

# Startseite der Anwendung (nach Login)
@app.route('/home')
@login_required
def home():
    return render_template('home.html')  # Dies könnte deine Hauptansichtsseite nach dem Login sein


# Profilseite für eingeloggte Benutzer
@app.route('/profile/view')
@login_required
def view_profile():
    return render_template('profile.html')
