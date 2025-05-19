from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def test_login_and_profile_edit():
    driver = webdriver.Chrome()
    driver.maximize_window()

    try:
        # 1. Login-Seite öffnen
        driver.get("http://127.0.0.1:5000/auth/login")

        # 2. Login-Formular ausfüllen
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        driver.find_element(By.NAME, "username").send_keys("fff")
        driver.find_element(By.NAME, "password").send_keys("fff")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # 3. Warten, bis Login abgeschlossen (URL enthält /home)
        WebDriverWait(driver, 10).until(EC.url_contains("/home"))
        print("Login erfolgreich, aktuelle URL:", driver.current_url)

        # 4. Kurz warten, damit Session und alles stabil ist
        time.sleep(1)

        # 5. Profilseite öffnen
        driver.get("http://127.0.0.1:5000/profile/profile")

        # 6. Warten, bis das Formular auf der Profilseite geladen ist (z.B. Username-Feld sichtbar)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )

        # 7. Username ändern
        username_input = driver.find_element(By.ID, "username")
        username_input.clear()
        username_input.send_keys("neuer_benutzername")

        # 8. Farbe ändern (optional)
        color_input = driver.find_element(By.ID, "color")
        color_input.clear()
        color_input.send_keys("#ff0000")  # Rot als Beispiel

        # 9. Passwort ändern (optional)
        password_input = driver.find_element(By.ID, "password")
        password_input.clear()
        password_input.send_keys("neues_passwort")

        # 10. Formular absenden
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # 11. Auf Flash-Meldung warten (Klasse alert-info)
        success_alert = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-info"))
        )
        print("Profil erfolgreich bearbeitet, Flash-Meldung gefunden!")

    except Exception as e:
        print("Fehler aufgetreten:", e)
        print("Aktuelle URL bei Fehler:", driver.current_url)
        driver.save_screenshot("error_screenshot.png")  # Screenshot für Debugging speichern

    finally:
        time.sleep(2)  # Optional zum Beobachten
        driver.quit()

if __name__ == "__main__":
    test_login_and_profile_edit()
