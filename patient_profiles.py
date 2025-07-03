# Mr. Lin baseline info + helpers
MR_LIN_PROFILE = {
    "initial_greeting": "林先生您好！我是您的營養追蹤助手 😊\n輸入 /help 看指令",
    "dash_meal_plan": {
        "monday": {
            "breakfast": "全麥吐司+水煮蛋+無糖豆漿",
            "lunch": "清蒸雞胸肉+糙米飯+炒青江菜",
            "dinner": "烤鮭魚+地瓜+清炒菠菜",
            "snack": "蘋果一顆",
        },
        # …省略其餘 6 天，如需完整菜單照舊填
    },
}

def get_weekly_meal_plan():
    plan = MR_LIN_PROFILE["dash_meal_plan"]
    txt = "📅 一週 DASH 菜單\n"
    zh = ["週一", "週二", "週三", "週四", "週五", "週六", "週日"]
    for d, day in zip(plan.values(), zh):
        txt += f"\n【{day}】\n🌅 {d['breakfast']}\n☀️ {d['lunch']}\n🌙 {d['dinner']}\n🍎 {d['snack']}\n"
    return txt


def get_bp_log_format(uid, records):
    if not records:
        return "尚無血壓記錄，使用 /bp 130/85 來記錄"
    txt = "📊 最近血壓:\n"
    for r in records[-7:]:
        txt += f"{r['datetime']}  {r['value']}\n"
    return txt
