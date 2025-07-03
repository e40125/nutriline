# NutriLINE – main server
import os
from datetime import datetime
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage
from dotenv import load_dotenv

from gemini_handler import (
    analyze_with_gemini,
    analyze_image_with_gemini,
    init_storage,
    get_daily_summary,
)
from patient_profiles import (
    MR_LIN_PROFILE,
    get_weekly_meal_plan,
    get_bp_log_format,
)

load_dotenv()  # read .env

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

# simple in-memory demo store
user_daily_intake = {}
user_bp_records = {}
user_med_taken = {}
user_exercise = {}
first_time_user = {}

init_storage(user_daily_intake)  # give dict ref to gemini_handler


@app.route("/")
def home():
    return "NutriLINE is running 🥗"


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"


# ========== TEXT EVENTS ==========
@handler.add(MessageEvent, message=TextMessage)
def on_text(event):
    uid = event.source.user_id
    msg = event.message.text.strip()

    # greet first-time user
    if uid not in first_time_user:
        first_time_user[uid] = True
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(MR_LIN_PROFILE["initial_greeting"])
        )
        return

    # command router
    if msg.lower() in ("/help", "幫助", "說明"):
        line_bot_api.reply_message(event.reply_token, TextSendMessage(help_text()))
    elif msg.lower() in ("/today", "今天"):
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(get_daily_summary(uid))
        )
    elif msg.lower() in ("/plan", "飲食計畫"):
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(get_weekly_meal_plan())
        )
    elif msg.lower().startswith("/bp"):
        handle_bp(uid, msg, event.reply_token)
    elif msg.lower() in ("/med", "吃藥"):
        record_med(uid)
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage("✅ 已記錄今日 Amlodipine 5 mg")
        )
    elif msg.lower().startswith("/exercise") or msg.startswith("運動"):
        handle_exercise(uid, msg, event.reply_token)
    elif msg.lower() in ("/tips", "小技巧"):
        line_bot_api.reply_message(event.reply_token, TextSendMessage(tips_text()))
    elif msg.lower() in ("/clear", "清除"):
        user_daily_intake[uid] = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0, "sodium": 0, "meals": []}
        line_bot_api.reply_message(event.reply_token, TextSendMessage("已清除今天的紀錄"))
    else:
        # send to Gemini
        reply = analyze_with_gemini(msg, uid)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(reply))


# ========== IMAGE EVENTS ==========
@handler.add(MessageEvent, message=ImageMessage)
def on_image(event):
    uid = event.source.user_id
    line_bot_api.reply_message(event.reply_token, TextSendMessage("📸 分析中…"))
    try:
        analysis = analyze_image_with_gemini(event.message.id, line_bot_api, uid)
        line_bot_api.push_message(uid, TextSendMessage(analysis))
    except Exception:
        line_bot_api.push_message(uid, TextSendMessage("圖片有問題，再傳一次試試！"))


# ---------- helpers ----------
def help_text():
    return """🥗 指令：
/help 說明
/today 今日摘要
/plan 一週菜單
/bp 130/85 記錄血壓
/med 記錄服藥
/exercise 30 記錄運動
/tips 小技巧
/clear 清除今日紀錄
"""


def tips_text():
    return """🌟 健康小技巧
• 醬料分開沾
• 麵改乾、湯另外裝
• 用醋、檸檬、大蒜調味
• 飯後散步 30 分鐘
"""


def handle_bp(uid, msg, token):
    parts = msg.split()
    if len(parts) > 1 and "/" in parts[1]:
        bp = parts[1]
        user_bp_records.setdefault(uid, []).append(
            {"datetime": datetime.now().strftime("%Y-%m-%d %H:%M"), "value": bp}
        )
        line_bot_api.reply_message(token, TextSendMessage(f"✅ 已記錄血壓 {bp}"))
    else:
        log = get_bp_log_format(uid, user_bp_records.get(uid, []))
        line_bot_api.reply_message(token, TextSendMessage(log))


def record_med(uid):
    today = datetime.now().strftime("%Y-%m-%d")
    user_med_taken.setdefault(uid, {})[today] = True


def handle_exercise(uid, msg, token):
    today = datetime.now().strftime("%Y-%m-%d")
    minutes = 30  # default
    parts = msg.split()
    if len(parts) > 1 and parts[1].isdigit():
        minutes = int(parts[1])
    user_exercise.setdefault(uid, {})[today] = minutes
    line_bot_api.reply_message(token, TextSendMessage(f"✅ 運動 {minutes} 分鐘已記錄"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
