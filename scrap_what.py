from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# === CONFIGURATION ===
CHROMEDRIVER_PATH = '/usr/local/bin/chromedriver'  # Vérifie que ce chemin est correct
GROUP_NAME = "Procédure Belgique 2025-2026"         # Nom exact du groupe WhatsApp
WAIT_TIME = 15                                      # Délai pour scanner le QR code

# === LANCEMENT SELENIUM ===
options = webdriver.ChromeOptions()
options.add_argument("--user-data-dir=./profile")  # Sauvegarde la session utilisateur
service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

# === OUVERTURE DE WHATSAPP WEB ===
driver.get("https://web.whatsapp.com/")
print(f"🕐 Patiente {WAIT_TIME} secondes pour scanner le QR Code...")
time.sleep(WAIT_TIME)

# === RECHERCHE DU GROUPE ===
wait = WebDriverWait(driver, 30)
search_box = wait.until(EC.presence_of_element_located(
    (By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
))
search_box.click()
time.sleep(1)
search_box.send_keys(GROUP_NAME)

# === CLIQUER SUR LE GROUPE ===
try:
    group = wait.until(EC.presence_of_element_located(
        (By.XPATH, f'//span[@title="{GROUP_NAME}"]')
    ))
    group.click()
    time.sleep(2)
except:
    print("❌ Groupe non trouvé. Vérifie le nom.")
    driver.quit()
    exit()

# === SCROLLER POUR CHARGER PLUS DE MESSAGES (optionnel) ===
try:
    message_container = driver.find_element(By.XPATH, '//div[@data-testid="chat-history"]')
    for _ in range(5):  # scrolle 5 fois vers le haut pour charger plus de messages
        driver.execute_script("arguments[0].scrollTop = 0", message_container)
        time.sleep(1)
except Exception as e:
    print("⚠️ Impossible de scroller les messages :", e)

# === RÉCUPÉRATION DES MESSAGES VISIBLES ===
print("📥 Récupération des messages...")
messages = driver.find_elements(By.XPATH, '//div[contains(@class,"message-in") or contains(@class,"message-out")]//span[@dir="ltr"]')

if not messages:
    print("❌ Aucun message trouvé. Vérifie que tu es bien dans le groupe.")
else:
    for i, msg in enumerate(messages, 1):
        try:
            text = msg.text.strip()
            if text:
                print(f"{i}. {text}")
        except Exception as e:
            print(f"❌ Erreur pour un message : {e}")

# === FERMETURE ===
# driver.quit()  # décommente si tu veux fermer automatiquement le navigateur après
