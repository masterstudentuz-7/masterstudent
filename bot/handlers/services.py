from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

import database as db
from locales import get_text
from keyboards.inline_kb import (
    get_services_kb, get_ai_services_kb, get_admin_services_kb,
    get_ppt_design_kb, get_buy_now_kb, get_back_inline_kb
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
async def admin_service_selected(callback: CallbackQuery, state: FSMContext):
    """Admin xizmati tanlandi — TO'LOVSIZ, faqat buyurtma olinadi.
    Narx mijoz va admin o'rtasida kelishiladi."""
    from handlers.documents import AdminOrderStates

    service_key = callback.data
    if service_key not in ADMIN_SERVICE_MAP:
        await callback.answer()
        return

    lang = await db.get_user_language(callback.from_user.id)
    price_key, service_name = ADMIN_SERVICE_MAP[service_key]

    # Admin xizmatlari uchun to'lov SHART EMAS — narx admin bilan kelishiladi
    await state.update_data(service_key=price_key, service_name=service_name)
    await state.set_state(AdminOrderStates.waiting_details)

    await callback.message.edit_text(
        f"✨ <b>{service_name}</b>\n\n"
        f"Ajoyib tanlov! 😊\n\n"
        f"Bu xizmat <b>mutaxassisimiz</b> tomonidan qo'lda, sifatli tarzda bajariladi.\n"
        f"💰 Narx siz bilan kelishilgan holda belgilanadi — hech qanday oldindan to'lov shart emas!\n\n"
        f"📝 Iltimos, nima kerakligini batafsil yozib yuboring.\n"
        f"💡 <i>Masalan: mavzu, talablar, muddat, qo'shimcha istaklaringiz...</i>",
        reply_markup=get_back_inline_kb(lang),
        parse_mode="HTML"
    )
    await callback.answer()
