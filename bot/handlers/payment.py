from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
from config import BANK_CARD, ADMIN_IDS, PAYME_TOKEN, CLICK_TOKEN
from locales import get_text
from keyboards.inline_kb import get_payment_amounts_kb, get_payment_method_kb, get_admin_payment_kb
from keyboards.main_kb import get_main_menu_kb

router = Router()


class PaymentStates(StatesGroup):
    choosing_amount = State()
    choosing_method = State()
    waiting_receipt = State()


@router.message(F.text.in_(["🛍 Sotib olish", "🛍 Пополнить", "🛍 Top Up"]))
async def buy_start(message: Message, state: FSMContext):
    """Start payment flow."""
    await state.clear()  # Oldingi jarayonni bekor qilish
    lang = await db.get_user_language(message.from_user.id)
    await state.set_state(PaymentStates.choosing_amount)
    await message.answer(
        get_text("choose_amount", lang),
        reply_markup=get_payment_amounts_kb(lang),
        parse_mode="HTML"
    )


@router.callback_query(PaymentStates.choosing_amount, F.data.startswith("pay_amount_"))
async def payment_amount_selected(callback: CallbackQuery, state: FSMContext):
    """Handle amount selection."""
    amount = int(callback.data.replace("pay_amount_", ""))
    lang = await db.get_user_language(callback.from_user.id)
    
    await state.update_data(amount=amount)
    await state.set_state(PaymentStates.choosing_method)
    
    await callback.message.edit_text(
        get_text("choose_payment_method", lang),
        reply_markup=get_payment_method_kb(lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(PaymentStates.choosing_method, F.data.startswith("pay_method_"))
async def payment_method_selected(callback: CallbackQuery, state: FSMContext):
    """Handle payment method selection."""
    method = callback.data.replace("pay_method_", "")
    user_id = callback.from_user.id
    lang = await db.get_user_language(user_id)
    data = await state.get_data()
    amount = data["amount"]
    
    if method == "payme":
        # Payme — chek yuborilishi kerak, admin tasdiqlaydi
        payment_id = await db.create_payment(user_id, amount, "payme")
        await state.update_data(payment_id=payment_id)
        await state.set_state(PaymentStates.waiting_receipt)
        
        await callback.message.edit_text(
            get_text("payment_payme_info", lang, amount=amount),
            parse_mode="HTML"
        )
    
    elif method == "click":
        # Click — chek yuborilishi kerak, admin tasdiqlaydi
        payment_id = await db.create_payment(user_id, amount, "click")
        await state.update_data(payment_id=payment_id)
        await state.set_state(PaymentStates.waiting_receipt)
        
        await callback.message.edit_text(
            get_text("payment_click_info", lang, amount=amount),
            parse_mode="HTML"
        )
    
    elif method == "card":
        # Bank karta — chek yuborilishi kerak, admin tasdiqlaydi
        payment_id = await db.create_payment(user_id, amount, "card")
        await state.update_data(payment_id=payment_id)
        await state.set_state(PaymentStates.waiting_receipt)
        
        await callback.message.edit_text(
            get_text("payment_card_info", lang, card=BANK_CARD, amount=amount),
            parse_mode="HTML"
        )
    
    await callback.answer()


@router.message(PaymentStates.waiting_receipt, F.photo)
async def payment_receipt_received(message: Message, state: FSMContext):
    """Handle receipt photo — admin tasdiqlamaguncha balans to'ldirilMAYDI."""
    user_id = message.from_user.id
    lang = await db.get_user_language(user_id)
    data = await state.get_data()
    
    # Mijozga xabar
    await message.answer(
        get_text("payment_pending", lang),
        reply_markup=get_main_menu_kb(lang),
        parse_mode="HTML"
    )
    
    # Admin'larga chek yuborish — ular tasdiqlagunicha balans TO'LDIRILMAYDI
    for admin_id in ADMIN_IDS:
        try:
            await message.bot.send_photo(
                admin_id,
                message.photo[-1].file_id,
                caption=f"💳 <b>Yangi to'lov kutilmoqda!</b>\n\n"
                        f"👤 @{message.from_user.username or user_id}\n"
                        f"🆔 User ID: {user_id}\n"
                        f"💰 Summa: <b>{data['amount']} so'm</b>\n"
                        f"📋 Usul: {data.get('method', 'unknown')}\n"
                        f"🆔 Payment ID: #{data['payment_id']}\n\n"
                        f"⚠️ <b>Tasdiqlash uchun tugmani bosing!</b>",
                reply_markup=get_admin_payment_kb(data["payment_id"]),
                parse_mode="HTML"
            )
        except Exception:
            pass
    
    await state.clear()


@router.message(PaymentStates.waiting_receipt, F.document)
async def payment_receipt_document(message: Message, state: FSMContext):
    """Handle receipt as document."""
    user_id = message.from_user.id
    lang = await db.get_user_language(user_id)
    data = await state.get_data()
    
    await message.answer(
        get_text("payment_pending", lang),
        reply_markup=get_main_menu_kb(lang),
        parse_mode="HTML"
    )
    
    for admin_id in ADMIN_IDS:
        try:
            await message.bot.send_document(
                admin_id,
                message.document.file_id,
                caption=f"💳 <b>Yangi to'lov kutilmoqda!</b>\n\n"
                        f"👤 @{message.from_user.username or user_id}\n"
                        f"🆔 User ID: {user_id}\n"
                        f"💰 Summa: <b>{data['amount']} so'm</b>\n"
                        f"🆔 Payment ID: #{data['payment_id']}\n\n"
                        f"⚠️ <b>Tasdiqlash uchun tugmani bosing!</b>",
                reply_markup=get_admin_payment_kb(data["payment_id"]),
                parse_mode="HTML"
            )
        except Exception:
            pass
    
    await state.clear()


@router.message(PaymentStates.waiting_receipt)
async def payment_receipt_text(message: Message, state: FSMContext):
    """Handle non-photo message while waiting for receipt."""
    lang = await db.get_user_language(message.from_user.id)
    
    # Ortga tugmasi bosilganda — jarayonni bekor qilish
    if message.text and message.text in ["⬅️ Ortga", "⬅️ Назад", "⬅️ Back"]:
        await state.clear()
        await message.answer(
            get_text("cancelled", lang),
            reply_markup=get_main_menu_kb(lang),
            parse_mode="HTML"
        )
        return
    
    await message.answer(
        "📷 Iltimos, to'lov chekining rasmini yoki screenshotini yuboring!\n\n⬅️ Bekor qilish uchun \"Ortga\" tugmasini bosing",
        parse_mode="HTML"
    )


@router.callback_query(F.data == "cancel_payment")
async def cancel_payment(callback: CallbackQuery, state: FSMContext):
    """Cancel payment."""
    lang = await db.get_user_language(callback.from_user.id)
    await state.clear()
    await callback.message.edit_text(get_text("cancelled", lang), parse_mode="HTML")
    await callback.answer()
