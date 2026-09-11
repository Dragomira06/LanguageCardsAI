import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 1. Зареждаме API ключа
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("❌ Не е намерен GEMINI_API_KEY в .env файла!")

client = genai.Client(api_key=api_key)

# 2. Инициализираме FastAPI приложението
app = FastAPI(title="Italian Verb Flashcards AI")

# Модел за входящата заявка от браузъра
class VerbRequest(BaseModel):
    verb: str

# 3. Ендпоинт за генериране на нови картички
@app.post("/api/generate")
def generate_cards(data: VerbRequest):
    verb = data.verb.strip().lower()
    if not verb:
        verb = "andare"

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

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )

        new_cards = json.loads(response.text)

        # Записваме и в cards.json
        filename = "cards.json"
        all_cards = []
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                try:
                    all_cards = json.load(f)
                except json.JSONDecodeError:
                    all_cards = []

        all_cards.extend(new_cards)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(all_cards, f, ensure_ascii=False, indent=2)

        return {"status": "success", "cards": new_cards}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 4. Ендпоинт за вземане на всички досега записани картички
@app.get("/api/cards")
def get_all_cards():
    filename = "cards.json"
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

# 5. Сервиране на началната HTML страница
@app.get("/")
def read_root():
    return FileResponse("static/index.html")

# Свързваме папката 'static' за HTML/CSS/JS файлове
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")