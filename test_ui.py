from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Starte den Chrome-Browser
driver = webdriver.Chrome()

# Lade deine Login-Seite
driver.get("http://127.0.0.1:5000/auth/login")
time.sleep(2)  # kurz warten, bis alles geladen ist

# Fülle Benutzername und Passwort aus
username_field = driver.find_element(By.ID, "username")
username_field.send_keys("deinBenutzername")  # <-- anpassen!

password_field = driver.find_element(By.ID, "password")
password_field.send_keys("deinPasswort")  # <-- anpassen!

# Klicke auf den Login-Button
login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
login_button.click()

# Warten und ggf. auf Erfolg prüfen
time.sleep(3)  # Warte auf die Weiterleitung nach dem Login
print("Nach dem Login befindest du dich auf dieser Seite:", driver.title, "--> Falls ich Recht habe, dann hast du dich erfolgreich eingeloggt und dein Zugriff auf die Seite lief prima!")
print("Um sicher zu sein findest du hier die URL deiner letzten Seite:", driver.current_url)

driver.quit()
