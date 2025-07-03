# Gemini tools for NutriLINE
import os, re, datetime, base64
from google import generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

user_store = {}
user_turns = {}


def init_storage(store):
    global user_store
    user_store = store


def turn(uid):
    user_turns[uid] = user_turns.get(uid, 0) + 1
    return user_turns[uid]


def analyze_with_gemini(msg, uid):
    depth = turn(uid)
    ctx = f"第 {depth} 次對話。今日統計：{user_store.get(uid, {})}"
    prompt = f"{ctx}\n使用者訊息：{msg}\n請用台灣口吻回覆。"
    try:
        res = model.generate_content(prompt)
        txt = res.text
        save_nutrition(uid, msg, txt)
        return txt
    except Exception:
        return "抱歉，暫時無法回覆…"


def analyze_image_with_gemini(img_id, line_api, uid):
    blob = b"".join(line_api.get_message_content(img_id).iter_content())
    part = genai.types.FileData(data=blob, mime_type="image/jpeg")
    prompt = "請判斷食物並估算營養（熱量、蛋白質、脂肪、碳水、鈉）。"
    res = model.generate_content([prompt, part])
    txt = res.text
    save_nutrition(uid, "照片", txt)
    return txt


# --- nutrition helpers ---
def save_nutrition(uid, meal, text):
    if uid not in user_store:
        user_store[uid] = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0, "sodium": 0, "meals": []}
    data = extract(text)
    if data["calories"] > 0:
        for k, v in data.items():
            if k != "desc":
                user_store[uid][k] += v
        user_store[uid]["meals"].append(meal)


def extract(t):
    pats = {
        "calories": r"(\d+)\s*(?:kcal|大卡)",
        "protein": r"(\d+\.?\d*)\s*(?:g|克).{0,4}(?:protein|蛋白質)",
        "carbs": r"(\d+\.?\d*)\s*(?:g|克).{0,4}(?:carb|碳水)",
        "fat": r"(\d+\.?\d*)\s*(?:g|克).{0,4}(?:fat|脂肪)",
        "sodium": r"(\d+)\s*(?:mg|毫克).{0,4}(?:sodium|鈉)",
    }
    out = {k: 0 for k in ["calories", "protein", "carbs", "fat", "sodium"]}
    for k, p in pats.items():
        m = re.search(p, t, re.I)
        if m:
            out[k] = float(m.group(1))
    out["desc"] = t[:40]
    return out


def get_daily_summary(uid):
    if uid not in user_store:
        return "今天還沒有紀錄任何餐點！"
    d = user_store[uid]
    return f"""📊 今日攝取
熱量 {d['calories']:.0f} kcal
蛋白 {d['protein']:.1f} g
碳水 {d['carbs']:.1f} g
脂肪 {d['fat']:.1f} g
鈉 {d['sodium']:.0f} mg
最近餐點: {', '.join(d['meals'][-5:])}"""
