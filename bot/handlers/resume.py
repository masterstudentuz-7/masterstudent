"""
Balans to'ldirilgandan keyin buyurtmani DAVOM ETTIRISH.
Foydalanuvchi balansi yetmasa, buyurtma ma'lumotlari saqlanadi.
Balans to'ldirilgach, foydalanuvchi boshidan emas, o'sha joydan davom etadi.
"""
import json
import logging

from aiogram import Router, F
from aiogram.types import CallbackQuery, BufferedInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

import database as db
from locales import get_text
from keyboards.main_kb import get_main_menu_kb
from keyboards.inline_kb import get_rating_kb, get_buy_now_kb
from services.ai_service import create_document_file, create_ppt_file
from utils.progress import start_progress_task, stop_progress_task

router = Router()
logger = logging.getLogger(__name__)


async def save_pending(user_id: int, data: dict):
    """Kutilayotgan buyurtmani saqlash."""
    await db.set_pending_order(user_id, json.dumps(data))


async def notify_if_can_resume(bot, user_id: int):
    """Balans to'ldirilgach chaqiriladi — kutilayotgan buyurtma bo'lsa, davom ettirishni taklif qiladi."""
    pj = await db.get_pending_order(user_id)
    if not pj:
        return
    try:
        p = json.loads(pj)
    except Exception:
        await db.clear_pending_order(user_id)
        return

    user = await db.get_user(user_id)
    balance = (user["balance"] + user["bonus"]) if user else 0
    if balance < p.get("price", 0):
        return  # hali yetarli emas

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="♻️ Davom ettirish", callback_data="resume_order")],
        [InlineKeyboardButton(text="❌ Kerak emas", callback_data="resume_cancel")],
    ])
    title = p.get("topic", "")
    try:
        await bot.send_message(
            user_id,
            f"🎉 <b>Hisobingiz to'ldirildi!</b>\n\n"
            f"Siz boshlagan buyurtmangizni eslab qoldik:\n"
            f"📝 <b>{title}</b>\n\n"
            f"Endi uni boshidan emas, shu yerdan davom ettirishingiz mumkin 👇",
            reply_markup=kb, parse_mode="HTML"
        )
    except Exception:
        pass


@router.callback_query(F.data == "resume_cancel")
async def resume_cancel(callback: CallbackQuery):
    await db.clear_pending_order(callback.from_user.id)
    lang = await db.get_user_language(callback.from_user.id)
    await callback.message.edit_text("✅ Bekor qilindi. Asosiy menyudan istalgan xizmatni tanlashingiz mumkin.")
    await callback.answer()


@router.callback_query(F.data == "resume_order")
async def resume_order(callback: CallbackQuery, state: FSMContext):
    """Saqlangan buyurtmani davom ettiradi — qaytadan yaratadi."""
    user_id = callback.from_user.id
    lang = await db.get_user_language(user_id)

    pj = await db.get_pending_order(user_id)
    if not pj:
        await callback.answer("Buyurtma topilmadi")
        return
    try:
        p = json.loads(pj)
    except Exception:
        await db.clear_pending_order(user_id)
        await callback.answer("Xatolik")
        return

    price = p.get("price", 0)
    user = await db.get_user(user_id)
    balance = (user["balance"] + user["bonus"]) if user else 0
    if balance < price:
        await callback.message.edit_text(
            "😔 Hali mablag' yetarli emas. Iltimos, hisobingizni to'ldiring 👇",
            reply_markup=get_buy_now_kb(lang), parse_mode="HTML"
        )
        await callback.answer()
        return

    await callback.answer("⏳ Yaratilmoqda...")
    await db.deduct_balance(user_id, price)
    await db.clear_pending_order(user_id)

    is_ppt = p.get("kind") == "ppt"
    progress_msg = await callback.message.answer(get_text("ai_processing", lang), parse_mode="HTML")
    progress_task = await start_progress_task(progress_msg, lang, is_ppt=is_ppt)

    try:
        if p["kind"] == "document":
            doc_name = "Referat" if p["doc_type"] == "referat" else "Mustaqil ish"
            order_id = await db.create_order(
                user_id, p["doc_type"], doc_name, f"Topic: {p['topic']}", price, is_ai=1
            )
            f = await create_document_file(
                p["topic"], doc_name, p["pages"], p["doc_lang"], p.get("references", True)
            )
            stop_progress_task(progress_task)
            fn = f"{p['doc_type']}_{order_id}.docx"
            doc = BufferedInputFile(f.read(), filename=fn)
            sent = await callback.message.answer_document(doc, caption=get_text("ai_complete", lang))
            if sent.document:
                await db.save_file(user_id, order_id, fn, sent.document.file_id, "docx")
        else:  # ppt
            order_id = await db.create_order(
                user_id, "ppt", "Taqdimot", f"Topic: {p['topic']}", price, is_ai=1
            )
            f = await create_ppt_file(
                p["topic"], p["slides"], p["design"], p.get("purpose", "educational"),
                p["ppt_lang"], p.get("extra", ""), is_pro=p.get("is_pro", False)
            )
            stop_progress_task(progress_task)
            fn = f"presentation_{order_id}.pptx"
            doc = BufferedInputFile(f.read(), filename=fn)
            sent = await callback.message.answer_document(doc, caption=get_text("ai_complete", lang))
            if sent.document:
                await db.save_file(user_id, order_id, fn, sent.document.file_id, "pptx")

        await db.update_order_status(order_id, "completed")
        await callback.message.answer(get_text("rate_order", lang), reply_markup=get_rating_kb())
    except Exception as e:
        stop_progress_task(progress_task)
        logger.error(f"Resume error: {type(e).__name__}: {e}")
        await callback.message.answer(get_text("error_generic", lang), reply_markup=get_main_menu_kb(lang))
        await db.add_balance(user_id, price)

    await state.clear()
