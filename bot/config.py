import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
PAYME_TOKEN = os.getenv("PAYME_TOKEN", "")
CLICK_TOKEN = os.getenv("CLICK_TOKEN", "")
BANK_CARD = os.getenv("BANK_CARD", "8600000000000000")
CARD_HOLDER = os.getenv("CARD_HOLDER", "Familiya Ism")
CHANNEL_ID = os.getenv("CHANNEL_ID", "")
SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "@admin")

# ===== AI PROVIDER SETTINGS =====
# Active provider: "gemini" or "openai"
AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini")

# Gemini (Google) - ASOSIY (hozir ishlamoqda)
# Bir nechta API key qo'yish mumkin — vergul bilan ajratiladi
# Masalan: GEMINI_API_KEY=key1,key2,key3
# Bitta key limiti tugasa keyingisiga o'tadi
GEMINI_API_KEYS = [k.strip() for k in os.getenv("GEMINI_API_KEY", "").split(",") if k.strip()]
GEMINI_API_KEY = GEMINI_API_KEYS[0] if GEMINI_API_KEYS else ""
GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
]

# OpenAI - O'CHIRILGAN (kelajakda ishlatiladi)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Pexels API — slaydlarga real rasmlar qo'shish uchun (IXTIYORIY)
# Bepul kalit: https://www.pexels.com/api/
# Agar bo'sh bo'lsa, slaydlar chiroyli dizayn elementlari bilan yaratiladi
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")

# Database
DB_PATH = "database.db"

# Bonus settings
NEW_USER_BONUS = 6000
REFERRAL_REWARDS = {1: 1000, 5: 5000, 10: 10000, 20: 20000}
PURCHASE_BONUS_THRESHOLD = 100000
PURCHASE_BONUS_AMOUNT = 5000

# Premium plans
PREMIUM_PLANS = {
    "silver": {"name": "Silver 🥈", "discount": 5, "bonus_multiplier": 1.2},
    "gold": {"name": "Gold 🥇", "discount": 10, "bonus_multiplier": 1.5},
    "premium": {"name": "Premium 💎", "discount": 15, "bonus_multiplier": 2.0},
}

# Payment amounts
PAYMENT_AMOUNTS = [
    3000, 6000, 9000, 12000, 15000, 18000, 21000,
    30000, 39000, 49000, 59000, 69000, 79000, 89000,
    99000, 101000
]

# PPT Designs
PPT_DESIGNS = [
    "Business", "Minimal", "Dark", "Modern", "Education",
    "Corporate", "Startup", "Creative", "Elegant", "Premium"
]

# PPT Purposes
PPT_PURPOSES = [
    "university", "business", "report", "startup", "educational"
]

# PPT Slide counts
PPT_SLIDES = [5, 10, 15, 20, 25, 30]

# Service prices (in so'm)
PRICES = {
    "ppt_5": 5000,
    "ppt_10": 8000,
    "ppt_15": 12000,
    "ppt_20": 15000,
    "ppt_25": 18000,
    "ppt_30": 22000,
    "referat": 10000,
    "mustaqil_ish": 10000,
    "esse": 5000,
    "tarjima_page": 3000,
    "qr_code": 2000,
    "ai_text": 5000,
    "ai_content": 7000,
    "speech": 8000,
    "banner_post": 10000,
    # Admin services
    "cv": 25000,
    "resume": 25000,
    "internet": 15000,
    "mygov": 20000,
    "hisobot": 30000,
    "diplom_design": 35000,
    "sertifikat": 25000,
    "vizitka": 20000,
    "telegram_post": 15000,
    "reklama_banner": 20000,
    "menu_design": 25000,
    "logo": 40000,
}
