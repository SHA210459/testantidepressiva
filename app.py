from flask import Flask, redirect, url_for, render_template, g
from flask_login import LoginManager, login_required
from extensions import socketio
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
            host="localhost",
            user="root",
            database="antidepressiva"
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
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    if user_data:
        return User(id=user_data[0], username=user_data[1], color=user_data[3])
    return None

# Blueprints registrieren
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(main_bp, url_prefix='/')
app.register_blueprint(chat_bp, url_prefix='/chat')
app.register_blueprint(profile_bp, url_prefix='/profile')
app.register_blueprint(tippsbp, url_prefix='/tipps')

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

# Profilseite für eingeloggte Benutzer
@app.route('/profile/view')
@login_required
def view_profile():
    return render_template('profile.html')
