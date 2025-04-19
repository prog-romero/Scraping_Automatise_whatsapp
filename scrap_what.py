from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv

# === CONFIGURATION ===
CHROMEDRIVER_PATH = '/usr/local/bin/chromedriver'  # Vérifie ce chemin
GROUP_NAME = "Hackathon"
WAIT_TIME = 60

# === LANCEMENT SELENIUM ===
options = webdriver.ChromeOptions()
options.add_argument("--user-data-dir=./profile")  # Pour éviter de rescanner le QR à chaque fois
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

try:
    group = wait.until(EC.presence_of_element_located(
        (By.XPATH, f'//span[@title="{GROUP_NAME}"]')
    ))
    group.click()
    time.sleep(2)
except:
    print("❌ Groupe non trouvé.")
    driver.quit()
    exit()

# === LOCALISER UN PREMIER MESSAGE POUR REMONTER AU CONTENEUR PARENT ===
print("📥 Recherche d'un message pour remonter au conteneur parent...")

first_message = wait.until(EC.presence_of_element_located((
    By.XPATH, '//div[contains(@class, "message-in") or contains(@class, "message-out")]'
)))

# Le conteneur est 4 niveaux au-dessus du message dans la hiérarchie DOM
chat_container = first_message.find_element(By.XPATH, "./ancestor::div[@class][4]")

print("✅ Conteneur localisé. Chargement de l'historique...")

# === SCROLLER POUR CHARGER L’HISTORIQUE ===
last_height = driver.execute_script("return arguments[0].scrollHeight", chat_container)
# === SCROLLER POUR CHARGER L’HISTORIQUE ===
print("⏪ Défilement jusqu'au tout début de la conversation...")

last_height = driver.execute_script("return arguments[0].scrollHeight", chat_container)
same_height_counter = 0
MAX_SAME_HEIGHT = 3  # Nombre de fois où la hauteur ne change pas avant d'arrêter

while True:
    driver.execute_script("arguments[0].scrollTop = 0", chat_container)
    time.sleep(2)  # attendre le chargement des anciens messages
    new_height = driver.execute_script("return arguments[0].scrollHeight", chat_container)

    if new_height == last_height:
        same_height_counter += 1
        print(f"🧱 Hauteur identique ({same_height_counter}/{MAX_SAME_HEIGHT})")
        if same_height_counter >= MAX_SAME_HEIGHT:
            break
    else:
        same_height_counter = 0
        last_height = new_height

print("✅ Défilement terminé. Tous les messages devraient être chargés.")


print("\n✅ Fin du chargement.")

# === EXTRACTION DE TOUS LES MESSAGES ===
print("📥 Extraction des messages...")
message_blocks = chat_container.find_elements(By.XPATH, './/div[contains(@class,"message-in") or contains(@class,"message-out")]')

all_texts = []
for i, block in enumerate(message_blocks, 1):
    try:
        span = block.find_element(By.XPATH, './/span[@dir="ltr"]')
        text = span.text.strip()
        if text:
            print(f"{i}. {text}")
            all_texts.append(text)
    except Exception:
        continue  # Certains blocs n'ont pas de texte

# === SAUVEGARDE CSV ===
with open("messages.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["id", "message"])
    for i, msg in enumerate(all_texts, 1):
        writer.writerow([i, msg])

print(f"💾 {len(all_texts)} messages sauvegardés dans messages.csv")
print("✅ Terminé.")
