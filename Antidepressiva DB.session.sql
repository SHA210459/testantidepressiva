INSERT INTO users (
    id,
    username,
    password,
    color,
    profile_image,
    role,
    is_banned
  )
VALUES (
    id:int,
    'username:varchar',
    'password:varchar',
    'color:varchar',
    'profile_image:varchar',
    'role:varchar',
    'is_banned:tinyint'
  );-- Benutzer zum Admin machen
UPDATE users 
SET role = 'admin' 
WHERE username = 'sha210459';

-- Prüfen ob es funktioniert hat
SELECT username, role FROM users;