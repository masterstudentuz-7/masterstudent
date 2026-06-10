from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import database as db
from config import SUPPORT_USERNAME, CHANNEL_ID, BANK_CARD
from locales import get_text
from keyboards.main_kb import get_main_menu_kb, get_back_kb, get_contact_kb
from keyboards.inline_kb import get_language_kb, get_services_kb

router = Router()


@router.message(F.text.in_(["🛒 Xizmatlar", "🛒 Услуги", "🛒 Services"]))
async def menu_services(message: Message, state: FSMContext):
    """Show services menu."""
    await state.clear()  # Oldingi jarayonni bekor qilish
    lang = await db.get_user_language(message.from_user.id)
    await message.answer(
        get_text("services_title", lang),
        reply_markup=get_services_kb(lang),
        parse_mode="HTML"
    )


@router.message(F.text.in_(["📦 Buyurtmalarim", "📦 Мои заказы", "📦 My Orders"]))
async def menu_my_orders(message: Message, state: FSMContext):
    """Show user orders."""
    await state.clear()
    user_id = message.from_user.id
    lang = await db.get_user_language(user_id)
    
    orders = await db.get_user_orders(user_id)
    
    if not orders:
        await message.answer(get_text("no_orders", lang), parse_mode="HTML")
        return
    
    text = get_text("my_orders_title", lang)
    status_map = {
        "pending": "status_pending",
        "accepted": "status_accepted",
        "in_progress": "status_in_progress",
        "ready": "status_ready",
        "completed": "status_completed",
        "cancelled": "status_cancelled",
        "creating": "status_creating",
    }
    
    for order in orders[:15]:
        status_key = status_map.get(order["status"], "status_pending")
        status_text = get_text(status_key, lang)
        text += get_text("order_item", lang,
                         id=order["order_id"],
                         service=order["service_name"],
                         price=order["price"],
                         status=status_text)
    
    await message.answer(text, parse_mode="HTML")


@router.message(F.text.in_(["📂 Mening fayllarim", "📂 Мои файлы", "📂 My Files"]))
async def menu_my_files(message: Message, state: FSMContext):
    """Show user files."""
    await state.clear()
    user_id = message.from_user.id
    lang = await db.get_user_language(user_id)
    
    files = await db.get_user_files(user_id)
    
    if not files:
        await message.answer(get_text("no_files", lang), parse_mode="HTML")
        return
    
    text = get_text("my_files_title", lang)
    for f in files[:20]:
        text += f"📄 {f['file_name']}\n"
    
    await message.answer(text, parse_mode="HTML")
    
    # Send files
    for f in files[:10]:
        try:
            await message.answer_document(f["telegram_file_id"])
        except Exception:
            pass


@router.message(F.text.in_(["💳 Balans", "💳 Баланс", "💳 Balance"]))
async def menu_balance(message: Message, state: FSMContext):
    """Show balance info."""
    await state.clear()
    user_id = message.from_user.id
    lang = await db.get_user_language(user_id)
    user = await db.get_user(user_id)
    
    if not user:
        return
    
    await message.answer(
        get_text("balance_info", lang,
                 balance=user["balance"],
                 bonus=user["bonus"],
                 total_spent=user["total_spent"],
                 total_orders=user["total_orders"]),
        parse_mode="HTML"
    )


@router.message(F.text.in_(["🎁 Referal", "🎁 Реферал", "🎁 Referral"]))
async def menu_referral(message: Message, state: FSMContext):
    """Show referral info."""
    await state.clear()
    user_id = message.from_user.id
    lang = await db.get_user_language(user_id)
    
    bot_info = await message.bot.get_me()
    link = f"https://t.me/{bot_info.username}?start={user_id}"
    count = await db.get_referral_count(user_id)
    
    await message.answer(
        get_text("referral_info", lang, link=link, count=count),
        parse_mode="HTML"
    )


@router.message(F.text.in_(["📢 Aksiyalar", "📢 Акции", "📢 Promotions"]))
async def menu_promotions(message: Message, state: FSMContext):
    """Show promotions."""
    await state.clear()
    lang = await db.get_user_language(message.from_user.id)
    await message.answer(get_text("promotions_title", lang), parse_mode="HTML")


@router.message(F.text.in_(["🌐 Til o'zgartirish", "🌐 Сменить язык", "🌐 Change Language"]))
async def menu_change_language(message: Message, state: FSMContext):
    """Show language selection."""
    await state.clear()
    lang = await db.get_user_language(message.from_user.id)
    await message.answer(
        get_text("choose_language", lang),
        reply_markup=get_language_kb()
    )


@router.message(F.text.in_(["🎗 Donat", "🎗 Донат", "🎗 Donate"]))
async def menu_donate(message: Message, state: FSMContext):
    """Show donate info."""
    await state.clear()
    lang = await db.get_user_language(message.from_user.id)
    await message.answer(
        get_text("donate_info", lang, card=BANK_CARD),
        parse_mode="HTML"
    )


@router.message(F.text.in_(["ℹ️ Haqimizda", "ℹ️ О нас", "ℹ️ About Us"]))
async def menu_about(message: Message, state: FSMContext):
    """Show about info."""
    await state.clear()
    lang = await db.get_user_language(message.from_user.id)
    await message.answer(
        get_text("about_info", lang, support=SUPPORT_USERNAME, channel=CHANNEL_ID),
        parse_mode="HTML"
    )


@router.message(F.text.in_(["📞 Bog'lanish", "📞 Связаться", "📞 Contact"]))
async def menu_contact(message: Message, state: FSMContext):
    """Show contact options."""
    await state.clear()
    lang = await db.get_user_language(message.from_user.id)
    await message.answer(
        get_text("contact_info", lang),
        reply_markup=get_contact_kb(lang),
        parse_mode="HTML"
    )


@router.message(F.text.in_(["📞 Admin", "📞 Админ", "📞 Admin"]))
async def contact_admin(message: Message):
    """Contact admin."""
    lang = await db.get_user_language(message.from_user.id)
    await message.answer(
        get_text("contact_admin_text", lang, support=SUPPORT_USERNAME),
        parse_mode="HTML"
    )


@router.message(F.text.in_(["💬 Taklif yuborish", "💬 Предложение", "💬 Suggestion"]))
async def contact_suggestion(message: Message, state):
    """Send suggestion."""
    from aiogram.fsm.context import FSMContext
    lang = await db.get_user_language(message.from_user.id)
    await message.answer(
        get_text("suggestion_prompt", lang),
        reply_markup=get_back_kb(lang),
        parse_mode="HTML"
    )


@router.message(F.text.in_(["⚠️ Muammo xabari", "⚠️ Сообщить о проблеме", "⚠️ Report Issue"]))
async def contact_report(message: Message):
    """Report issue."""
    lang = await db.get_user_language(message.from_user.id)
    await message.answer(
        get_text("report_prompt", lang),
        reply_markup=get_back_kb(lang),
        parse_mode="HTML"
    )


@router.message(F.text.in_(["📢 Kanal", "📢 Канал", "📢 Channel"]))
async def contact_channel(message: Message):
    """Show channel link."""
    lang = await db.get_user_language(message.from_user.id)
    await message.answer(
        get_text("channel_link", lang, channel=CHANNEL_ID),
        parse_mode="HTML"
    )


@router.message(F.text.in_(["👤 Profil", "👤 Профиль", "👤 Profile"]))
async def menu_profile(message: Message, state: FSMContext):
    """Show user profile."""
    await state.clear()
    user_id = message.from_user.id
    lang = await db.get_user_language(user_id)
    user = await db.get_user(user_id)
    
    if not user:
        return
    
    premium_names = {
        "free": "Free",
        "silver": "Silver 🥈",
        "gold": "Gold 🥇",
        "premium": "Premium 💎",
    }
    
    await message.answer(
        get_text("profile_info", lang,
                 user_id=user_id,
                 username=user["username"] or "N/A",
                 balance=user["balance"],
                 bonus=user["bonus"],
                 referrals=user["referral_count"],
                 orders=user["total_orders"],
                 total_spent=user["total_spent"],
                 premium=premium_names.get(user["premium_plan"], "Free")),
        parse_mode="HTML"
    )


@router.message(F.text.in_(["⬅️ Ortga", "⬅️ Назад", "⬅️ Back"]))
async def menu_back(message: Message, state: FSMContext):
    """Go back to main menu — HAR QANDAY state'dan chiqadi."""
    await state.clear()  # Barcha jarayonlarni bekor qilish
    lang = await db.get_user_language(message.from_user.id)
    await message.answer(
        get_text("main_menu", lang),
        reply_markup=get_main_menu_kb(lang),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "back_menu")
async def callback_back_menu(callback: CallbackQuery):
    """Back to main menu from inline."""
    lang = await db.get_user_language(callback.from_user.id)
    await callback.message.delete()
    await callback.message.answer(
        get_text("main_menu", lang),
        reply_markup=get_main_menu_kb(lang),
        parse_mode="HTML"
    )
    await callback.answer()
