# gemini_handler.py - Complete file customized for Mr. Lin

import os
import re
from google import genai
from google.genai import types
from dotenv import load_dotenv
from patient_profiles import MR_LIN_PROFILE, get_mr_lin_context, check_food_for_mr_lin

load_dotenv()

# Initialize Gemini client
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

# Storage will be passed from main app
user_daily_intake = None
user_conversation_count = {}  # Track conversation depth

def init_storage(storage_ref):
    """Initialize storage reference from main app"""
    global user_daily_intake
    user_daily_intake = storage_ref

# Demo mode flag - always True for Mr. Lin demo
DEMO_MODE = True

def get_conversation_depth(user_id):
    """Track how many messages exchanged to adjust verbosity"""
    if user_id not in user_conversation_count:
        user_conversation_count[user_id] = 0
    user_conversation_count[user_id] += 1
    return user_conversation_count[user_id]

def analyze_with_gemini(user_message, user_id):
    """Mr. Lin specific version with personalized responses"""
    
    # Track conversation depth
    msg_count = get_conversation_depth(user_id)
    
    # Check if message seems food-related
    food_keywords = ['吃', '喝', '早餐', '午餐', '晚餐', '宵夜', '點心', '飲料', 'ate', 'eaten', 'had', 'breakfast', 'lunch', 'dinner']
    is_food_log = any(keyword in user_message.lower() for keyword in food_keywords)
    
    # Get current intake
    current_intake = user_daily_intake.get(user_id, {})
    current_sodium = current_intake.get('sodium', 0)
    current_calories = current_intake.get('calories', 0)
    
    # Build Mr. Lin specific prompt
    base_prompt = f"""你是林先生的個人營養追蹤助手。以下是他的完整背景：

**諮詢背景（從營養師轉介）：**
- 林先生，55歲，BMI 27，高血壓（145/92）
- 每天服用 Amlodipine 5mg
- 爸爸60多歲中風（他最大的恐懼）
- 原本飲食：油條甜豆漿、滷肉飯、牛肉麵（喝湯）、洋芋片、珍奶
- 原本鈉攝取：約4000毫克/天（超標快3倍！）
- 久坐上班，只有週末跟林太太散步
- LDL膽固醇160，血糖也偏高

**營養師計畫（他已同意）：**
- 早餐：全麥吐司+水煮蛋+無糖豆漿（取代油條）
- 午餐：清蒸雞肉/豆腐（取代滷肉）
- 晚餐：乾麵或不喝湯（取代整碗湯）
- 點心：水果、無鹽堅果（取代洋芋片）
- 每天走路30分鐘，5次/週（可以遛狗時進行）
- 鈉限制：1500毫克/天
- 熱量目標：2000大卡/天
- 林太太會協助準備健康餐點

**今日狀況：**
- 已攝取鈉：{current_sodium:.0f}毫克（限制1500）
- 已攝取熱量：{current_calories:.0f}大卡（目標2000）
- 第{msg_count}次對話

使用者訊息："{user_message}"

重要回應原則：
1. 你完全了解林先生的病史和諮詢內容
2. 如果他吃了不該吃的（如油條），溫和但堅定地提醒
3. 適時提到他爸爸中風的事（這是他的主要動力）
4. 多提到林太太的支持和幫助
5. 建議要具體可行（用大蒜、醋調味等）
6. 用台灣人說話方式，親切但關心的語氣
7. 記得他「不想吃太多藥」的心願
"""

    # Special context for specific situations
    if "油條" in user_message or "甜豆漿" in user_message:
        base_prompt += """
特別處理：他又吃油條了！
- 溫和提醒全麥吐司的約定
- 提到油脂對LDL的影響（已經160了）
- 請林太太幫忙準備早餐
"""
    
    if "牛肉麵" in user_message:
        base_prompt += """
特別處理：確認他有沒有喝湯！
- 如果喝湯，嚴肅提醒（一碗湯=一天的鈉）
- 建議乾麵或湯另裝
- 提醒他爸爸的事
"""
    
    if "運動" in user_message or "走" in user_message:
        base_prompt += """
特別處理：運動追蹤
- 鼓勵他遛狗時多走15分鐘
- 提醒林太太可以陪他
- 讚美任何運動努力
"""
    
    if "血壓" in user_message or "藥" in user_message:
        base_prompt += """
特別處理：健康監測
- 提醒按時吃 Amlodipine 5mg
- 詢問今天血壓多少
- 強調飲食控制能減少用藥
"""

    base_prompt += """
回應風格：
- 像個關心他的朋友，不是機器人
- 用「林先生」稱呼，表示尊重
- 適當使用 😊 💪 👍 等表情
- 語氣：關切但不說教，鼓勵但要實際
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[base_prompt]
        )
        
        response_text = response.text
        
        # If it was a food log, extract nutrition and add Mr. Lin specific warnings
        if is_food_log:
            nutrition_data = update_daily_intake(user_id, user_message, response.text)
            
            if nutrition_data['calories'] > 0:
                # Check against Mr. Lin's specific triggers
                warnings, suggestions = check_food_for_mr_lin(user_message, nutrition_data)
                
                # Add personalized warnings based on daily totals
                new_sodium_total = current_sodium + nutrition_data.get('sodium', 0)
                
                if current_sodium < 1500 and new_sodium_total >= 1500:
                    response_text += "\n\n🚨 林先生！今天的鈉已經超標了（1500毫克）！"
                    response_text += "\n記得您爸爸的事...晚餐一定要清淡，不然血壓會飆高的"
                elif current_sodium < 1200 and new_sodium_total >= 1200:
                    response_text += "\n\n📊 提醒：鈉攝取已經到80%了，晚餐要小心哦"
                
                # Add any specific warnings
                for warning in warnings[:1]:  # Only show top warning
                    response_text += f"\n\n{warning}"
                
                for suggestion in suggestions[:1]:  # Only show top suggestion
                    response_text += f"\n💡 {suggestion}"
        
        return response_text
        
    except Exception as e:
        return "哎呀，我現在有點轉不過來，林先生可以再說一次嗎？"

def analyze_image_with_gemini(image_id, line_bot_api, user_id):
    """Mr. Lin specific image analysis"""
    
    # Track conversation
    msg_count = get_conversation_depth(user_id)
    current_intake = user_daily_intake.get(user_id, {})
    current_sodium = current_intake.get('sodium', 0)
    current_calories = current_intake.get('calories', 0)
    
    try:
        # Download image from LINE
        message_content = line_bot_api.get_message_content(image_id)
        image_bytes = b''
        for chunk in message_content.iter_content():
            image_bytes += chunk
        
        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type='image/jpeg'
        )
        
        prompt = f"""你是林先生的營養追蹤助手，正在分析他傳來的食物照片。

林先生背景：
- 55歲，高血壓（145/92），BMI 27
- 原本愛吃：油條、滷肉飯、牛肉麵湯
- 目標：鈉<1500mg/天，熱量2000大卡
- 今天已吃：鈉{current_sodium}mg，熱量{current_calories}大卡
- 怕像爸爸一樣中風

分析這張照片時：
1. 用台灣人熟悉的食物名稱描述
2. 估算營養成分（特別注意鈉含量）
3. 如果是他的「地雷食物」（油條、滷肉、醃菜等），要提醒
4. 給出具體建議（不是說教）
5. 如果是健康選擇，要大力稱讚
6. 適時提到林太太可以幫忙準備更健康的版本

回應要像朋友，不要像營養報告。"""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt, image_part]
        )
        
        # Extract nutrition and check limits
        nutrition_data = update_daily_intake_from_image(user_id, response.text)
        
        response_text = response.text
        
        # Mr. Lin specific alerts
        if nutrition_data.get('sodium', 0) > 0:
            new_sodium_total = current_sodium + nutrition_data['sodium']
            
            # Check for his specific trigger foods in the response
            if any(trigger in response_text for trigger in ['油條', '滷肉', '牛肉麵', '醃']):
                response_text += "\n\n😅 林先生...這個不是我們說好要避免的嗎？"
                response_text += "\n記得您說過「不想像爸爸一樣」，加油，我們可以做到的！"
            
            if new_sodium_total >= 1500:
                response_text += "\n\n🚨 糟糕！今天鈉攝取爆表了！"
                response_text += "\n晚餐拜託一定要清淡，喝點水，明天重新開始 💪"
        
        return response_text
        
    except Exception as e:
        return "哎呀，照片有點看不清楚欸，林先生可以再拍一張嗎？光線亮一點會更好哦！"

def get_daily_summary(user_id):
    """Generate Mr. Lin specific daily summary"""
    # Import these at function level to avoid circular import
    from datetime import datetime
    
    if user_id not in user_daily_intake or not user_daily_intake[user_id]['meals']:
        return """📊 林先生，今天還沒有記錄任何餐點欸！

記得要：
• 拍照或告訴我您吃了什麼
• 早餐吃全麥吐司了嗎？
• 今天走路了嗎？

加油！為了不要像爸爸一樣，我們一起努力 💪"""
    
    intake = user_daily_intake[user_id]
    meals_list = "\n".join([f"• {meal}" for meal in intake['meals'][-5:]])
    
    # Calculate percentages
    sodium_percent = (intake['sodium'] / 1500) * 100
    calorie_percent = (intake['calories'] / 2000) * 100
    
    # Mr. Lin specific messages based on performance
    if intake['sodium'] > 1500:
        sodium_msg = f"⚠️ 鈉已超標！{intake['sodium']:.0f}毫克（{sodium_percent:.0f}%）\n林先生，想想您爸爸...明天一定要控制！"
    elif intake['sodium'] > 1200:
        sodium_msg = f"📊 鈉快到上限了：{intake['sodium']:.0f}毫克（{sodium_percent:.0f}%）\n晚餐記得清淡一點哦"
    else:
        sodium_msg = f"✅ 鈉控制得不錯：{intake['sodium']:.0f}毫克（{sodium_percent:.0f}%）\n繼續保持！"
    
    # Check if he ate any trigger foods
    trigger_foods_eaten = []
    for meal in intake['meals']:
        if '油條' in meal:
            trigger_foods_eaten.append('油條')
        if '牛肉麵' in meal:
            trigger_foods_eaten.append('牛肉麵')
        if '滷肉' in meal:
            trigger_foods_eaten.append('滷肉')
    
    reminder = ""
    if trigger_foods_eaten:
        reminder = f"\n\n💭 今天又吃了{' '.join(trigger_foods_eaten)}...記得我們的約定嗎？"
    else:
        reminder = "\n\n👏 今天選擇不錯！林太太的健康餐有幫助吧？"
    
    summary = f"""📊 林先生今日營養摘要
━━━━━━━━━━━━━━━
📈 總攝取量：
• 熱量：{intake['calories']:.0f} 大卡（{calorie_percent:.0f}%）
• 蛋白質：{intake['protein']:.1f} 克
• 碳水化合物：{intake['carbs']:.1f} 克
• 脂肪：{intake['fat']:.1f} 克
{sodium_msg}

🍽️ 今天吃了：
{meals_list}

💊 記得吃 Amlodipine 5mg 了嗎？
🚶 今天走路30分鐘了嗎？
📏 血壓記得量了嗎？
{reminder}

明天繼續加油！為了健康，為了家人 💪

💡 輸入 /plan 查看明天的建議餐點"""
    
    return summary

def update_daily_intake(user_id, user_message, gemini_response):
    """Extract nutrition data and return it"""
    if user_id not in user_daily_intake:
        user_daily_intake[user_id] = {
            'calories': 0, 'protein': 0, 'carbs': 0, 
            'fat': 0, 'sodium': 0, 'meals': []
        }
    
    nutrition = extract_nutrition_values(gemini_response)
    
    if nutrition['calories'] > 0:
        for key, value in nutrition.items():
            if key != 'meal_description':
                user_daily_intake[user_id][key] += value
        
        meal_desc = user_message[:50] + "..." if len(user_message) > 50 else user_message
        user_daily_intake[user_id]['meals'].append(meal_desc)
    
    return nutrition

def update_daily_intake_from_image(user_id, gemini_response):
    """Extract nutrition from image analysis"""
    if user_id not in user_daily_intake:
        user_daily_intake[user_id] = {
            'calories': 0, 'protein': 0, 'carbs': 0, 
            'fat': 0, 'sodium': 0, 'meals': []
        }
    
    nutrition = extract_nutrition_values(gemini_response)
    
    if nutrition['calories'] > 0:
        for key, value in nutrition.items():
            if key != 'meal_description':
                user_daily_intake[user_id][key] += value
        
        # Try to extract food name from response
        food_match = re.search(r'這[似看]起來是(.+?)[！。\n]', gemini_response)
        if food_match:
            meal_desc = f"照片：{food_match.group(1)}"
        else:
            meal_desc = "照片：分析的餐點"
        
        user_daily_intake[user_id]['meals'].append(meal_desc)
    
    return nutrition

def extract_nutrition_values(text):
    """Extract nutrition values - works with both English and Chinese"""
    values = {
        'calories': 0,
        'protein': 0,
        'carbs': 0,
        'fat': 0,
        'sodium': 0
    }
    
    # Patterns for both languages
    patterns = {
        'calories': [
            r'(\d+)\s*(?:calories|kcal|cal|大卡|卡路里|熱量)',
            r'(?:calories|熱量)[:\s]+(\d+)',
            r'(?:約|大約|大概|approximately)?\s*(\d+)\s*(?:kcal|大卡)'
        ],
        'protein': [
            r'(?:protein|蛋白質)[:\s]+(\d+\.?\d*)\s*(?:g|克|公克)',
            r'(\d+\.?\d*)\s*(?:g|克)\s*(?:protein|蛋白質)',
            r'蛋白質\s*(\d+\.?\d*)(?:g|克)?'
        ],
        'carbs': [
            r'(?:carb|碳水化合物|醣類)[:\s]+(\d+\.?\d*)\s*(?:g|克|公克)',
            r'(\d+\.?\d*)\s*(?:g|克)\s*(?:carb|碳水)',
            r'碳水\s*(\d+\.?\d*)(?:g|克)?'
        ],
        'fat': [
            r'(?:fat|脂肪)[:\s]+(\d+\.?\d*)\s*(?:g|克|公克)',
            r'(\d+\.?\d*)\s*(?:g|克)\s*(?:fat|脂肪)',
            r'脂肪\s*(\d+\.?\d*)(?:g|克)?'
        ],
        'sodium': [
            r'(?:sodium|鈉)[:\s]+(\d+)\s*(?:mg|毫克)',
            r'(\d+)\s*(?:mg|毫克)\s*(?:sodium|的鈉|鈉)',
            r'鈉\s*(\d+)\s*(?:mg|毫克)?',
            r'(\d+)-(\d+)\s*(?:mg|毫克)\s*(?:的)?鈉'  # For ranges
        ]
    }
    
    text_lower = text.lower()
    for nutrient, pattern_list in patterns.items():
        for pattern in pattern_list:
            match = re.search(pattern, text_lower)
            if match:
                if nutrient == 'sodium' and len(match.groups()) == 2:
                    # For ranges, take the higher value
                    values[nutrient] = float(match.group(2))
                else:
                    values[nutrient] = float(match.group(1))
                break
    
    return values