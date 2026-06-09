from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
from config import BANK_CARD, ADMIN_IDS
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
    
    if method in ["payme", "click"]:
        # Automated payment (simplified - in production would redirect to payment gateway)
        payment_id = await db.create_payment(user_id, amount, method)
        # Auto-confirm for demo (in production, webhook would confirm)
        result = await db.confirm_payment(payment_id)
        
        await callback.message.edit_text(
            get_text("payment_confirmed", lang, amount=amount),
            parse_mode="HTML"
        )
        await state.clear()
    
    elif method == "card":
        # Bank card - manual confirmation
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
    """Handle receipt photo."""
    user_id = message.from_user.id
    lang = await db.get_user_language(user_id)
    data = await state.get_data()
    
    await message.answer(
        get_text("payment_pending", lang),
        reply_markup=get_main_menu_kb(lang),
        parse_mode="HTML"
    )
    
    # Notify admins
    for admin_id in ADMIN_IDS:
        try:
            await message.bot.send_photo(
                admin_id,
                message.photo[-1].file_id,
                caption=f"💳 <b>Yangi to'lov!</b>\n\n"
                        f"👤 @{message.from_user.username or user_id}\n"
                        f"💰 Summa: {data['amount']} so'm\n"
                        f"🆔 Payment ID: #{data['payment_id']}",
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
    await message.answer("📷 Iltimos, chek rasmini yuboring!", parse_mode="HTML")


@router.callback_query(F.data == "cancel_payment")
async def cancel_payment(callback: CallbackQuery, state: FSMContext):
    """Cancel payment."""
    lang = await db.get_user_language(callback.from_user.id)
    await state.clear()
    await callback.message.edit_text(get_text("cancelled", lang), parse_mode="HTML")
    await callback.answer()
