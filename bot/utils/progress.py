"""
EVA Progress Bar — kutish paytida animatsiyali progress va maslahatlar.
"""
import asyncio
import random
from aiogram.types import Message


# Har safar har xil maslahatlar
TIPS_UZ = [
    "☕ Shu vaqtda bir piyola choy ichib turing...",
    "💧 Suv ichishni unutmang — salomatlik uchun muhim!",
    "🧘 Nafas rostlab, dam olib turing...",
    "📱 Shu orada boshqa ishlaringizni hal qilib turing",
    "🌿 Bir oz turib, ko'zlaringizni dam bering...",
    "🎵 Yoqimli musiqa eshitib turing...",
    "✨ Yaxshi natija kutish — sabr bilan bo'ladi!",
    "🍎 Meva yeb turing — sog'liq uchun foydali!",
    "📖 Kitob o'qib turing — bilim hech qachon ko'p bo'lmaydi",
    "🏃 Bir oz harakatlanib turing — tanaga foydali!",
    "🌅 Derazadan tashqariga qarang — tabiat go'zal!",
    "💪 Siz zo'rsiz! EVA sizga eng yaxshi natijani tayyorlamoqda",
    "🤝 Do'stlaringizga ham botimizni tavsiya qiling!",
    "🎯 Maqsadingizga yana bir qadam yaqinlashdingiz!",
    "🌟 Sabr — muvaffaqiyat kaliti!",
]

TIPS_RU = [
    "☕ Пока можете выпить чашку чая...",
    "💧 Не забудьте выпить воды — это важно для здоровья!",
    "🧘 Расслабьтесь и подышите...",
    "📱 Можете пока заняться другими делами",
    "🌿 Дайте отдохнуть глазам...",
    "🎵 Послушайте приятную музыку...",
    "✨ Хороший результат стоит ожидания!",
]

TIPS_EN = [
    "☕ Grab a cup of tea while you wait...",
    "💧 Don't forget to drink some water!",
    "🧘 Take a deep breath and relax...",
    "📱 Feel free to handle other tasks meanwhile",
    "🌿 Give your eyes a little rest...",
    "🎵 Listen to some nice music...",
    "✨ Good things come to those who wait!",
]

TIPS = {"uz": TIPS_UZ, "ru": TIPS_RU, "en": TIPS_EN}

# Progress bar uchun shakl
PROGRESS_STAGES = [
    ("🟢⚪⚪⚪⚪⚪⚪⚪⚪⚪", "10%", "Reja tuzilmoqda..."),
    ("🟢🟢⚪⚪⚪⚪⚪⚪⚪⚪", "20%", "Kirish yozilmoqda..."),
    ("🟢🟢🟢⚪⚪⚪⚪⚪⚪⚪", "30%", "1-bo'lim yaratilmoqda..."),
    ("🟢🟢🟢🟢⚪⚪⚪⚪⚪⚪", "40%", "2-bo'lim yaratilmoqda..."),
    ("🟢🟢🟢🟢🟢⚪⚪⚪⚪⚪", "50%", "3-bo'lim yaratilmoqda..."),
    ("🟢🟢🟢🟢🟢🟢⚪⚪⚪⚪", "60%", "4-bo'lim yaratilmoqda..."),
    ("🟢🟢🟢🟢🟢🟢🟢⚪⚪⚪", "70%", "Xulosa yozilmoqda..."),
    ("🟢🟢🟢🟢🟢🟢🟢🟢⚪⚪", "80%", "Adabiyotlar qo'shilmoqda..."),
    ("🟢🟢🟢🟢🟢🟢🟢🟢🟢⚪", "90%", "Formatlash..."),
    ("🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢", "100%", "Tayyor! 🎉"),
]

PPT_PROGRESS_STAGES = [
    ("🟢⚪⚪⚪⚪⚪⚪⚪⚪⚪", "10%", "Slaydlar rejasi tuzilmoqda..."),
    ("🟢🟢🟢⚪⚪⚪⚪⚪⚪⚪", "30%", "Kontent yaratilmoqda..."),
    ("🟢🟢🟢🟢🟢⚪⚪⚪⚪⚪", "50%", "Dizayn qo'llanilmoqda..."),
    ("🟢🟢🟢🟢🟢🟢🟢⚪⚪⚪", "70%", "Slaydlar shakllantirilmoqda..."),
    ("🟢🟢🟢🟢🟢🟢🟢🟢🟢⚪", "90%", "Yakuniy tekshiruv..."),
    ("🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢", "100%", "Tayyor! 🎉"),
]


def get_random_tip(lang: str = "uz") -> str:
    """Tasodifiy maslahat qaytaradi."""
    tips = TIPS.get(lang, TIPS_UZ)
    return random.choice(tips)


async def show_progress(message: Message, lang: str = "uz", is_ppt: bool = False):
    """
    Animatsiyali progress bar ko'rsatadi.
    Bu funksiya alohida task sifatida ishga tushiriladi.
    """
    stages = PPT_PROGRESS_STAGES if is_ppt else PROGRESS_STAGES
    
    for i, (bar, percent, status) in enumerate(stages[:-1]):  # Oxirgi 100% ni ko'rsatmaymiz (fayl kelganda ko'rinadi)
        tip = get_random_tip(lang)
        text = (
            f"🤖 <b>EVA ishlamoqda...</b>\n\n"
            f"{bar} <b>{percent}</b>\n"
            f"📋 {status}\n\n"
            f"💬 <i>{tip}</i>"
        )
        try:
            await message.edit_text(text, parse_mode="HTML")
        except Exception:
            pass  # Xabar o'zgartirib bo'lmasa - o'tkazib yuboramiz
        
        # Har bir bosqich orasida kutish
        if is_ppt:
            await asyncio.sleep(8)  # PPT uchun
        else:
            await asyncio.sleep(6)  # Document uchun


async def start_progress_task(message: Message, lang: str = "uz", is_ppt: bool = False) -> asyncio.Task:
    """Progress bar'ni background task sifatida ishga tushiradi."""
    task = asyncio.create_task(show_progress(message, lang, is_ppt))
    return task


def stop_progress_task(task: asyncio.Task):
    """Progress task'ni to'xtatadi."""
    if task and not task.done():
        task.cancel()
