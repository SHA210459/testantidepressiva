-- Benutzer-Tabelle mit korrekten Feldern
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    color VARCHAR(7) DEFAULT '#000000',
    role VARCHAR(20) DEFAULT 'user',
    is_banned BOOLEAN DEFAULT FALSE,
    profile_image VARCHAR(255) DEFAULT 'profile_pics/default_profile_image.png'
);

-- Tabelle für Nachrichten
CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    content TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Tabelle für Tipps
CREATE TABLE IF NOT EXISTS tipps (
    tippsID INT AUTO_INCREMENT PRIMARY KEY,
    ueberschrift VARCHAR(255) NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Admin-Benutzer mit KORREKT formatiertem Hash erstellen
INSERT INTO users (username, password, role, color) 
VALUES ('admin', 'pbkdf2:sha256:150000$aCkiJqRs$5d0c151abb01272e83fb22e3b59c0ae1fc0bd9af89571304458218f8c2dae20a', 'admin', '#000000')
ON DUPLICATE KEY UPDATE role = 'admin';