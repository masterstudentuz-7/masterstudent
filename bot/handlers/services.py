from aiogram import Router, F
from aiogram.types import CallbackQuery

import database as db
from locales import get_text
from keyboards.inline_kb import (
    get_services_kb, get_ai_services_kb, get_admin_services_kb,
    get_ppt_design_kb, get_buy_now_kb
)

router = Router()


@router.callback_query(F.data == "cat_ai")
async def show_ai_services(callback: CallbackQuery):
    """Show AI services list."""
    lang = await db.get_user_language(callback.from_user.id)
    await callback.message.edit_text(
        get_text("ai_services_title", lang),
        reply_markup=get_ai_services_kb(lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "cat_admin")
async def show_admin_services(callback: CallbackQuery):
    """Show admin services list."""
    lang = await db.get_user_language(callback.from_user.id)
    await callback.message.edit_text(
        get_text("admin_services_title", lang),
        reply_markup=get_admin_services_kb(lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "back_services")
async def back_to_services(callback: CallbackQuery):
    """Go back to service categories."""
    lang = await db.get_user_language(callback.from_user.id)
    await callback.message.edit_text(
        get_text("services_title", lang),
        reply_markup=get_services_kb(lang),
        parse_mode="HTML"
    )
    await callback.answer()


# ===== ADMIN SERVICE ORDERS =====
# Services that require admin processing

ADMIN_SERVICE_MAP = {
    "adm_cv": ("cv", "CV tayyorlash"),
    "adm_resume": ("resume", "Resume tayyorlash"),
    "adm_internet": ("internet", "Internet xizmatlari"),
    "adm_mygov": ("mygov", "My.gov.uz"),
    "adm_hisobot": ("hisobot", "Hisobotlar"),
    "adm_diplom": ("diplom_design", "Diplom dizayni"),
    "adm_sertifikat": ("sertifikat", "Sertifikat dizayni"),
    "adm_vizitka": ("vizitka", "Vizitka dizayni"),
    "adm_tg_post": ("telegram_post", "Telegram post dizayni"),
    "adm_reklama": ("reklama_banner", "Reklama bannerlari"),
    "adm_menu_design": ("menu_design", "Menyu dizayni"),
    "adm_logo": ("logo", "Logo yaratish"),
}


@router.callback_query(F.data.startswith("adm_"))
async def admin_service_selected(callback: CallbackQuery, state=None):
    """Handle admin service selection."""
    from aiogram.fsm.context import FSMContext
    from handlers.documents import AdminOrderStates
    
    service_key = callback.data
    if service_key not in ADMIN_SERVICE_MAP:
        await callback.answer()
        return
    
    lang = await db.get_user_language(callback.from_user.id)
    price_key, service_name = ADMIN_SERVICE_MAP[service_key]
    
    from config import PRICES
    price = PRICES.get(price_key, 20000)
    
    # Check balance
    user = await db.get_user(callback.from_user.id)
    total_balance = user["balance"] + user["bonus"]
    
    if total_balance < price:
        await callback.message.edit_text(
            get_text("insufficient_balance", lang, price=price, balance=total_balance),
            reply_markup=get_buy_now_kb(lang),
            parse_mode="HTML"
        )
        await callback.answer()
        return
    
    # Ask for details using FSM
    if state:
        await state.update_data(
            service_key=price_key,
            service_name=service_name,
            price=price
        )
        await state.set_state(AdminOrderStates.waiting_details)
    
    await callback.message.edit_text(
        get_text("admin_service_details", lang),
        parse_mode="HTML"
    )
    await callback.answer()
