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

# Web App (Mini App) — taqdimot yaratish web oynasi
# Sayt deploy qilingach (Netlify/GitHub Pages), shu manzilni .env ga yozing
# Masalan: WEBAPP_URL=https://master-student.netlify.app/app/
WEBAPP_URL = os.getenv("WEBAPP_URL", "")

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

# Pixabay API — Pexels ishlamasa zaxira rasm manbasi (IXTIYORIY, bepul)
# Bepul kalit: https://pixabay.com/api/docs/
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "")

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

# PPT Designs (15 ta)
PPT_DESIGNS = [
    "Business", "Minimal", "Dark", "Modern", "Education",
    "Corporate", "Startup", "Creative", "Elegant", "Premium",
    "Ocean", "Sunset", "Forest", "Royal", "Neon"
]

# PPT Purposes
PPT_PURPOSES = [
    "university", "business", "report", "startup", "educational"
]

# PPT Slide counts
PPT_SLIDES = [5, 10, 15, 20, 25, 30]

# Hujjat (referat/mustaqil ish) varoq oralig'i va narxlari
# 10-15 dan boshlanadi, 25-30 gacha (skrinshotdagidek)
DOC_PAGE_OPTIONS = [
    ("p_10_15", "10-15 sahifa", 15,  3000),
    ("p_15_20", "15-20 sahifa", 20,  4000),
    ("p_20_25", "20-25 sahifa", 25,  5000),
    ("p_25_30", "25-30 sahifa", 30,  6000),
]

# Service prices (in so'm)
# Taqdimot Standart: 6-19 slayd=3000, 20-30 slayd=5000
# Taqdimot Premium (PRO, rasmli): 6-19 slayd=6000, 20-30 slayd=8000
PRICES = {
    "ppt_5": 3000,
    "ppt_10": 3000,
    "ppt_15": 3000,
    "ppt_20": 5000,
    "ppt_25": 5000,
    "ppt_30": 5000,
    # Taqdimot PRO (Premium — rasmli, boy ma'lumot)
    "ppt_pro_5": 6000,
    "ppt_pro_10": 6000,
    "ppt_pro_15": 6000,
    "ppt_pro_20": 8000,
    "ppt_pro_25": 8000,
    "ppt_pro_30": 8000,
    "referat": 3000,
    "mustaqil_ish": 3000,
    "referat_premium": 5000,
    "mustaqil_ish_premium": 5000,
    "esse": 2000,
    "tarjima_page": 1500,
    "qr_code": 1000,
    "ai_text": 2000,
    "ai_content": 3000,
    "speech": 3000,
    "banner_post": 4000,
    # Admin services (narx admin bilan kelishiladi — bu faqat ko'rsatkich)
    "cv": 20000,
    "resume": 20000,
    "internet": 10000,
    "mygov": 15000,
    "hisobot": 25000,
    "diplom_design": 30000,
    "sertifikat": 20000,
    "vizitka": 15000,
    "telegram_post": 12000,
    "reklama_banner": 15000,
    "menu_design": 20000,
    "logo": 30000,
}
