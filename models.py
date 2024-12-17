import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# MySQL Verbindung einrichten
db = mysql.connector.connect(
    host="localhost",
    user="root",  # Dein MySQL-Benutzername
    database="antidepressiva"  # Dein MySQL-Datenbankname
)

# User Modell für Flask-Login
class User(UserMixin):
    def __init__(self, id, username, color):
        self.id = id
        self.username = username
        self.color = color

    @staticmethod
    def get_by_id(user_id):
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user_data = cursor.fetchone()
        cursor.close()
        if user_data:
            return User(id=user_data[0], username=user_data[1], color=user_data[3])
        return None

    @staticmethod
    def create_user(username, password, color):
        cursor = db.cursor()
        hashed_password = generate_password_hash(password)  # Passwort verschlüsseln
        cursor.execute(
            "INSERT INTO users (username, password, color) VALUES (%s, %s, %s)",
            (username, hashed_password, color)
        )
        db.commit()
        cursor.close()
        print(f"Benutzer {username} wurde erfolgreich erstellt.")

# Erstellen der `users`-Tabelle, falls sie noch nicht existiert
def create_tables():
    cursor = db.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(100) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        color VARCHAR(7) NOT NULL,  -- Farbe als HEX-Wert (z.B. #FFFFFF)
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
        text VARCHAR(255000) NOT NULL,  -- Der Text des Tipps
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
