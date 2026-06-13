from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from locales import get_text


def get_main_menu_kb(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Get the main menu keyboard."""
    buttons = [
        [KeyboardButton(text=get_text("btn_services", lang)), KeyboardButton(text=get_text("btn_my_orders", lang))],
        [KeyboardButton(text=get_text("btn_my_files", lang)), KeyboardButton(text=get_text("btn_balance", lang))],
        [KeyboardButton(text=get_text("btn_buy", lang)), KeyboardButton(text=get_text("btn_ai_helper", lang))],
        [KeyboardButton(text=get_text("btn_referral", lang)), KeyboardButton(text=get_text("btn_promotions", lang))],
        [KeyboardButton(text=get_text("btn_language", lang)), KeyboardButton(text=get_text("btn_about", lang))],
        [KeyboardButton(text=get_text("btn_donate", lang)), KeyboardButton(text=get_text("btn_profile", lang))],
        [KeyboardButton(text=get_text("btn_contact", lang))],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def get_back_kb(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Get keyboard with just back button."""
    buttons = [[KeyboardButton(text=get_text("btn_back", lang))]]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def get_cancel_kb(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Get keyboard with cancel button."""
    buttons = [[KeyboardButton(text=get_text("btn_cancel", lang))]]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def get_contact_kb(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Get contact menu keyboard."""
    buttons = [
        [KeyboardButton(text=get_text("btn_admin_contact", lang)), KeyboardButton(text=get_text("btn_suggestion", lang))],
        [KeyboardButton(text=get_text("btn_report", lang)), KeyboardButton(text=get_text("btn_channel", lang))],
        [KeyboardButton(text=get_text("btn_back", lang))],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
