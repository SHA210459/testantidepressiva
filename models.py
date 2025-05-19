import os
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
import datetime

# MySQL Verbindung einrichten
db = mysql.connector.connect(
    host=os.environ.get('MYSQL_HOST', 'db'),
    user=os.environ.get('MYSQL_USER', 'root'),
    password=os.environ.get('MYSQL_PASSWORD', 'Rootroot1'),
    database=os.environ.get('MYSQL_DATABASE', 'antidepressiva')
)

class User(UserMixin):
    def __init__(self, id, username, color, profile_image=None, role='user', is_banned=False):
        self.id = id
        self.username = username
        self.color = color
        self.profile_image = profile_image  # Profilbild als Base64-String oder Dateipfad
        self.role = role  # Standardrolle auf 'user' setzen
        self.is_banned = is_banned

    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False, unique=True)
    color = Column(String(50))
    profile_image = Column(Text, default='/static/profile_pics/default_profile_image.png')  # Profilbild in Base64 oder als Dateipfad
    role = Column(String(20), default='user')  # Rolle als neue Spalte

    def is_admin(self):
        return self.role == 'admin'

    def toggle_ban(self):
        """Toggle the banned status of the user"""
        from app import get_db
        db = get_db()
        cursor = db.cursor()
        # Toggle the ban status
        new_banned_status = not self.is_banned
        cursor.execute("UPDATE users SET is_banned = %s WHERE id = %s",
                      (new_banned_status, self.id))
        db.commit()
        cursor.close()

        # Lokale Instanz aktualisieren
        self.is_banned = new_banned_status

        # Neuen Status zurückgeben
        return new_banned_status

    def is_banned(self):
        return self.is_banned

    def is_muted(self):
        """Prüfen, ob der Benutzer aktuell stummgeschaltet ist."""
        if self.muted_until:
            return datetime.datetime.now() < self.muted_until
        return False

    def get_id(self):
        """Gibt die Benutzer-ID zurück (für Flask-Login)."""
        return str(self.id)

    @staticmethod
    def get_by_id(user_id):
        from app import get_db
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
                profile_image=user_data['profile_image'],
                role=user_data.get('role', 'user'),
                is_banned=user_data.get('is_banned', False)
            )
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

    @staticmethod
    def update_profile(user_id, username, color, password=None, profile_image=None):
        """Aktualisiert das Benutzerprofil"""
        from app import get_db
        db = get_db()
        cursor = db.cursor()

        # Grundlegende Update-Abfrage
        query = "UPDATE users SET username = %s, color = %s"
        params = [username, color]

        # Wenn ein neues Passwort gesetzt werden soll
        if password and password.strip():
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            query += ", password = %s"
            params.append(hashed_password)

        # Wenn ein neues Profilbild gesetzt werden soll
        if profile_image:
            query += ", profile_image = %s"
            params.append(profile_image)

        # WHERE-Klausel hinzufügen
        query += " WHERE id = %s"
        params.append(user_id)

        cursor.execute(query, tuple(params))
        db.commit()
        cursor.close()
        return True

def get_db():
    """Establish and return a database connection."""
    return mysql.connector.connect(
        host=os.environ.get('MYSQL_HOST', 'db'),
        user=os.environ.get('MYSQL_USER', 'root'),
        password=os.environ.get('MYSQL_PASSWORD', 'password'),
        database=os.environ.get('MYSQL_DATABASE', 'antidepressiva')
    )

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


def create_chat_tables():
    cursor = db.cursor()

    # Tabelle für private Nachrichten
    create_private_messages_table = """
    CREATE TABLE IF NOT EXISTS private_messages (
        id INT AUTO_INCREMENT PRIMARY KEY,
        sender_id INT NOT NULL,
        receiver_id INT NOT NULL,
        message TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_read BOOLEAN DEFAULT FALSE,
        FOREIGN KEY (sender_id) REFERENCES users(id),
        FOREIGN KEY (receiver_id) REFERENCES users(id)
    );
    """

    # Tabelle für Chat-Sitzungen (optional, für erweiterte Funktionalität)
    create_chat_sessions_table = """
    CREATE TABLE IF NOT EXISTS chat_sessions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user1_id INT NOT NULL,
        user2_id INT NOT NULL,
        last_message_id INT,
        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user1_id) REFERENCES users(id),
        FOREIGN KEY (user2_id) REFERENCES users(id),
        FOREIGN KEY (last_message_id) REFERENCES private_messages(id),
        UNIQUE KEY unique_chat_pair (user1_id, user2_id)
    );
    """

    cursor.execute(create_private_messages_table)
    cursor.execute(create_chat_sessions_table)
    db.commit()
    cursor.close()
    print("Chat-Tabellen wurden erfolgreich erstellt.")


class PrivateMessage:
    def __init__(self, id, sender_id, receiver_id, message, timestamp, is_read=False):
        self.id = id
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.message = message
        self.timestamp = timestamp
        self.is_read = is_read

    @staticmethod
    def send_message(sender_id, receiver_id, message):
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO private_messages (sender_id, receiver_id, message) VALUES (%s, %s, %s)",
            (sender_id, receiver_id, message)
        )
        db.commit()
        message_id = cursor.lastrowid

        # Chat-Session aktualisieren oder erstellen
        user1, user2 = sorted([sender_id, receiver_id])
        cursor.execute("""
            INSERT INTO chat_sessions (user1_id, user2_id, last_message_id) 
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            last_message_id = VALUES(last_message_id),
            last_activity = CURRENT_TIMESTAMP
        """, (user1, user2, message_id))

        db.commit()
        cursor.close()
        return message_id

    @staticmethod
    def get_conversation(user1_id, user2_id):
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM private_messages 
            WHERE (sender_id = %s AND receiver_id = %s)
            OR (sender_id = %s AND receiver_id = %s)
            ORDER BY timestamp ASC
        """, (user1_id, user2_id, user2_id, user1_id))
        messages = cursor.fetchall()
        cursor.close()
        return [PrivateMessage(**msg) for msg in messages]

    @staticmethod
    def get_chat_partners(user_id):
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT u.id, u.username, u.profile_image, 
                   MAX(pm.timestamp) as last_message_time
            FROM users u
            JOIN private_messages pm ON (u.id = pm.sender_id OR u.id = pm.receiver_id)
            WHERE (pm.sender_id = %s OR pm.receiver_id = %s) AND u.id != %s
            GROUP BY u.id
            ORDER BY last_message_time DESC
        """, (user_id, user_id, user_id))
        partners = cursor.fetchall()
        cursor.close()
        return partners

    @staticmethod
    def mark_as_read(message_ids):
        if not message_ids:
            return
        cursor = db.cursor()
        format_strings = ','.join(['%s'] * len(message_ids))
        cursor.execute(
            f"UPDATE private_messages SET is_read = TRUE WHERE id IN ({format_strings})",
            tuple(message_ids)
        )
        db.commit()
        cursor.close()


# Tabellen erstellen
create_tables()
create_tips_table()
create_chat_tables()  # Neue Funktion aufrufen
