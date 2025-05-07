PREPARE stmt FROM 'INSERT INTO users (id, username, password, color, profile_image, role, is_banned) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)';
SET @id = 1;
SET @username = 'actual_username';
SET @password = 'actual_password';
SET @color = 'blue';
SET @profile_image = 'profile.jpg';
SET @role = 'user';
SET @is_banned = 0;
EXECUTE stmt USING @id, @username, @password, @color, @profile_image, @role, @is_banned;
DEALLOCATE PREPARE stmt;

-- Benutzer zum Admin machen
UPDATE users 
SET role = 'admin' 
WHERE username = 'sha210459';

-- Prüfen ob es funktioniert hat
SELECT username, role FROM users;