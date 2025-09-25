# bot_webhook.py
import os
import logging
from flask import Flask, request
import openai
import requests

# Логирование
logging.basicConfig(level=logging.INFO)

# Переменные окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# URL Telegram API
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# Flask сервер
app = Flask(__name__)

def send_message(chat_id, text):
    """Отправка сообщения пользователю Telegram"""
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        logging.error(f"Ошибка при отправке сообщения: {e}")

def generate_reply(user_message):
    """Генерация ответа через OpenAI"""
    prompt = f"""
Ты — Блейз, рассудительный и строгий персонаж из "Темного Рождества".
Отвечай коротко, мрачно, загадочно.
Пользователь говорит: "{user_message}"
Блейз отвечает:
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role":"user","content":prompt}],
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Ошибка при запросе к ИИ: {e}")
        return "Ошибка при запросе к ИИ."

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def telegram_webhook():
    """Главная точка Webhook для Telegram"""
    data = request.get_json()
    logging.info(f"Получено сообщение: {data}")

    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"]["text"]
        reply = generate_reply(user_message)
        send_message(chat_id, reply)

    return {"ok": True}

@app.route("/")
def index():
    return "Блейз бот работает!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
