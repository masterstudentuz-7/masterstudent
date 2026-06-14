from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, BufferedInputFile
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
from config import PRICES, WEBAPP_URL
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


_designs_preview_cache = None


def _get_designs_preview_bytes():
    """Dizayn preview rasmini bir marta yaratib, keshda saqlaydi."""
    global _designs_preview_cache
    if _designs_preview_cache is None:
        try:
            from services.ai_service import generate_designs_preview
            _designs_preview_cache = generate_designs_preview().read()
        except Exception:
            _designs_preview_cache = b""
    return _designs_preview_cache


@router.callback_query(F.data == "svc_ppt")
async def ppt_start(callback: CallbackQuery, state: FSMContext):
    """Start PPT creation flow (oddiy) — dizayn preview rasmi bilan."""
    lang = await db.get_user_language(callback.from_user.id)
    await state.update_data(is_pro=False)
    await state.set_state(PPTStates.choosing_design)
    await _send_design_picker(callback, lang)
    await callback.answer()


async def _send_design_picker(callback: CallbackQuery, lang: str):
    """15 ta dizayn preview rasmini va tanlash tugmalarini yuboradi.
    Pastda (reply klaviatura) doimo 'Ortga' tugmasi turadi."""
    from keyboards.main_kb import get_back_kb
    photo_bytes = _get_designs_preview_bytes()

    # Pastki 'Ortga' tugmasi bilan header (rasm yoki matn)
    sent = False
    if photo_bytes:
        try:
            await callback.message.answer_photo(
                BufferedInputFile(photo_bytes, filename="designs.png"),
                caption="🎨 <b>15 ta tayyor dizayn</b> — quyida ko'rinishini ko'ring 👇",
                reply_markup=get_back_kb(lang),
                parse_mode="HTML"
            )
            sent = True
        except Exception:
            sent = False
    if not sent:
        # Rasm chiqmasa ham — pastda Ortga tugmasi bilan matn yuboramiz
        await callback.message.answer(
            "🎨 <b>15 ta tayyor dizayn</b>\n\nQuyidagi ro'yxatdan tanlang 👇",
            reply_markup=get_back_kb(lang),
            parse_mode="HTML"
        )

    # Dizayn tanlash (inline) — har dizayn alohida
    await callback.message.answer(
        get_text("ppt_choose_design", lang),
        reply_markup=get_ppt_design_kb(lang),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "svc_ppt_pro")
async def ppt_pro_start(callback: CallbackQuery, state: FSMContext):
    """Taqdimot PRO — Web App (Mini App) ni Telegram ICHIDA ochadi."""
    lang = await db.get_user_language(callback.from_user.id)

    if WEBAPP_URL:
        kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🌟 Taqdimot PRO — ochish", web_app=WebAppInfo(url=WEBAPP_URL))],
                [KeyboardButton(text=get_text("btn_back", lang))],
            ],
            resize_keyboard=True
        )
        await callback.message.answer(
            "🌟 <b>Taqdimot PRO</b>\n\n"
            "Premium taqdimot — rasmlar va boy ma'lumot bilan! 💎\n\n"
            "Web ilovada:\n"
            "• 🎨 15 ta tayyor dizayn (rasmli ko'rinish)\n"
            "• 🖼 Avtomatik rasmlar\n"
            "• ⭐ 3 xil sifat tarifi\n"
            "• 📄 PPTX yoki PDF format\n\n"
            "Quyidagi tugmani bosing 👇\n"
            "⬅️ Chiqish uchun «Ortga» tugmasini bosing",
            reply_markup=kb,
            parse_mode="HTML"
        )
        await callback.answer()
        return

    # WEBAPP_URL sozlanmagan bo'lsa — ichki oqim (dizayn preview bilan)
    await state.update_data(is_pro=True)
    await state.set_state(PPTStates.choosing_design)
    await callback.message.answer(
        "🌟 <b>Taqdimot PRO</b>\n\n"
        "Premium taqdimot — rasmlar va 2 baravar boy ma'lumot bilan! 💎",
        parse_mode="HTML"
    )
    await _send_design_picker(callback, lang)
    await callback.answer()


@router.callback_query(PPTStates.choosing_design, F.data.startswith("ppt_design_"))
async def ppt_design_selected(callback: CallbackQuery, state: FSMContext):
    """Handle design selection."""
    design = callback.data.replace("ppt_design_", "")
    lang = await db.get_user_language(callback.from_user.id)
    
    await state.update_data(design=design)
    await state.set_state(PPTStates.choosing_purpose)

    # Xabar rasm bo'lishi mumkin — edit_text ishlamasligi mumkin, shuning uchun yangi xabar
    try:
        await callback.message.edit_text(
            get_text("ppt_choose_purpose", lang),
            reply_markup=get_ppt_purpose_kb(lang),
            parse_mode="HTML"
        )
    except Exception:
        await callback.message.answer(
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
    
    from keyboards.inline_kb import get_back_inline_kb
    await callback.message.edit_text(
        get_text("ppt_enter_topic", lang),
        reply_markup=get_back_inline_kb(lang),
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
    
    lang_names = {"uz": "O'zbek tili", "ru": "Rus tili", "en": "Ingliz tili"}
    
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
        # Kutilayotgan buyurtmani saqlash
        import json as _json
        pending = {
            "kind": "ppt", "design": data["design"], "purpose": data.get("purpose", "educational"),
            "ppt_lang": data["ppt_lang"], "topic": data["topic"], "slides": data["slides"],
            "is_pro": data.get("is_pro", False), "extra": data.get("extra", ""), "price": price
        }
        await db.set_pending_order(user_id, _json.dumps(pending))
        bal_str = f"{balance:,}".replace(",", " ")
        price_str = f"{price:,}".replace(",", " ")
        await callback.message.edit_text(
            f"😔 <b>Afsuski, hisobingizda mablag' yetarli emas</b>\n\n"
            f"💰 Xizmat narxi: <b>{price_str} so'm</b>\n"
            f"💳 Sizning hisobingiz: <b>{bal_str} so'm</b>\n\n"
            f"✅ Buyurtmangiz eslab qolindi!\n"
            f"Hisobni to'ldirgach, boshidan emas — shu yerdan davom ettirasiz 👇",
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



# ============================================================
# WEB APP (Mini App) — taqdimot sozlamalari web oynadan keladi
# ============================================================

@router.message(F.web_app_data)
async def handle_webapp_data(message: Message, state: FSMContext):
    """Web App formasidan kelgan ma'lumotni qabul qiladi va taqdimot yaratadi."""
    import json
    import logging
    from utils.progress import start_progress_task, stop_progress_task

    user_id = message.from_user.id
    lang = await db.get_user_language(user_id)

    try:
        data = json.loads(message.web_app_data.data)
    except Exception:
        await message.answer(get_text("error_generic", lang), reply_markup=get_main_menu_kb(lang))
        return

    if data.get("type") != "ppt_webapp":
        return

    topic = (data.get("topic") or "").strip()
    if len(topic) < 3:
        await message.answer("❗ Mavzu juda qisqa. Iltimos qaytadan urinib ko'ring.", reply_markup=get_main_menu_kb(lang))
        return

    ppt_lang = data.get("lang", "uz")
    slides = int(data.get("slides", 10))
    design = data.get("design", "business")
    image_mode = data.get("image_mode", "auto")
    tariff = data.get("tariff", "standart")
    author = (data.get("author") or "").strip()

    # Narx hisoblash: rasm bo'lsa PRO narx, tarif bo'yicha qo'shimcha
    is_pro = (image_mode == "auto")
    base_key = f"ppt_pro_{slides}" if is_pro else f"ppt_{slides}"
    price = PRICES.get(base_key, PRICES.get("ppt_10", 8000))
    # Tarif qo'shimchasi
    if tariff == "premium":
        price += 3000
    elif tariff == "ilmiy":
        price += 5000

    # Balans tekshirish
    user = await db.get_user(user_id)
    balance = (user["balance"] + user["bonus"]) if user else 0
    if balance < price:
        import json as _json
        pending = {
            "kind": "ppt", "design": design, "purpose": "educational",
            "ppt_lang": ppt_lang, "topic": topic, "slides": slides,
            "is_pro": is_pro, "extra": (f"Muallif: {author}." if author else ""), "price": price
        }
        await db.set_pending_order(user_id, _json.dumps(pending))
        bal_str = f"{balance:,}".replace(",", " ")
        price_str = f"{price:,}".replace(",", " ")
        await message.answer(
            f"😔 <b>Afsuski, hisobingizda mablag' yetarli emas</b>\n\n"
            f"💰 Xizmat narxi: <b>{price_str} so'm</b>\n"
            f"💳 Sizning hisobingiz: <b>{bal_str} so'm</b>\n\n"
            f"✅ Buyurtmangiz eslab qolindi! To'lovdan keyin shu yerdan davom etasiz 👇",
            reply_markup=get_buy_now_kb(lang),
            parse_mode="HTML"
        )
        return

    # To'lovni yechish
    success = await db.deduct_balance(user_id, price)
    if not success:
        await message.answer(get_text("error_generic", lang), reply_markup=get_main_menu_kb(lang))
        return

    tariff_names = {"standart": "Standart", "premium": "Premium", "ilmiy": "Yuqori Sifatli Premium"}
    order_id = await db.create_order(
        user_id=user_id, service_type="ppt_webapp", service_name="Taqdimot (Web App)",
        details=f"Topic: {topic}, Design: {design}, Slides: {slides}, Tarif: {tariff}, Rasm: {image_mode}",
        price=price, is_ai=1
    )
    await db.update_order_status(order_id, "creating")

    progress_msg = await message.answer(get_text("ai_processing", lang), parse_mode="HTML")
    progress_task = await start_progress_task(progress_msg, lang, is_ppt=True)

    try:
        # Mavzuga muallif ismini qo'shamiz (titul uchun)
        extra = f"Muallif: {author}. Tarif: {tariff_names.get(tariff, tariff)}." if author else f"Tarif: {tariff_names.get(tariff, tariff)}."
        ppt_file = await create_ppt_file(
            topic=topic, slides_count=slides, design=design,
            purpose="educational", lang=ppt_lang, extra=extra, is_pro=is_pro
        )
        stop_progress_task(progress_task)

        filename = f"presentation_{order_id}.pptx"
        doc = BufferedInputFile(ppt_file.read(), filename=filename)
        sent_msg = await message.answer_document(doc, caption=get_text("ai_complete", lang))
        if sent_msg.document:
            await db.save_file(user_id, order_id, filename, sent_msg.document.file_id, "pptx")
        await db.update_order_status(order_id, "completed")

        from keyboards.inline_kb import get_rating_kb
        await message.answer(get_text("rate_order", lang), reply_markup=get_rating_kb())
    except Exception as e:
        stop_progress_task(progress_task)
        logging.getLogger(__name__).error(f"WebApp PPT error: {type(e).__name__}: {e}")
        await message.answer(
            f"❌ Xatolik: {type(e).__name__}\n\nUzr, qaytadan urinib ko'ring.",
            reply_markup=get_main_menu_kb(lang)
        )
        await db.update_order_status(order_id, "cancelled")
        await db.add_balance(user_id, price)

    await state.clear()
