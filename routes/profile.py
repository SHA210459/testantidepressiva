from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def test_login_and_profile_edit():
    driver = webdriver.Chrome()  # Dein WebDriver starten
    driver.maximize_window()

    try:
        # 1. Login-Seite aufrufen
        driver.get("http://127.0.0.1:5000/auth/login")

        # 2. Login-Form ausfüllen
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        driver.find_element(By.NAME, "username").send_keys("aaa")
        driver.find_element(By.NAME, "password").send_keys("aaa")

        # 3. Login-Button scrollen & per JS klicken (vermeidet 'click intercepted')
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        driver.execute_script("arguments[0].scrollIntoView(true);", login_button)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", login_button)

        # 4. Warten, bis Login erfolgreich ist (URL enthält /home)
        try:
            WebDriverWait(driver, 10).until(
                EC.url_contains("/home")
            )
            print("Login erfolgreich, aktuelle URL:", driver.current_url)
        except Exception:
            print("Login fehlgeschlagen, aktuelle URL:", driver.current_url)
            print("Seitenquelltext (Auszug):", driver.page_source[:500])
            return  # Test abbrechen

        # 5. Profilseite aufrufen
        driver.get("http://127.0.0.1:5000/profile/profile")

        # 6. Warten bis Profil-Seite geladen ist (Username-Feld)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )

        # 7. Username ändern
        username_input = driver.find_element(By.ID, "username")
        username_input.clear()
        username_input.send_keys("neuer_benutzername")

        # 8. Farbe ändern
        color_input = driver.find_element(By.ID, "color")
        driver.execute_script("arguments[0].value = '#00FF00';", color_input)  # Setze green via JS

        # 9. Passwort ändern
        password_input = driver.find_element(By.ID, "password")
        password_input.clear()
        password_input.send_keys("neues_passwort")

        # 10. Submit-Button scrollen & klicken via JS
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", submit_button)

        # 11. Warten auf Flash-Meldung (alert-info)
        success_alert = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-info"))
        )
        print("Profil erfolgreich bearbeitet, Flash-Meldung gefunden!")

    finally:
        time.sleep(2)  # Zum Debuggen, kannst du entfernen
        driver.quit()

if __name__ == "__main__":
    test_login_and_profile_edit()
