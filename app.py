import os
import random
import requests
from flask import Flask, request

app = Flask(__name__)

VK_TOKEN = os.getenv("VK_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")
CONFIRMATION_CODE = os.getenv("CONFIRMATION_CODE")
SECRET_KEY = os.getenv("SECRET_KEY", "")
VK_API_VERSION = "5.199"

MESSAGES = {
    "нет": [
        "Сегодня важно сказать «нет» тому, что забирает ваши силы. Вы не обязаны соглашаться на то, что разрушает ваше спокойствие.",
        "Ваше послание: не позволяйте чужим ожиданиям управлять вашим днём. Сегодня выбирайте себя.",
        "Иногда отказ — это не потеря, а защита. Сегодня ваша энергия требует бережного отношения."
    ],
    "отдых": [
        "Ваша душа просит паузы. Не требуйте от себя больше, чем можете дать сегодня.",
        "Вы слишком долго держали всё внутри. Сейчас важно восстановиться и услышать себя.",
        "Отдых сегодня — не слабость, а способ вернуть себе силу."
    ],
    "сердце": [
        "Чувства, которые вы пытаетесь понять, ещё не раскрылись до конца. Дайте ситуации немного времени.",
        "Сердце уже знает ответ, но разум пока сопротивляется. Прислушайтесь к себе.",
        "В ближайшее время один человек может показать своё истинное отношение."
    ],
    "деньги": [
        "Финансовая ситуация постепенно сдвигается. Обратите внимание на новую идею или предложение.",
        "Сегодня важно не обесценивать свой труд. Вы заслуживаете большего.",
        "Деньги придут через решение, которое вы давно откладывали."
    ],
    "будущее": [
        "Впереди открывается новый этап. Не бойтесь перемен — они ведут вас дальше.",
        "Скоро появится знак, который поможет принять важное решение.",
        "То, что сейчас кажется задержкой, может оказаться защитой от ошибки."
    ],
}


def vk_api(method, params):
    params["access_token"] = VK_TOKEN
    params["v"] = VK_API_VERSION
    return requests.post(f"https://api.vk.com/method/{method}", data=params, timeout=10).json()


def choose_message(text):
    text = text.lower()

    for keyword, messages in MESSAGES.items():
        if keyword in text:
            return random.choice(messages)

    return None


def reply_to_comment(owner_id, post_id, comment_id, message):
    return vk_api("wall.createComment", {
        "owner_id": owner_id,
        "post_id": post_id,
        "reply_to_comment": comment_id,
        "message": f"✨ Послание для вас:\n\n{message}"
    })


def send_private_message(user_id, message):
    return vk_api("messages.send", {
        "user_id": user_id,
        "random_id": random.randint(1, 2_000_000_000),
        "message": f"✨ Послание для вас:\n\n{message}"
    })


@app.route("/", methods=["GET"])
def index():
    return "VK Tarot Bot is working"


@app.route("/callback", methods=["POST"])
def callback():
    data = request.json

    if SECRET_KEY and data.get("secret") != SECRET_KEY:
        return "forbidden", 403

    if data.get("type") == "confirmation":
        return CONFIRMATION_CODE

    if data.get("type") == "wall_reply_new":
        obj = data.get("object", {})
        comment_text = obj.get("text", "")
        user_id = obj.get("from_id")
        post_id = obj.get("post_id")
        comment_id = obj.get("id")
        owner_id = obj.get("owner_id")  # обычно отрицательный id группы

        message = choose_message(comment_text)

        if message:
            reply_to_comment(owner_id, post_id, comment_id, message)

            try:
                send_private_message(user_id, message)
            except Exception:
                pass

    return "ok"
