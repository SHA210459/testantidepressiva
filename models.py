import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Text

# MySQL Verbindung einrichten
db = mysql.connector.connect(
    host="localhost",
    user="root",  # Dein MySQL-Benutzername
    database="antidepressiva"  # Dein MySQL-Datenbankname
)

class User(UserMixin):
    def __init__(self, id, username, color, profile_image=None):
        self.id = id
        self.username = username
        self.color = color
        self.profile_image = profile_image  # Profilbild als Base64-String oder Dateipfad

    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False, unique=True)
    color = Column(String(50))
    profile_image = Column(Text, nullable=True)  # Profilbild in Base64 oder als Dateipfad

    def get_id(self):
        # Gibt die Benutzer-ID zurück (wird von Flask-Login benötigt)
        return str(self.id)

    # Methode zum Abrufen von Benutzerdaten nach ID
    @classmethod
    def get_by_id(cls, user_id):
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user_data = cursor.fetchone()
        cursor.close()
        if user_data:
            return cls(user_data[0], user_data[1], user_data[3], user_data[4])  # Beispiel: [id, username, password, color, profile_image]
        return None

    @staticmethod
    def create_user(username, password, color, profile_image=None):
        cursor = db.cursor()
        hashed_password = generate_password_hash(password)  # Passwort verschlüsseln
        if not profile_image:
            profile_image = "default_profile_image.png"  # Standard-Profilbild setzen
        cursor.execute(
            "INSERT INTO users (username, password, color, profile_image) VALUES (%s, %s, %s, %s)",
            (username, hashed_password, color, profile_image)
        )
        db.commit()
        cursor.close()
        print(f"Benutzer {username} wurde erfolgreich erstellt.")

    @staticmethod
    def update_profile(user_id, username, color, password=None, profile_image=None):
        cursor = db.cursor()
        update_fields = "username = %s, color = %s"
        values = [username, color]

        if password:
            hashed_password = generate_password_hash(password)
            update_fields += ", password = %s"
            values.append(hashed_password)

        if profile_image:
            update_fields += ", profile_image = %s"
            values.append(profile_image)

        values.append(user_id)
        query = f"UPDATE users SET {update_fields} WHERE id = %s"
        cursor.execute(query, values)
        db.commit()
        cursor.close()
        print(f"Profil von Benutzer {username} erfolgreich aktualisiert.")

def create_tables():
    cursor = db.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(100) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        color VARCHAR(7) NOT NULL,  -- Farbe als HEX-Wert (z.B. #FFFFFF)
        profile_image BLOB, -- Bild als Binärdaten
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    cursor.execute(create_table_query)
    db.commit()
    cursor.close()
    print("Tabelle 'users' wurde erfolgreich erstellt.")

# Erstellen der `tipps`-Tabelle, falls sie noch nicht existiert
def create_tips_table():
    cursor = db.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS tipps (
        tippsID INT AUTO_INCREMENT PRIMARY KEY,
        ueberschrift VARCHAR(255) NOT NULL,  -- Die Überschrift des Tipps
        text TEXT NOT NULL,  -- Der Text des Tipps
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    cursor.execute(create_table_query)
    db.commit()
    cursor.close()
    print("Tabelle 'tipps' wurde erfolgreich erstellt.")

# Aufruf der Funktionen zum Erstellen der Tabellen
create_tables()
create_tips_table()
