import os
import json
import random
import traceback
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

VK_TOKEN = os.getenv("VK_TOKEN", "").strip()
CONFIRMATION_CODE = os.getenv("CONFIRMATION_CODE", "").strip()
SECRET_KEY = os.getenv("SECRET_KEY", "").strip()
VK_API_VERSION = "5.199"

KEYWORDS = {
    "сердце": "love",
    "любовь": "love",
    "чувствую": "love",
    "правда": "love",

    "деньги": "money",
    "финансы": "money",

    "будущее": "future",
    "судьба": "future",

    "нет": "energy",
    "отдых": "energy",
}


def load_messages(category):
    path = os.path.join("messages", f"{category}.json")
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def vk_api(method, params):
    if not VK_TOKEN:
        print("ERROR: VK_TOKEN is empty")
        return {"error": "VK_TOKEN is empty"}

    payload = dict(params)
    payload["access_token"] = VK_TOKEN
    payload["v"] = VK_API_VERSION

    response = requests.post(
        f"https://api.vk.com/method/{method}",
        data=payload,
        timeout=10
    )
    result = response.json()
    print(f"VK API {method} response:", result)
    return result


def choose_message(text):
    text = (text or "").lower()

    for keyword, category in KEYWORDS.items():
        if keyword in text:
            messages = load_messages(category)
            return random.choice(messages), category, keyword

    return None, None, None


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


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "vk_token_exists": bool(VK_TOKEN),
        "confirmation_code_exists": bool(CONFIRMATION_CODE),
        "secret_key_exists": bool(SECRET_KEY),
    })


@app.route("/callback", methods=["GET"])
def callback_get():
    return "Callback endpoint is alive. VK will use POST here.", 200


@app.route("/callback", methods=["POST"])
def callback():
    try:
        data = request.get_json(force=True, silent=True) or {}
        print("Incoming VK event:", data)

        # ВАЖНО: confirmation отвечаем до проверки secret.
        # Так проще пройти первое подтверждение сервера в VK.
        if data.get("type") == "confirmation":
            print("Confirmation requested. Returning:", CONFIRMATION_CODE)
            return CONFIRMATION_CODE or "", 200

        if SECRET_KEY and data.get("secret") != SECRET_KEY:
            print("Forbidden: wrong secret key")
            return "forbidden", 403

        if data.get("type") == "wall_reply_new":
            obj = data.get("object", {})

            comment_text = obj.get("text", "")
            user_id = obj.get("from_id")
            post_id = obj.get("post_id")
            comment_id = obj.get("id")
            owner_id = obj.get("owner_id")

            message, category, keyword = choose_message(comment_text)

            if message:
                print(f"Matched keyword={keyword}, category={category}, user_id={user_id}")

                if owner_id and post_id and comment_id:
                    reply_to_comment(owner_id, post_id, comment_id, message)
                else:
                    print("Missing comment fields:", obj)

                # VK может не отправить ЛС, если человек не писал сообществу.
                if user_id and user_id > 0:
                    send_private_message(user_id, message)

        return "ok", 200

    except Exception:
        print("Callback error:")
        traceback.print_exc()
        return "ok", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
