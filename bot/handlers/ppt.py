from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BufferedInputFile

import database as db
from config import PRICES
from locales import get_text
from keyboards.inline_kb import (
    get_ppt_design_kb, get_ppt_purpose_kb, get_ppt_lang_kb,
    get_ppt_slides_kb, get_confirm_kb, get_buy_now_kb
)
from keyboards.main_kb import get_cancel_kb, get_main_menu_kb
from services.ai_service import create_ppt_file

router = Router()


class PPTStates(StatesGroup):
    choosing_design = State()
    choosing_purpose = State()
    choosing_lang = State()
    entering_topic = State()
    choosing_slides = State()
    entering_extra = State()
    confirming = State()


@router.callback_query(F.data == "svc_ppt")
async def ppt_start(callback: CallbackQuery, state: FSMContext):
    """Start PPT creation flow (oddiy)."""
    lang = await db.get_user_language(callback.from_user.id)
    await state.update_data(is_pro=False)
    await state.set_state(PPTStates.choosing_design)
    await callback.message.edit_text(
        get_text("ppt_choose_design", lang),
        reply_markup=get_ppt_design_kb(lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "svc_ppt_pro")
async def ppt_pro_start(callback: CallbackQuery, state: FSMContext):
    """Start Taqdimot PRO flow — rasmlar bilan, boy kontent."""
    lang = await db.get_user_language(callback.from_user.id)
    await state.update_data(is_pro=True)
    await state.set_state(PPTStates.choosing_design)
    await callback.message.edit_text(
        "🌟 <b>Taqdimot PRO</b>\n\n"
        "Bu — premium taqdimot:\n"
        "• 🖼 Mavzuga mos professional rasmlar\n"
        "• 📚 Oddiyga qaraganda 2 baravar ko'p ma'lumot\n"
        "• 🎨 Yuqori sifatli dizayn\n\n"
        "Keling, boshlaymiz! Avval dizaynni tanlang 👇",
        reply_markup=get_ppt_design_kb(lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(PPTStates.choosing_design, F.data.startswith("ppt_design_"))
async def ppt_design_selected(callback: CallbackQuery, state: FSMContext):
    """Handle design selection."""
    design = callback.data.replace("ppt_design_", "")
    lang = await db.get_user_language(callback.from_user.id)
    
    await state.update_data(design=design)
    await state.set_state(PPTStates.choosing_purpose)
    
    await callback.message.edit_text(
        get_text("ppt_choose_purpose", lang),
        reply_markup=get_ppt_purpose_kb(lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(PPTStates.choosing_purpose, F.data.startswith("ppt_purp_"))
async def ppt_purpose_selected(callback: CallbackQuery, state: FSMContext):
    """Handle purpose selection."""
    purpose = callback.data.replace("ppt_purp_", "")
    lang = await db.get_user_language(callback.from_user.id)
    
    await state.update_data(purpose=purpose)
    await state.set_state(PPTStates.choosing_lang)
    
    await callback.message.edit_text(
        get_text("ppt_choose_lang", lang),
        reply_markup=get_ppt_lang_kb(lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(PPTStates.choosing_lang, F.data.startswith("ppt_lang_"))
async def ppt_lang_selected(callback: CallbackQuery, state: FSMContext):
    """Handle PPT language selection."""
    ppt_lang = callback.data.replace("ppt_lang_", "")
    lang = await db.get_user_language(callback.from_user.id)
    
    await state.update_data(ppt_lang=ppt_lang)
    await state.set_state(PPTStates.entering_topic)
    
    await callback.message.edit_text(
        get_text("ppt_enter_topic", lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(PPTStates.entering_topic)
async def ppt_topic_entered(message: Message, state: FSMContext):
    """Handle topic input."""
    lang = await db.get_user_language(message.from_user.id)
    
    if message.text in ["❌ Bekor qilish", "❌ Отмена", "❌ Cancel"]:
        await state.clear()
        await message.answer(get_text("cancelled", lang), reply_markup=get_main_menu_kb(lang))
        return
    
    await state.update_data(topic=message.text)
    await state.set_state(PPTStates.choosing_slides)
    
    data = await state.get_data()
    is_pro = data.get("is_pro", False)
    await message.answer(
        get_text("ppt_choose_slides", lang),
        reply_markup=get_ppt_slides_kb(lang, is_pro=is_pro),
        parse_mode="HTML"
    )


@router.callback_query(PPTStates.choosing_slides, F.data.startswith("ppt_slides_"))
async def ppt_slides_selected(callback: CallbackQuery, state: FSMContext):
    """Handle slides count selection."""
    slides = int(callback.data.replace("ppt_slides_", ""))
    lang = await db.get_user_language(callback.from_user.id)
    
    await state.update_data(slides=slides)
    await state.set_state(PPTStates.entering_extra)
    
    await callback.message.edit_text(
        get_text("ppt_extra_requirements", lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(PPTStates.entering_extra)
async def ppt_extra_entered(message: Message, state: FSMContext):
    """Handle extra requirements input."""
    lang = await db.get_user_language(message.from_user.id)
    
    extra = message.text
    if extra.lower() in ["yo'q", "нет", "no", "-"]:
        extra = ""
    
    await state.update_data(extra=extra)
    await state.set_state(PPTStates.confirming)
    
    data = await state.get_data()
    slides = data["slides"]
    
    # Calculate price (PRO bo'lsa qimmatroq)
    data_now = await state.get_data()
    is_pro = data_now.get("is_pro", False)
    if is_pro:
        price_key = f"ppt_pro_{slides}"
        price = PRICES.get(price_key, PRICES["ppt_pro_10"])
    else:
        price_key = f"ppt_{slides}"
        price = PRICES.get(price_key, PRICES["ppt_10"])
    await state.update_data(price=price)
    
    # Get user balance
    user = await db.get_user(message.from_user.id)
    balance = user["balance"] + user["bonus"]
    
    purpose_names = {
        "university": "Universitet",
        "business": "Biznes",
        "report": "Hisobot",
        "startup": "Startup",
        "educational": "O'quv materiali",
    }
    
    lang_names = {"uz": "O'zbek", "ru": "Rus", "en": "Ingliz"}
    
    await message.answer(
        get_text("ppt_confirm", lang,
                 design=data["design"].title(),
                 purpose=purpose_names.get(data["purpose"], data["purpose"]),
                 ppt_lang=lang_names.get(data["ppt_lang"], data["ppt_lang"]),
                 topic=data["topic"],
                 slides=slides,
                 extra=extra or "-",
                 price=price,
                 balance=balance),
        reply_markup=get_confirm_kb(lang),
        parse_mode="HTML"
    )


@router.callback_query(PPTStates.confirming, F.data == "confirm_order")
async def ppt_confirmed(callback: CallbackQuery, state: FSMContext):
    """Process PPT order."""
    user_id = callback.from_user.id
    lang = await db.get_user_language(user_id)
    data = await state.get_data()
    price = data["price"]
    
    # DARHOL callback.answer() — Telegram 30s timeout bo'lmasligi uchun
    await callback.answer("⏳ PPT yaratilmoqda...")
    
    # Check and deduct balance
    success = await db.deduct_balance(user_id, price)
    if not success:
        user = await db.get_user(user_id)
        balance = user["balance"] + user["bonus"]
        await callback.message.edit_text(
            get_text("insufficient_balance", lang, price=price, balance=balance),
            reply_markup=get_buy_now_kb(lang),
            parse_mode="HTML"
        )
        await state.clear()
        return
    
    # Create order
    order_id = await db.create_order(
        user_id=user_id,
        service_type="ppt",
        service_name="Professional PPT",
        details=f"Design: {data['design']}, Purpose: {data['purpose']}, Lang: {data['ppt_lang']}, Topic: {data['topic']}, Slides: {data['slides']}, Extra: {data.get('extra', '')}",
        price=price,
        is_ai=1
    )
    
    await db.update_order_status(order_id, "creating")
    
    # Show processing message with progress bar
    progress_msg = await callback.message.edit_text(
        get_text("ai_processing", lang),
        parse_mode="HTML"
    )
    
    from utils.progress import start_progress_task, stop_progress_task
    progress_task = await start_progress_task(progress_msg, lang, is_ppt=True)
    
    try:
        # Generate PPT
        ppt_file = await create_ppt_file(
            topic=data["topic"],
            slides_count=data["slides"],
            design=data["design"],
            purpose=data["purpose"],
            lang=data["ppt_lang"],
            extra=data.get("extra", ""),
            is_pro=data.get("is_pro", False)
        )
        
        # Progress to'xtatish
        stop_progress_task(progress_task)
        
        # Send file
        filename = f"presentation_{order_id}.pptx"
        doc = BufferedInputFile(ppt_file.read(), filename=filename)
        
        sent_msg = await callback.message.answer_document(
            doc,
            caption=get_text("ai_complete", lang)
        )
        
        # Save file reference
        if sent_msg.document:
            await db.save_file(user_id, order_id, filename, sent_msg.document.file_id, "pptx")
        
        # Update order status
        await db.update_order_status(order_id, "completed")
        
        # Show rating
        from keyboards.inline_kb import get_rating_kb
        await callback.message.answer(
            get_text("rate_order", lang),
            reply_markup=get_rating_kb()
        )
        await state.update_data(rate_order_id=order_id)
        
    except Exception as e:
        stop_progress_task(progress_task)
        import logging
        logging.getLogger(__name__).error(f"PPT creation error: {type(e).__name__}: {e}")
        await callback.message.answer(
            f"❌ Xatolik: {type(e).__name__}\n\n💬 Iltimos qayta urinib ko'ring.",
            reply_markup=get_main_menu_kb(lang),
            parse_mode="HTML"
        )
        await db.update_order_status(order_id, "cancelled")
        # Refund
        await db.add_balance(user_id, price)
    
    await state.clear()


@router.callback_query(F.data == "cancel_order")
async def cancel_order(callback: CallbackQuery, state: FSMContext):
    """Cancel current order flow."""
    lang = await db.get_user_language(callback.from_user.id)
    await state.clear()
    await callback.message.edit_text(get_text("cancelled", lang), parse_mode="HTML")
    await callback.message.answer(
        get_text("main_menu", lang),
        reply_markup=get_main_menu_kb(lang),
        parse_mode="HTML"
    )
    await callback.answer()
