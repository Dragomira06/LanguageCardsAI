import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 1. Прочитаме API ключа от скрития .env файл
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ Грешка: Не открих GEMINI_API_KEY във файла .env!")
    exit()

client = genai.Client(api_key=api_key)

# 2. Питаме потребителя за глагол
verb = input("👉 Въведете италиански глагол (напр. fare, venire, essere): ").strip().lower()
if not verb:
    verb = "andare"

print(f"\n⏳ Gemini генерира картички за '{verb}'...")

# 3. Инструкции към Gemini
prompt = f"""
Генерирай 3 картички за упражнение на италианския неправилен глагол '{verb}' в сегашно време.
За всяка картичка дай:
- front: изречение с липсваща дума (______)
- back: правилната дума
- translation_bg: превод на български
- options: масив от 4 възможни отговора
- explanation: кратко обяснение

Върни отговора ЕДИНСТВЕНО като валиден JSON масив.
"""

# 4. Извикване на AI модела
response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=prompt,
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
    ),
)

# 5. Превръщаме текста от Gemini в Python данни
new_cards = json.loads(response.text)

# 6. Запазваме картичките във файла cards.json
filename = "cards.json"
all_cards = []

# Ако файлът cards.json вече съществува, първо прочитаме старите картички
if os.path.exists(filename):
    with open(filename, "r", encoding="utf-8") as file:
        try:
            all_cards = json.load(file)
        except json.JSONDecodeError:
            all_cards = []

# Добавяме новите картички към старите
all_cards.extend(new_cards)

# Записваме всичко обратно във файла cards.json
with open(filename, "w", encoding="utf-8") as file:
    json.dump(all_cards, file, ensure_ascii=False, indent=2)

print(f"\n✅ Успешно! Добавени са {len(new_cards)} нови картички.")
print(f"📁 Общ брой картички в '{filename}': {len(all_cards)}\n")

# Показваме току-що генерираните картички на екрана
print(json.dumps(new_cards, indent=2, ensure_ascii=False))