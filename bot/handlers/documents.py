from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BufferedInputFile

import database as db
from config import PRICES, ADMIN_IDS
from locales import get_text
from keyboards.inline_kb import (
    get_ppt_lang_kb, get_yes_no_kb, get_confirm_kb,
    get_esse_type_kb, get_esse_words_kb, get_qr_design_kb,
    get_rating_kb, get_admin_order_kb
)
from keyboards.main_kb import get_cancel_kb, get_main_menu_kb
from services.ai_service import (
    create_document_file, create_essay_file, translate_text,
    create_qr_code, generate_ai_text, generate_speech
)

router = Router()


# ===== REFERAT / MUSTAQIL ISH STATES =====

class DocumentStates(StatesGroup):
    choosing_lang = State()
    entering_topic = State()
    entering_pages = State()
    choosing_references = State()
    confirming = State()


class EssayStates(StatesGroup):
    entering_topic = State()
    choosing_lang = State()
    choosing_words = State()
    choosing_type = State()
    confirming = State()


class TranslationStates(StatesGroup):
    entering_text = State()
    choosing_lang = State()


class QRStates(StatesGroup):
    entering_data = State()
    choosing_design = State()


class AITextStates(StatesGroup):
    entering_topic = State()
    choosing_lang = State()


class AdminOrderStates(StatesGroup):
    waiting_details = State()


# ===== REFERAT =====

@router.callback_query(F.data.in_(["svc_referat", "svc_mustaqil"]))
async def doc_start(callback: CallbackQuery, state: FSMContext):
    """Start document creation flow."""
    lang = await db.get_user_language(callback.from_user.id)
    doc_type = "referat" if callback.data == "svc_referat" else "mustaqil_ish"
    
    await state.update_data(doc_type=doc_type)
    await state.set_state(DocumentStates.entering_topic)
    
    await callback.message.edit_text(
        get_text("referat_enter_topic", lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(DocumentStates.entering_topic)
async def doc_topic_entered(message: Message, state: FSMContext):
    """Handle topic input for document."""
    lang = await db.get_user_language(message.from_user.id)
    
    if message.text in ["❌ Bekor qilish", "❌ Отмена", "❌ Cancel"]:
        await state.clear()
        await message.answer(get_text("cancelled", lang), reply_markup=get_main_menu_kb(lang))
        return
    
    await state.update_data(topic=message.text)
    await state.set_state(DocumentStates.choosing_lang)
    
    await message.answer(
        get_text("referat_choose_lang", lang),
        reply_markup=get_ppt_lang_kb(lang),
        parse_mode="HTML"
    )


@router.callback_query(DocumentStates.choosing_lang, F.data.startswith("ppt_lang_"))
async def doc_lang_selected(callback: CallbackQuery, state: FSMContext):
    """Handle document language selection."""
    doc_lang = callback.data.replace("ppt_lang_", "")
    lang = await db.get_user_language(callback.from_user.id)
    
    await state.update_data(doc_lang=doc_lang)
    await state.set_state(DocumentStates.entering_pages)
    
    await callback.message.edit_text(
        get_text("referat_pages", lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(DocumentStates.entering_pages)
async def doc_pages_entered(message: Message, state: FSMContext):
    """Handle pages count input."""
    lang = await db.get_user_language(message.from_user.id)
    
    try:
        pages = int(message.text)
        if pages < 5 or pages > 50:
            raise ValueError()
    except (ValueError, TypeError):
        await message.answer(get_text("referat_pages", lang), parse_mode="HTML")
        return
    
    await state.update_data(pages=pages)
    await state.set_state(DocumentStates.choosing_references)
    
    await message.answer(
        get_text("referat_references", lang),
        reply_markup=get_yes_no_kb(lang),
        parse_mode="HTML"
    )


@router.callback_query(DocumentStates.choosing_references, F.data.in_(["answer_yes", "answer_no"]))
async def doc_references_selected(callback: CallbackQuery, state: FSMContext):
    """Handle references selection."""
    references = callback.data == "answer_yes"
    lang = await db.get_user_language(callback.from_user.id)
    
    await state.update_data(references=references)
    
    data = await state.get_data()
    price = PRICES.get(data["doc_type"], 10000)
    await state.update_data(price=price)
    
    user = await db.get_user(callback.from_user.id)
    if not user:
        await callback.answer("❌ Xatolik")
        await state.clear()
        return
    balance = user["balance"] + user["bonus"]
    
    if balance < price:
        await callback.message.edit_text(
            get_text("insufficient_balance", lang, price=price, balance=balance),
            parse_mode="HTML"
        )
        await state.clear()
        await callback.answer()
        return
    
    await state.set_state(DocumentStates.confirming)
    await callback.message.edit_text(
        f"📋 <b>Tasdiqlang:</b>\n\n"
        f"📝 Mavzu: {data['topic']}\n"
        f"🌐 Til: {data['doc_lang']}\n"
        f"📄 Sahifalar: {data['pages']}\n"
        f"📚 Adabiyotlar: {'Ha' if references else 'Yoq'}\n"
        f"💰 Narx: {price} so'm\n"
        f"💳 Balans: {balance} so'm",
        reply_markup=get_confirm_kb(lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(DocumentStates.confirming, F.data == "confirm_order")
async def doc_confirmed(callback: CallbackQuery, state: FSMContext):
    """Process document order."""
    user_id = callback.from_user.id
    lang = await db.get_user_language(user_id)
    data = await state.get_data()
    price = data["price"]
    
    # DARHOL callback.answer() chaqiramiz — timeout bo'lmasligi uchun
    await callback.answer("⏳ Yaratilmoqda...")
    
    success = await db.deduct_balance(user_id, price)
    if not success:
        user = await db.get_user(user_id)
        balance = user["balance"] + user["bonus"]
        await callback.message.edit_text(
            get_text("insufficient_balance", lang, price=price, balance=balance),
            parse_mode="HTML"
        )
        await state.clear()
        return
    
    doc_type_name = "Referat" if data["doc_type"] == "referat" else "Mustaqil ish"
    order_id = await db.create_order(
        user_id=user_id,
        service_type=data["doc_type"],
        service_name=doc_type_name,
        details=f"Topic: {data['topic']}, Lang: {data['doc_lang']}, Pages: {data['pages']}, References: {data['references']}",
        price=price,
        is_ai=1
    )
    
    await db.update_order_status(order_id, "creating")
    await callback.message.edit_text(get_text("ai_processing", lang), parse_mode="HTML")
    
    try:
        doc_file = await create_document_file(
            topic=data["topic"],
            doc_type=doc_type_name,
            pages=data["pages"],
            lang=data["doc_lang"],
            references=data["references"]
        )
        
        filename = f"{data['doc_type']}_{order_id}.docx"
        doc = BufferedInputFile(doc_file.read(), filename=filename)
        
        sent_msg = await callback.message.answer_document(doc, caption=get_text("ai_complete", lang))
        
        if sent_msg.document:
            await db.save_file(user_id, order_id, filename, sent_msg.document.file_id, "docx")
        
        await db.update_order_status(order_id, "completed")
        await callback.message.answer(get_text("rate_order", lang), reply_markup=get_rating_kb())
        
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Document creation error: {type(e).__name__}: {e}")
        await callback.message.answer(
            f"❌ Xatolik: {type(e).__name__}\n\n💬 Iltimos qayta urinib ko'ring.",
            reply_markup=get_main_menu_kb(lang),
            parse_mode="HTML"
        )
        await db.update_order_status(order_id, "cancelled")
        await db.add_balance(user_id, price)
    
    await state.clear()


# ===== ESSAY =====

@router.callback_query(F.data == "svc_esse")
async def esse_start(callback: CallbackQuery, state: FSMContext):
    """Start essay flow."""
    lang = await db.get_user_language(callback.from_user.id)
    await state.set_state(EssayStates.entering_topic)
    await callback.message.edit_text(get_text("esse_enter_topic", lang), parse_mode="HTML")
    await callback.answer()


@router.message(EssayStates.entering_topic)
async def esse_topic_entered(message: Message, state: FSMContext):
    """Handle essay topic."""
    lang = await db.get_user_language(message.from_user.id)
    await state.update_data(topic=message.text)
    await state.set_state(EssayStates.choosing_lang)
    await message.answer(get_text("referat_choose_lang", lang), reply_markup=get_ppt_lang_kb(lang), parse_mode="HTML")


@router.callback_query(EssayStates.choosing_lang, F.data.startswith("ppt_lang_"))
async def esse_lang_selected(callback: CallbackQuery, state: FSMContext):
    """Handle essay language."""
    essay_lang = callback.data.replace("ppt_lang_", "")
    lang = await db.get_user_language(callback.from_user.id)
    await state.update_data(essay_lang=essay_lang)
    await state.set_state(EssayStates.choosing_words)
    await callback.message.edit_text(get_text("esse_word_count", lang), reply_markup=get_esse_words_kb(lang), parse_mode="HTML")
    await callback.answer()


@router.callback_query(EssayStates.choosing_words, F.data.startswith("esse_words_"))
async def esse_words_selected(callback: CallbackQuery, state: FSMContext):
    """Handle word count selection."""
    words = int(callback.data.replace("esse_words_", ""))
    lang = await db.get_user_language(callback.from_user.id)
    await state.update_data(word_count=words)
    await state.set_state(EssayStates.choosing_type)
    await callback.message.edit_text(get_text("esse_type", lang), reply_markup=get_esse_type_kb(lang), parse_mode="HTML")
    await callback.answer()


@router.callback_query(EssayStates.choosing_type, F.data.startswith("esse_"))
async def esse_type_selected(callback: CallbackQuery, state: FSMContext):
    """Handle essay type and process."""
    essay_type = callback.data.replace("esse_", "")
    user_id = callback.from_user.id
    lang = await db.get_user_language(user_id)
    
    # DARHOL callback.answer() — timeout bo'lmasligi uchun
    await callback.answer("⏳ Yaratilmoqda...")
    
    await state.update_data(essay_type=essay_type)
    data = await state.get_data()
    price = PRICES["esse"]
    
    user = await db.get_user(user_id)
    balance = user["balance"] + user["bonus"]
    
    if balance < price:
        await callback.message.edit_text(
            get_text("insufficient_balance", lang, price=price, balance=balance),
            parse_mode="HTML"
        )
        await state.clear()
        return
    
    success = await db.deduct_balance(user_id, price)
    if not success:
        await state.clear()
        return
    
    order_id = await db.create_order(user_id, "esse", "Esse", 
        f"Topic: {data['topic']}, Lang: {data['essay_lang']}, Words: {data['word_count']}, Type: {essay_type}",
        price, is_ai=1)
    
    await db.update_order_status(order_id, "creating")
    await callback.message.edit_text(get_text("ai_processing", lang), parse_mode="HTML")
    
    try:
        file = await create_essay_file(data["topic"], data["essay_lang"], data["word_count"], essay_type)
        filename = f"essay_{order_id}.docx"
        doc = BufferedInputFile(file.read(), filename=filename)
        sent_msg = await callback.message.answer_document(doc, caption=get_text("ai_complete", lang))
        
        if sent_msg.document:
            await db.save_file(user_id, order_id, filename, sent_msg.document.file_id, "docx")
        await db.update_order_status(order_id, "completed")
        await callback.message.answer(get_text("rate_order", lang), reply_markup=get_rating_kb())
    except Exception:
        await callback.message.answer(get_text("error_generic", lang), reply_markup=get_main_menu_kb(lang))
        await db.update_order_status(order_id, "cancelled")
        await db.add_balance(user_id, price)
    
    await state.clear()


# ===== TRANSLATION =====

@router.callback_query(F.data == "svc_tarjima")
async def tarjima_start(callback: CallbackQuery, state: FSMContext):
    """Start translation flow."""
    lang = await db.get_user_language(callback.from_user.id)
    await state.set_state(TranslationStates.entering_text)
    await callback.message.edit_text(get_text("tarjima_send_text", lang), parse_mode="HTML")
    await callback.answer()


@router.message(TranslationStates.entering_text)
async def tarjima_text_entered(message: Message, state: FSMContext):
    """Handle translation text."""
    lang = await db.get_user_language(message.from_user.id)
    await state.update_data(text=message.text)
    await state.set_state(TranslationStates.choosing_lang)
    await message.answer(get_text("tarjima_choose_lang", lang), reply_markup=get_ppt_lang_kb(lang), parse_mode="HTML")


@router.callback_query(TranslationStates.choosing_lang, F.data.startswith("ppt_lang_"))
async def tarjima_lang_selected(callback: CallbackQuery, state: FSMContext):
    """Process translation."""
    target_lang = callback.data.replace("ppt_lang_", "")
    user_id = callback.from_user.id
    lang = await db.get_user_language(user_id)
    data = await state.get_data()
    
    # DARHOL callback.answer() — timeout bo'lmasligi uchun
    await callback.answer("⏳ Tarjima qilinmoqda...")
    
    price = PRICES["tarjima_page"]
    user = await db.get_user(user_id)
    balance = user["balance"] + user["bonus"]
    
    if balance < price:
        await callback.message.edit_text(
            get_text("insufficient_balance", lang, price=price, balance=balance), parse_mode="HTML")
        await state.clear()
        return
    
    await db.deduct_balance(user_id, price)
    order_id = await db.create_order(user_id, "tarjima", "Tarjima", 
        f"Target: {target_lang}, Text: {data['text'][:100]}...", price, is_ai=1)
    
    await callback.message.edit_text(get_text("ai_processing", lang), parse_mode="HTML")
    
    try:
        result = await translate_text(data["text"], target_lang)
        await callback.message.answer(f"🌐 <b>Tarjima natijasi:</b>\n\n{result}", parse_mode="HTML")
        await db.update_order_status(order_id, "completed")
    except Exception:
        await callback.message.answer(get_text("error_generic", lang), reply_markup=get_main_menu_kb(lang))
        await db.update_order_status(order_id, "cancelled")
        await db.add_balance(user_id, price)
    
    await state.clear()


# ===== QR CODE =====

@router.callback_query(F.data == "svc_qr")
async def qr_start(callback: CallbackQuery, state: FSMContext):
    """Start QR code flow."""
    lang = await db.get_user_language(callback.from_user.id)
    await state.set_state(QRStates.entering_data)
    await callback.message.edit_text(get_text("qr_enter_data", lang), parse_mode="HTML")
    await callback.answer()


@router.message(QRStates.entering_data)
async def qr_data_entered(message: Message, state: FSMContext):
    """Handle QR data input."""
    lang = await db.get_user_language(message.from_user.id)
    await state.update_data(qr_data=message.text)
    await state.set_state(QRStates.choosing_design)
    await message.answer(get_text("qr_choose_design", lang), reply_markup=get_qr_design_kb(lang), parse_mode="HTML")


@router.callback_query(QRStates.choosing_design, F.data.startswith("qr_design_"))
async def qr_design_selected(callback: CallbackQuery, state: FSMContext):
    """Process QR code generation."""
    design = callback.data.replace("qr_design_", "")
    user_id = callback.from_user.id
    lang = await db.get_user_language(user_id)
    data = await state.get_data()
    
    # DARHOL callback.answer()
    await callback.answer()
    
    price = PRICES["qr_code"]
    user = await db.get_user(user_id)
    balance = user["balance"] + user["bonus"]
    
    if balance < price:
        await callback.message.edit_text(
            get_text("insufficient_balance", lang, price=price, balance=balance), parse_mode="HTML")
        await state.clear()
        return
    
    await db.deduct_balance(user_id, price)
    order_id = await db.create_order(user_id, "qr_code", "QR Code", 
        f"Data: {data['qr_data']}, Design: {design}", price, is_ai=1)
    
    try:
        qr_img = create_qr_code(data["qr_data"], design)
        filename = f"qrcode_{order_id}.png"
        photo = BufferedInputFile(qr_img.read(), filename=filename)
        
        sent_msg = await callback.message.answer_photo(photo, caption=get_text("ai_complete", lang))
        
        if sent_msg.photo:
            await db.save_file(user_id, order_id, filename, sent_msg.photo[-1].file_id, "png")
        await db.update_order_status(order_id, "completed")
    except Exception:
        await callback.message.answer(get_text("error_generic", lang), reply_markup=get_main_menu_kb(lang))
        await db.update_order_status(order_id, "cancelled")
        await db.add_balance(user_id, price)
    
    await state.clear()


# ===== AI TEXT / CONTENT / SPEECH / BANNER =====

@router.callback_query(F.data.in_(["svc_ai_text", "svc_ai_content", "svc_speech", "svc_banner", "svc_word", "svc_excel", "svc_pdf", "svc_pdf_word"]))
async def ai_text_start(callback: CallbackQuery, state: FSMContext):
    """Start AI text service."""
    lang = await db.get_user_language(callback.from_user.id)
    service_map = {
        "svc_ai_text": ("ai_text", "AI matn yozish"),
        "svc_ai_content": ("ai_content", "AI kontent yaratish"),
        "svc_speech": ("speech", "Nutq tayyorlash"),
        "svc_banner": ("banner_post", "Banner va postlar"),
        "svc_word": ("word_service", "Word xizmatlari"),
        "svc_excel": ("excel_service", "Excel xizmatlari"),
        "svc_pdf": ("pdf_service", "PDF xizmatlari"),
        "svc_pdf_word": ("pdf_word", "PDF ↔ Word"),
    }
    service_key, service_name = service_map.get(callback.data, ("ai_text", "AI Text"))
    
    await state.update_data(service_key=service_key, service_name=service_name)
    await state.set_state(AITextStates.entering_topic)
    await callback.message.edit_text(
        f"📝 <b>{service_name}</b>\n\nNima haqida yozish kerak? Mavzu yoki talab kiriting:",
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(AITextStates.entering_topic)
async def ai_text_topic(message: Message, state: FSMContext):
    """Handle AI text topic and generate."""
    user_id = message.from_user.id
    lang = await db.get_user_language(user_id)
    data = await state.get_data()
    
    price = PRICES.get(data["service_key"], 5000)
    user = await db.get_user(user_id)
    balance = user["balance"] + user["bonus"]
    
    if balance < price:
        await message.answer(get_text("insufficient_balance", lang, price=price, balance=balance), parse_mode="HTML")
        await state.clear()
        return
    
    await db.deduct_balance(user_id, price)
    order_id = await db.create_order(user_id, data["service_key"], data["service_name"],
        f"Topic: {message.text}", price, is_ai=1)
    
    await message.answer(get_text("ai_processing", lang), parse_mode="HTML")
    
    try:
        if data["service_key"] == "speech":
            file = await generate_speech(message.text, lang)
            filename = f"speech_{order_id}.docx"
            doc = BufferedInputFile(file.read(), filename=filename)
            sent_msg = await message.answer_document(doc, caption=get_text("ai_complete", lang))
            if sent_msg.document:
                await db.save_file(user_id, order_id, filename, sent_msg.document.file_id, "docx")
        else:
            result = await generate_ai_text(message.text, lang)
            await message.answer(f"✅ <b>Natija:</b>\n\n{result}", parse_mode="HTML")
        
        await db.update_order_status(order_id, "completed")
    except Exception:
        await message.answer(get_text("error_generic", lang), reply_markup=get_main_menu_kb(lang))
        await db.update_order_status(order_id, "cancelled")
        await db.add_balance(user_id, price)
    
    await state.clear()


# ===== ADMIN SERVICE ORDER =====

@router.message(AdminOrderStates.waiting_details)
async def admin_order_details(message: Message, state: FSMContext):
    """Handle admin service order details."""
    user_id = message.from_user.id
    lang = await db.get_user_language(user_id)
    data = await state.get_data()
    
    price = data["price"]
    
    success = await db.deduct_balance(user_id, price)
    if not success:
        user = await db.get_user(user_id)
        balance = user["balance"] + user["bonus"]
        await message.answer(get_text("insufficient_balance", lang, price=price, balance=balance), parse_mode="HTML")
        await state.clear()
        return
    
    order_id = await db.create_order(
        user_id=user_id,
        service_type=data["service_key"],
        service_name=data["service_name"],
        details=message.text,
        price=price,
        is_ai=0
    )
    
    await message.answer(
        get_text("admin_order_submitted", lang, order_id=order_id),
        reply_markup=get_main_menu_kb(lang),
        parse_mode="HTML"
    )
    
    # Notify admins
    for admin_id in ADMIN_IDS:
        try:
            await message.bot.send_message(
                admin_id,
                get_text("admin_new_order", "uz",
                         order_id=order_id,
                         user=f"@{message.from_user.username or message.from_user.id}",
                         service=data["service_name"],
                         price=price,
                         details=message.text[:200]),
                reply_markup=get_admin_order_kb(order_id),
                parse_mode="HTML"
            )
        except Exception:
            pass
    
    await state.clear()


# ===== RATING =====

@router.callback_query(F.data.startswith("rate_"))
async def handle_rating(callback: CallbackQuery, state: FSMContext):
    """Handle order rating."""
    rating = int(callback.data.split("_")[1])
    lang = await db.get_user_language(callback.from_user.id)
    
    # Get latest order
    orders = await db.get_user_orders(callback.from_user.id, limit=1)
    if orders:
        await db.add_review(callback.from_user.id, orders[0]["order_id"], rating)
    
    await callback.message.edit_text(get_text("rate_thanks", lang), parse_mode="HTML")
    await callback.answer()
