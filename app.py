# app.py

import os
from datetime import datetime
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage
from dotenv import load_dotenv
from gemini_handler import analyze_with_gemini, analyze_image_with_gemini, init_storage, get_daily_summary
from patient_profiles import MR_LIN_PROFILE, get_weekly_meal_plan, get_bp_log_format

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize LINE bot
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

# Simple in-memory storage for demo
user_daily_intake = {}
user_bp_records = {}  # Store BP measurements
user_medication_taken = {}  # Track medication
user_exercise_log = {}  # Track exercise
user_first_message = {}  # Track if user is new

# Make it accessible to other modules
def get_user_daily_intake():
    return user_daily_intake

# Initialize gemini_handler with storage reference
init_storage(user_daily_intake)

@app.route("/")
def home():
    return "NutriLINE - 林先生的營養追蹤助手 🥗"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    user_id = event.source.user_id
    user_message = event.message.text.strip()
    
    # Check if this is user's first message
    if user_id not in user_first_message:
        user_first_message[user_id] = True
        # Send Mr. Lin's personalized greeting
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=MR_LIN_PROFILE['initial_greeting'])
        )
        return
    
    # Handle /help command
    if user_message.lower() == '/help' or user_message == '幫助' or user_message == '說明':
        help_text = """🥗 林先生的營養追蹤助手

📱 主要功能：
• 分析食物照片並記錄營養
• 追蹤每日鈉攝取（限1500mg）
• 提醒健康飲食選擇
• 記錄血壓和運動
• 藥物提醒

📋 指令列表：
/help - 顯示這個說明
/today - 今日營養摘要
/plan - 查看一週DASH飲食計畫
/bp - 記錄血壓（例：/bp 145/90）
/med - 記錄服藥
/exercise - 記錄運動
/tips - 飲食小技巧
/clear - 重置今天的紀錄

💡 記住我們的目標：
✅ 早餐：全麥吐司+水煮蛋
✅ 牛肉麵不喝湯
✅ 每天走路30分鐘
✅ 按時服用Amlodipine

林太太有幫您準備餐點嗎？記得傳照片給我！"""
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=help_text)
        )
        return
    
    # Handle /today command
    elif user_message.lower() == '/today' or user_message == '今天':
        summary = get_daily_summary(user_id)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=summary)
        )
        return
    
    # Handle /plan command - NEW FEATURE
    elif user_message.lower() == '/plan' or user_message == '飲食計畫':
        meal_plan = get_weekly_meal_plan()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=meal_plan)
        )
        return
    
    # Handle /bp command - NEW FEATURE
    elif user_message.lower().startswith('/bp'):
        if len(user_message.split()) > 1:
            bp_value = user_message.split()[1]
            if '/' in bp_value:
                record_bp(user_id, bp_value)
                response = f"✅ 已記錄血壓：{bp_value}\n"
                
                # Check if BP is high
                systolic = int(bp_value.split('/')[0])
                if systolic >= 140:
                    response += "⚠️ 血壓偏高！記得放鬆心情，避免高鈉食物"
                else:
                    response += "👍 血壓控制不錯，繼續保持！"
                
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=response)
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="請輸入正確格式，例如：/bp 130/85")
                )
        else:
            bp_log = get_bp_log_format(user_id, user_bp_records.get(user_id, []))
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=bp_log)
            )
        return
    
    # Handle /med command - NEW FEATURE
    elif user_message.lower() == '/med' or user_message == '吃藥':
        today = datetime.now().strftime('%Y-%m-%d')
        if user_id not in user_medication_taken:
            user_medication_taken[user_id] = {}
        user_medication_taken[user_id][today] = True
        
        response = "✅ 已記錄今天服用 Amlodipine 5mg\n\n"
        response += "💊 記得：\n"
        response += "• 每天固定時間服用\n"
        response += "• 不可配葡萄柚\n"
        response += "• 配合飲食控制效果更好！"
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response)
        )
        return
    
    # Handle /exercise command - NEW FEATURE
    elif user_message.lower().startswith('/exercise') or user_message.startswith('運動'):
        today = datetime.now().strftime('%Y-%m-%d')
        if user_id not in user_exercise_log:
            user_exercise_log[user_id] = {}
        
        # Extract minutes if provided
        parts = user_message.split()
        if len(parts) > 1 and parts[1].isdigit():
            minutes = int(parts[1])
            user_exercise_log[user_id][today] = minutes
            response = f"✅ 已記錄運動 {minutes} 分鐘！\n\n"
            if minutes >= 30:
                response += "🎉 太棒了！達到今天的運動目標！\n"
                response += "林太太一定很開心看到您這麼努力 💪"
            else:
                response += f"💪 加油！再運動 {30-minutes} 分鐘就達標了！"
        else:
            user_exercise_log[user_id][today] = 30
            response = "✅ 已記錄運動 30 分鐘！\n"
            response += "🎉 太棒了林先生！持續運動對血壓控制很有幫助！"
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response)
        )
        return
    
    # Handle /tips command - NEW FEATURE
    elif user_message.lower() == '/tips' or user_message == '小技巧':
        tips = """🌟 林先生的健康小技巧

🧂 減鈉妙招：
• 用大蒜、薑、醋、檸檬調味
• 醬料另外裝，沾著吃
• 選「乾」的麵食，避免喝湯
• 少吃醃漬品和加工食品

🥗 聰明選擇：
• 早餐店：蛋餅不加醬 > 鐵板麵
• 便當店：蒸煮 > 油炸，配菜選時蔬
• 麵店：乾麵 > 湯麵，不喝湯
• 飲料：無糖茶 > 半糖飲料

🏃 運動建議：
• 飯後散步最適合
• 遛狗時多走15分鐘
• 週末和林太太去公園
• 爬樓梯代替搭電梯

記住：小改變，大健康！為了不像爸爸一樣，我們一起努力 💪"""
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=tips)
        )
        return
    
    # Handle /clear command
    elif user_message.lower() == '/clear' or user_message == '清除':
        user_daily_intake[user_id] = {
            'calories': 0, 'protein': 0, 'carbs': 0, 
            'fat': 0, 'sodium': 0, 'meals': []
        }
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="✅ 林先生，今天的紀錄已經清除囉！\n重新開始記錄，記得要選健康的食物哦～")
        )
        return
    
    # For everything else, use Gemini's natural language understanding
    response = analyze_with_gemini(user_message, user_id)
    
    # Send response
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response)
    )

@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    user_id = event.source.user_id
    
    # Send analyzing message
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="📸 讓我看看林先生今天吃了什麼...")
    )
    
    try:
        # Analyze image with Gemini
        analysis = analyze_image_with_gemini(event.message.id, line_bot_api, user_id)
        
        # Send results
        line_bot_api.push_message(
            user_id,
            TextSendMessage(text=analysis)
        )
        
    except Exception as e:
        line_bot_api.push_message(
            user_id,
            TextSendMessage(text="哎呀，照片有點問題欸，林先生再傳一次試試看？")
        )

def record_bp(user_id, bp_value):
    """Record blood pressure measurement"""
    if user_id not in user_bp_records:
        user_bp_records[user_id] = []
    
    user_bp_records[user_id].append({
        'datetime': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'value': bp_value
    })
    
    # Keep only last 7 records
    if len(user_bp_records[user_id]) > 7:
        user_bp_records[user_id] = user_bp_records[user_id][-7:]

if __name__ == "__main__":
    app.run(debug=True, port=5000)