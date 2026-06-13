from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from locales import get_text
from config import PAYMENT_AMOUNTS, PPT_DESIGNS, PPT_SLIDES


def get_language_kb() -> InlineKeyboardMarkup:
    """Language selection keyboard."""
    buttons = [
        [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_services_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    """Service categories keyboard."""
    buttons = [
        [InlineKeyboardButton(text=get_text("btn_ai_services", lang), callback_data="cat_ai")],
        [InlineKeyboardButton(text=get_text("btn_admin_services", lang), callback_data="cat_admin")],
        [InlineKeyboardButton(text=get_text("btn_back", lang), callback_data="back_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_ai_services_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    """AI services keyboard."""
    builder = InlineKeyboardBuilder()
    services = [
        ("btn_ppt", "svc_ppt"),
        ("btn_referat", "svc_referat"),
        ("btn_mustaqil", "svc_mustaqil"),
        ("btn_esse", "svc_esse"),
        ("btn_tarjima", "svc_tarjima"),
        ("btn_qr", "svc_qr"),
        ("btn_ai_text", "svc_ai_text"),
        ("btn_ai_content", "svc_ai_content"),
        ("btn_speech", "svc_speech"),
        ("btn_banner", "svc_banner"),
    ]
    for text_key, callback in services:
        builder.button(text=get_text(text_key, lang), callback_data=callback)
    builder.button(text=get_text("btn_back", lang), callback_data="back_services")
    builder.adjust(2)
    return builder.as_markup()


def get_admin_services_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    """Admin services keyboard."""
    builder = InlineKeyboardBuilder()
    services = [
        ("btn_cv", "adm_cv"),
        ("btn_resume", "adm_resume"),
        ("btn_internet", "adm_internet"),
        ("btn_mygov", "adm_mygov"),
        ("btn_hisobot", "adm_hisobot"),
        ("btn_diplom", "adm_diplom"),
        ("btn_sertifikat", "adm_sertifikat"),
        ("btn_vizitka", "adm_vizitka"),
        ("btn_tg_post", "adm_tg_post"),
        ("btn_reklama", "adm_reklama"),
        ("btn_menu_design", "adm_menu_design"),
        ("btn_logo", "adm_logo"),
    ]
    for text_key, callback in services:
        builder.button(text=get_text(text_key, lang), callback_data=callback)
    builder.button(text=get_text("btn_back", lang), callback_data="back_services")
    builder.adjust(2)
    return builder.as_markup()


def get_ppt_design_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    """PPT design selection keyboard."""
    builder = InlineKeyboardBuilder()
    for design in PPT_DESIGNS:
        builder.button(text=f"🎨 {design}", callback_data=f"ppt_design_{design.lower()}")
    builder.button(text=get_text("btn_cancel", lang), callback_data="cancel_order")
    builder.adjust(2)
    return builder.as_markup()


def get_ppt_purpose_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    """PPT purpose selection keyboard."""
    buttons = [
        [InlineKeyboardButton(text=get_text("ppt_purpose_university", lang), callback_data="ppt_purp_university")],
        [InlineKeyboardButton(text=get_text("ppt_purpose_business", lang), callback_data="ppt_purp_business")],
        [InlineKeyboardButton(text=get_text("ppt_purpose_report", lang), callback_data="ppt_purp_report")],
        [InlineKeyboardButton(text=get_text("ppt_purpose_startup", lang), callback_data="ppt_purp_startup")],
        [InlineKeyboardButton(text=get_text("ppt_purpose_educational", lang), callback_data="ppt_purp_educational")],
        [InlineKeyboardButton(text=get_text("btn_cancel", lang), callback_data="cancel_order")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_ppt_lang_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    """PPT language selection keyboard."""
    buttons = [
        [InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="ppt_lang_uz")],
        [InlineKeyboardButton(text="🇷🇺 Rus", callback_data="ppt_lang_ru")],
        [InlineKeyboardButton(text="🇬🇧 Ingliz", callback_data="ppt_lang_en")],
        [InlineKeyboardButton(text=get_text("btn_cancel", lang), callback_data="cancel_order")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_ppt_slides_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    """PPT slides count selection keyboard."""
    builder = InlineKeyboardBuilder()
    for count in PPT_SLIDES:
        builder.button(text=str(count), callback_data=f"ppt_slides_{count}")
    builder.button(text=get_text("btn_cancel", lang), callback_data="cancel_order")
    builder.adjust(3)
    return builder.as_markup()


def get_confirm_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    """Confirm/cancel keyboard."""
    buttons = [
        [
            InlineKeyboardButton(text=get_text("btn_confirm", lang), callback_data="confirm_order"),
            InlineKeyboardButton(text=get_text("btn_cancel", lang), callback_data="cancel_order"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_payment_amounts_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    """Payment amounts keyboard."""
    builder = InlineKeyboardBuilder()
    for amount in PAYMENT_AMOUNTS:
        text = f"{amount:,} so'm".replace(",", " ")
        builder.button(text=text, callback_data=f"pay_amount_{amount}")
    builder.button(text=get_text("btn_cancel", lang), callback_data="cancel_payment")
    builder.adjust(3)
    return builder.as_markup()


def get_payment_method_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    """Payment method keyboard — faqat bank karta."""
    buttons = [
        [InlineKeyboardButton(text=get_text("btn_bank_card", lang), callback_data="pay_method_card")],
        [InlineKeyboardButton(text=get_text("btn_cancel", lang), callback_data="cancel_payment")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_buy_now_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    """Balans yetmaganda — 'Sotib olish' tugmasi."""
    buttons = [
        [InlineKeyboardButton(text=get_text("btn_buy_now", lang), callback_data="open_buy")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_yes_no_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    """Yes/No keyboard."""
    buttons = [
        [
            InlineKeyboardButton(text=get_text("btn_yes", lang), callback_data="answer_yes"),
            InlineKeyboardButton(text=get_text("btn_no", lang), callback_data="answer_no"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_rating_kb() -> InlineKeyboardMarkup:
    """Rating keyboard."""
    buttons = [[
        InlineKeyboardButton(text="⭐", callback_data="rate_1"),
        InlineKeyboardButton(text="⭐⭐", callback_data="rate_2"),
        InlineKeyboardButton(text="⭐⭐⭐", callback_data="rate_3"),
        InlineKeyboardButton(text="⭐⭐⭐⭐", callback_data="rate_4"),
        InlineKeyboardButton(text="⭐⭐⭐⭐⭐", callback_data="rate_5"),
    ]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_esse_type_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    """Essay type keyboard."""
    buttons = [
        [InlineKeyboardButton(text=get_text("esse_type_argumentative", lang), callback_data="esse_argumentative")],
        [InlineKeyboardButton(text=get_text("esse_type_descriptive", lang), callback_data="esse_descriptive")],
        [InlineKeyboardButton(text=get_text("esse_type_narrative", lang), callback_data="esse_narrative")],
        [InlineKeyboardButton(text=get_text("esse_type_analytical", lang), callback_data="esse_analytical")],
        [InlineKeyboardButton(text=get_text("btn_cancel", lang), callback_data="cancel_order")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_esse_words_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    """Essay word count keyboard."""
    builder = InlineKeyboardBuilder()
    for count in [300, 500, 700, 1000, 1500, 2000]:
        builder.button(text=str(count), callback_data=f"esse_words_{count}")
    builder.button(text=get_text("btn_cancel", lang), callback_data="cancel_order")
    builder.adjust(3)
    return builder.as_markup()


def get_qr_design_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    """QR Code design keyboard."""
    buttons = [
        [InlineKeyboardButton(text="⬜ Oddiy", callback_data="qr_design_simple")],
        [InlineKeyboardButton(text="🔲 Minimal", callback_data="qr_design_minimal")],
        [InlineKeyboardButton(text="💼 Business", callback_data="qr_design_business")],
        [InlineKeyboardButton(text="✨ Premium", callback_data="qr_design_premium")],
        [InlineKeyboardButton(text=get_text("btn_cancel", lang), callback_data="cancel_order")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ===== ADMIN KEYBOARDS =====

def get_admin_panel_kb() -> InlineKeyboardMarkup:
    """Admin panel main keyboard."""
    buttons = [
        [InlineKeyboardButton(text="📊 Dashboard", callback_data="admin_dashboard")],
        [InlineKeyboardButton(text="📦 Buyurtmalar", callback_data="admin_orders")],
        [InlineKeyboardButton(text="💳 To'lovlar", callback_data="admin_payments")],
        [InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="admin_users")],
        [InlineKeyboardButton(text="🎁 Bonuslar", callback_data="admin_bonuses")],
        [InlineKeyboardButton(text="🎫 Promo kodlar", callback_data="admin_promos")],
        [InlineKeyboardButton(text="📢 Xabarnoma yuborish", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="admin_settings")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_admin_order_kb(order_id: int) -> InlineKeyboardMarkup:
    """Admin order management keyboard."""
    buttons = [
        [
            InlineKeyboardButton(text="✅ Qabul", callback_data=f"adm_accept_{order_id}"),
            InlineKeyboardButton(text="❌ Rad", callback_data=f"adm_reject_{order_id}"),
        ],
        [InlineKeyboardButton(text="📎 Fayl yuklash", callback_data=f"adm_upload_{order_id}")],
        [InlineKeyboardButton(text="🔵 Jarayonda", callback_data=f"adm_progress_{order_id}")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_admin_payment_kb(payment_id: int) -> InlineKeyboardMarkup:
    """Admin payment confirmation keyboard."""
    buttons = [
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"pay_confirm_{payment_id}"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"pay_reject_{payment_id}"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
