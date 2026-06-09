from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

import database as db
from config import NEW_USER_BONUS
from locales import get_text
from keyboards.inline_kb import get_language_kb
from keyboards.main_kb import get_main_menu_kb

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Handle /start command."""
    user_id = message.from_user.id
    username = message.from_user.username or ""
    full_name = message.from_user.full_name or ""
    
    # Check for referral
    referred_by = None
    args = message.text.split()
    if len(args) > 1:
        try:
            referred_by = int(args[1])
            if referred_by == user_id:
                referred_by = None
        except ValueError:
            referred_by = None
    
    # Check if user exists
    user = await db.get_user(user_id)
    
    if not user:
        # New user
        await db.create_user(user_id, username, full_name, referred_by)
        
        # Give new user bonus
        await db.add_bonus(user_id, NEW_USER_BONUS, "new_user_bonus")
        
        # Process referral
        if referred_by:
            referrer = await db.get_user(referred_by)
            if referrer:
                await db.add_referral(referred_by, user_id)
                await db.add_bonus(referred_by, 1000, "referral")
        
        # Show language selection
        await message.answer(
            "🌐 Tilni tanlang / Выберите язык / Choose language:",
            reply_markup=get_language_kb()
        )
    else:
        # Returning user
        lang = user["language"]
        await message.answer(
            get_text("welcome_back", lang),
            reply_markup=get_main_menu_kb(lang),
            parse_mode="HTML"
        )


@router.callback_query(F.data.startswith("lang_"))
async def set_language(callback: CallbackQuery):
    """Handle language selection."""
    lang = callback.data.split("_")[1]
    user_id = callback.from_user.id
    
    await db.update_user_language(user_id, lang)
    
    # Check if new user (just registered)
    user = await db.get_user(user_id)
    
    await callback.message.delete()
    
    if user and user["bonus"] == NEW_USER_BONUS and user["total_orders"] == 0:
        # New user - show welcome
        await callback.message.answer(
            get_text("welcome", lang),
            reply_markup=get_main_menu_kb(lang),
            parse_mode="HTML"
        )
    else:
        # Language change
        await callback.message.answer(
            get_text("language_set", lang),
            reply_markup=get_main_menu_kb(lang),
            parse_mode="HTML"
        )
    
    await callback.answer()
