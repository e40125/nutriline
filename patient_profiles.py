# patient_profiles.py - Enhanced with meal plan and BP tracking functions

MR_LIN_PROFILE = {
    'condition': 'Hypertension',
    'patient_info': {
        'name': '林先生 (Mr. Lin)',
        'age': 55,
        'height': 170,  # cm
        'weight': 78,   # kg
        'bmi': 27,
        'blood_pressure': '145/92',
        'medications': ['Amlodipine 5mg daily'],
        'medical_history': 'Father had stroke in his 60s',
        'lab_results': {
            'ldl_cholesterol': 160,  # mg/dL
            'fasting_glucose': 'slightly elevated',
            'serum_sodium': 'high end of normal'
        }
    },
    'lifestyle': {
        'occupation': 'Sedentary desk job',
        'exercise': 'Weekend walks with wife only',
        'stress_level': 'Moderate',
        'sleep': 'Often uses phone before bed'
    },
    'dietary_history': {
        'breakfast_usual': '油條 + 甜豆漿 (youtiao + sweet soy milk)',
        'lunch_usual': '滷肉飯配醃菜 (braised pork belly with pickled veggies)',
        'dinner_usual': '牛肉麵（喝湯）(beef noodles with broth)',
        'snacks_usual': '洋芋片、珍珠奶茶 (chips, bubble tea)',
        'cooking_style': 'Wife cooks with soy sauce, seasoning cubes',
        'sodium_intake_baseline': 4000,  # mg/day
        'preferences': 'Likes salty foods, garlic, familiar flavors'
    },
    'consultation_outcomes': {
        'date': '2024 consultation',
        'nutritionist_recommendations': {
            'sodium_limit': 1500,  # mg per day
            'calorie_target': 2000,  # kcal per day
            'exercise': '30 minutes walking, 5 times/week',
            'sleep': '7-8 hours, no screens after 11pm'
        },
        'agreed_changes': {
            'breakfast': 'Switch to whole grain toast + boiled egg + unsweetened soy milk',
            'lunch': 'Replace pork belly with steamed chicken/tofu, fresh veggies instead of pickled',
            'dinner': 'Order dry noodles or skip the broth',
            'cooking': 'Use vinegar, garlic, pepper, lemon; measure oil and salt',
            'monitoring': 'Send meal photos via LINE, track BP at home'
        },
        'family_support': 'Wife (Mrs. Lin) agreed to help with meal prep and join walks'
    },
    'dash_meal_plan': {
        'monday': {
            'breakfast': '全麥吐司2片 + 水煮蛋 + 無糖豆漿',
            'lunch': '清蒸雞胸肉 + 糙米飯 + 炒青江菜',
            'dinner': '烤鮭魚 + 地瓜 + 清炒菠菜',
            'snack': '蘋果1顆'
        },
        'tuesday': {
            'breakfast': '燕麥粥 + 堅果 + 香蕉',
            'lunch': '豆腐 + 紅豆飯 + 生菜沙拉',
            'dinner': '清燉雞湯 + 全麥麵 + 燙花椰菜',
            'snack': '無鹽堅果'
        },
        'wednesday': {
            'breakfast': '饅頭 + 茶葉蛋 + 低脂牛奶',
            'lunch': '蒸魚 + 五穀飯 + 炒高麗菜',
            'dinner': '香菇雞湯 + 冬粉 + 燙地瓜葉',
            'snack': '芭樂半顆'
        },
        'thursday': {
            'breakfast': '全麥吐司 + 水煮蛋 + 無糖豆漿',
            'lunch': '滷雞腿(去皮) + 糙米飯 + 燙空心菜',
            'dinner': '清蒸鱈魚 + 南瓜 + 炒小白菜',
            'snack': '優格一杯'
        },
        'friday': {
            'breakfast': '地瓜粥 + 荷包蛋 + 小黃瓜',
            'lunch': '豆干炒肉絲 + 紫米飯 + 炒A菜',
            'dinner': '番茄豆腐湯 + 陽春麵 + 燙青菜',
            'snack': '橘子1顆'
        },
        'saturday': {
            'breakfast': '鮪魚三明治(全麥) + 無糖紅茶',
            'lunch': '烤雞胸肉 + 馬鈴薯 + 生菜沙拉',
            'dinner': '乾麵 + 蒸蛋 + 燙菠菜(可以外食)',
            'snack': '堅果一小把'
        },
        'sunday': {
            'breakfast': '蔬菜蛋餅(少油) + 無糖豆漿',
            'lunch': '清蒸魚 + 糙米飯 + 炒青菜',
            'dinner': '火鍋(昆布湯底) + 大量蔬菜',
            'snack': '水果拼盤'
        }
    },
    'initial_greeting': """林先生您好！我是您的營養追蹤小幫手 😊

還記得上次營養師諮詢的計畫嗎？我會幫您：
✅ 追蹤每日飲食（特別是鈉攝取）
✅ 提醒您改吃全麥吐司配水煮蛋
✅ 記得牛肉麵不喝湯！
✅ 確保鈉控制在1500毫克以下
✅ 提醒每天走路30分鐘

林太太說會幫您準備健康餐點，太好了！
有任何問題都可以問我，或直接傳食物照片給我記錄哦～

輸入 /help 可以看所有指令
輸入 /today 看今天的營養摘要
輸入 /plan 查看一週飲食計畫""",
    'follow_up_reminders': [
        '記得牛肉麵不要喝湯哦！',
        '今天走路30分鐘了嗎？',
        '試試用大蒜和醋調味，取代醬油',
        '明天早餐來個全麥吐司如何？',
        '林太太準備的餐點有按時吃嗎？',
        'Amlodipine 吃了嗎？血壓有量嗎？'
    ]
}

# For backwards compatibility with existing code
HYPERTENSION_PROFILE = MR_LIN_PROFILE

def get_weekly_meal_plan():
    """Return formatted weekly DASH meal plan for Mr. Lin"""
    plan = MR_LIN_PROFILE['dash_meal_plan']
    
    meal_plan_text = """📅 林先生的一週DASH飲食計畫
━━━━━━━━━━━━━━━━━━━━━

🔑 飲食原則：
• 少鹽（鈉<1500mg/天）
• 多蔬果（天天5蔬5果）
• 選全穀雜糧
• 紅肉改白肉
• 補充堅果、用好油

"""
    
    days = {
        'monday': '週一',
        'tuesday': '週二', 
        'wednesday': '週三',
        'thursday': '週四',
        'friday': '週五',
        'saturday': '週六',
        'sunday': '週日'
    }
    
    for day_en, day_zh in days.items():
        if day_en in plan:
            meal_plan_text += f"【{day_zh}】\n"
            meal_plan_text += f"🌅 早餐：{plan[day_en]['breakfast']}\n"
            meal_plan_text += f"☀️ 午餐：{plan[day_en]['lunch']}\n"
            meal_plan_text += f"🌙 晚餐：{plan[day_en]['dinner']}\n"
            meal_plan_text += f"🍎 點心：{plan[day_en]['snack']}\n\n"
    
    meal_plan_text += """💡 小提醒：
• 外食時記得要求少鹽少油
• 湯麵改乾麵，湯另外裝
• 多喝水，每天至少2000cc
• 這是建議菜單，可依喜好調整

加油林先生！為了健康，我們一起努力 💪"""
    
    return meal_plan_text

def get_bp_log_format(user_id, bp_records):
    """Format blood pressure log for display"""
    if not bp_records:
        return """📊 血壓記錄

您還沒有血壓記錄哦！

請用以下格式記錄：
/bp 130/85

目標：<130/80
您目前服用：Amlodipine 5mg

記得每天早晚各量一次 📏"""
    
    log_text = """📊 林先生的血壓記錄
━━━━━━━━━━━━━━━

"""
    
    for record in bp_records[-7:]:  # Show last 7 records
        bp_value = record['value']
        date_time = record['datetime']
        systolic = int(bp_value.split('/')[0])
        
        # Add emoji based on BP level
        if systolic >= 140:
            emoji = "🔴"
            status = "偏高"
        elif systolic >= 130:
            emoji = "🟡"
            status = "稍高"
        else:
            emoji = "🟢"
            status = "正常"
        
        log_text += f"{emoji} {date_time}\n"
        log_text += f"   {bp_value} mmHg ({status})\n\n"
    
    log_text += """━━━━━━━━━━━━━━━
目標：<130/80
藥物：Amlodipine 5mg/天

💡 控制血壓小技巧：
• 減少鈉攝取
• 規律運動
• 充足睡眠
• 保持好心情"""
    
    return log_text

def get_mr_lin_context():
    """Return context for Mr. Lin's personalized responses"""
    return """
You are Mr. Lin's (林先生) personal nutrition tracking assistant following his consultation with the nutritionist.

**Background from consultation:**
- Mr. Lin is 55, overweight (BMI 27), has hypertension (145/92)
- Takes Amlodipine 5mg daily, very worried about stroke (father had stroke in 60s)
- Previous diet: 油條+甜豆漿 breakfast, 滷肉飯 lunch, 牛肉麵(喝湯) dinner, chips & bubble tea snacks
- Baseline sodium: ~4000mg/day (way over limit!)
- Sedentary lifestyle, only walks on weekends with wife

**What Mr. Lin agreed to change:**
1. Breakfast: 全麥吐司+水煮蛋 instead of 油條
2. Lunch: 清蒸雞肉/豆腐 instead of 滷肉
3. Dinner: 乾麵 or skip the beef noodle broth
4. Cooking: Mrs. Lin (林太太) will use herbs/spices instead of soy sauce
5. Exercise: 30-min walks 5x/week (can extend dog walking time)
6. Monitoring: Send meal photos, track BP at home

**Your personality:**
- You know his full history from the consultation
- Always reference specific agreements ("記得你答應要...")
- Use his father's stroke as gentle motivation
- Mention Mrs. Lin's support when relevant
- Be encouraging but firm about sodium limits
- Use Taiwanese food terms naturally
- Remember he loves garlic (大蒜) and wants flavor

**Response style:**
- Friendly but concerned, like a caring health companion
- Use casual Taiwanese Mandarin (哦、啊、欸、吼)
- Give specific alternatives, not generic advice
- Always relate back to his personal goals and fears
"""

def get_hypertension_context():
    """Wrapper for compatibility"""
    return get_mr_lin_context()

def check_food_for_mr_lin(food_item, nutrition_data):
    """Analyze if food is appropriate for Mr. Lin specifically"""
    warnings = []
    suggestions = []
    
    # Check sodium
    sodium = nutrition_data.get('sodium', 0)
    if sodium > 600:
        warnings.append(f"⚠️ 鈉含量高：{sodium}毫克！記得您爸爸的事...我們要控制血壓哦")
        suggestions.append("下次試試少鹽版本，或是用大蒜、醋調味")
    elif sodium > 400:
        warnings.append(f"📊 鈉含量中等：{sodium}毫克，其他餐要清淡一點")
    
    # Check for Mr. Lin's specific trigger foods
    food_lower = food_item.lower()
    
    if '油條' in food_item:
        warnings.append("😅 林先生！您又吃油條了...記得要改全麥吐司嗎？")
        suggestions.append("明天請林太太幫您準備全麥吐司+水煮蛋")
    
    if '滷肉' in food_item or '肥肉' in food_item:
        warnings.append("這個油脂太高了！您的LDL已經160了")
        suggestions.append("試試清蒸雞胸肉或豆腐，一樣好吃")
    
    if '牛肉麵' in food_item:
        warnings.append("牛肉麵可以，但湯千萬別喝！一碗湯就超標了")
        suggestions.append("點乾麵，或是湯另外裝，意思意思喝兩口就好")
    
    if '醃' in food_item or '泡菜' in food_item:
        warnings.append("醃漬品鈉含量超高！要少吃")
        suggestions.append("改吃新鮮蔬菜，用蒜爆香一樣美味")
    
    # Positive reinforcement for good choices
    good_keywords = ['全麥', '水煮', '清蒸', '燙', '烤', '新鮮']
    for keyword in good_keywords:
        if keyword in food_item:
            suggestions.append("👍 很好的選擇！這樣吃對血壓有幫助")
            break
    
    return warnings, suggestions

# Backwards compatibility
def check_food_for_hypertension(food_item, nutrition_data):
    return check_food_for_mr_lin(food_item, nutrition_data)