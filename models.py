import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
import datetime

# MySQL Verbindung einrichten
db = mysql.connector.connect(
    host="localhost",
    user="root",  # Dein MySQL-Benutzername
    database="antidepressiva"  # Dein MySQL-Datenbankname
)

class User(UserMixin):
    def __init__(self, id, username, color, profile_image=None, role='user'):
        self.id = id
        self.username = username
        self.color = color
        self.profile_image = profile_image  # Profilbild als Base64-String oder Dateipfad
        self.role = role  # Standardrolle auf 'user' setzen

    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False, unique=True)
    color = Column(String(50))
    profile_image = Column(Text, default='/static/profile_pics/default_profile_image.png')  # Profilbild in Base64 oder als Dateipfad
    role = Column(String(20), default='user')  # Rolle als neue Spalte



    def is_muted(self):
        """Prüfen, ob der Benutzer aktuell stummgeschaltet ist."""
        if self.muted_until:
            return datetime.datetime.now() < self.muted_until
        return False

    def get_id(self):
        """Gibt die Benutzer-ID zurück (für Flask-Login)."""
        return str(self.id)

        # Die get_by_id-Methode anpassen, um die Rolle zu verarbeiten

    @classmethod
    def get_by_id(cls, user_id):
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user_data = cursor.fetchone()
        cursor.close()
        if user_data:
            # Stelle sicher, dass alle Attribute korrekt übergeben werden (einschließlich role)
            return cls(user_data[0], user_data[1], user_data[3], user_data[4],
                       user_data[5])  # [id, username, password, color, profile_image, role]
        return None

    @staticmethod
    def create_user(username, password, color, role="user", profile_image=None):
        """Neuen Benutzer erstellen."""
        cursor = db.cursor()
        hashed_password = generate_password_hash(password)
        if not profile_image:
            profile_image = "default_profile_image.png"
        cursor.execute(
            "INSERT INTO users (username, password, color, role, profile_image) VALUES (%s, %s, %s, %s, %s)",
            (username, hashed_password, color, role, profile_image)
        )
        db.commit()
        cursor.close()
        print(f"Benutzer {username} wurde erfolgreich erstellt.")

    @staticmethod
    def mute_user(user_id, duration_minutes):
        """Benutzer stummschalten."""
        muted_until = datetime.datetime.now() + datetime.timedelta(minutes=duration_minutes)
        cursor = db.cursor()
        cursor.execute("UPDATE users SET muted_until = %s WHERE id = %s", (muted_until, user_id))
        db.commit()
        cursor.close()
        print(f"Benutzer mit ID {user_id} wurde bis {muted_until} stummgeschaltet.")

    def update_profile(user_id, username, color, password, profile_image):
        cursor = db.cursor()
        update_query = "UPDATE users SET username = %s, color = %s, profile_image = %s"

        # Falls ein Passwort angegeben wurde, das Passwort auch aktualisieren
        if password:
            hashed_password = generate_password_hash(password)
            update_query += ", password = %s"
            cursor.execute(update_query + " WHERE id = %s", (username, color, profile_image, hashed_password, user_id))
        else:
            cursor.execute(update_query + " WHERE id = %s", (username, color, profile_image, user_id))

        db.commit()
        cursor.close()
# Tabellen für Benutzer erstellen
def create_tables():
    cursor = db.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(100) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        color VARCHAR(7) NOT NULL,
        role VARCHAR(10) NOT NULL DEFAULT 'user',  -- Rolle des Benutzers: 'user' oder 'admin'
        muted_until DATETIME DEFAULT NULL,  -- Zeitpunkt, bis zu dem der Benutzer stummgeschaltet ist
        profile_image BLOB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    cursor.execute(create_table_query)
    db.commit()
    cursor.close()
    print("Tabelle 'users' wurde erfolgreich erstellt.")

# Tipps-Tabelle erstellen
def create_tips_table():
    cursor = db.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS tipps (
        tippsID INT AUTO_INCREMENT PRIMARY KEY,
        ueberschrift VARCHAR(255) NOT NULL,
        text TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    cursor.execute(create_table_query)
    db.commit()
    cursor.close()
    print("Tabelle 'tipps' wurde erfolgreich erstellt.")

# Tabellen erstellen
create_tables()
create_tips_table()
