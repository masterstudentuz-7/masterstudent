from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
from config import ADMIN_IDS
from locales import get_text
from keyboards.inline_kb import get_admin_panel_kb, get_admin_order_kb

router = Router()


class AdminStates(StatesGroup):
    uploading_file = State()
    broadcasting = State()
    adding_promo = State()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Show admin panel."""
    if not is_admin(message.from_user.id):
        return
    
    await message.answer(
        get_text("admin_panel", "uz"),
        reply_markup=get_admin_panel_kb(),
        parse_mode="HTML"
    )


@router.message(Command("elon"))
async def cmd_elon(message: Message, state: FSMContext):
    """Tezkor e'lon — admin barcha foydalanuvchilarga xabar yuboradi.
    Foydalanish: /elon Bot yangilanmoqda, biroz kuting!
    yoki shunchaki /elon yozsa, keyingi xabarni so'raydi."""
    if not is_admin(message.from_user.id):
        return

    text = message.text.replace("/elon", "", 1).strip()
    if text:
        # Matn buyruq bilan birga yuborilgan — darhol yuboramiz
        await _do_broadcast(message, text)
    else:
        # Matn yo'q — keyingi xabarni so'raymiz
        await state.set_state(AdminStates.broadcasting)
        await message.answer(
            "📢 <b>E'lon yuborish</b>\n\n"
            "Barcha foydalanuvchilarga yubormoqchi bo'lgan xabaringizni yozing.\n\n"
            "💡 Masalan: <i>«Hurmatli mijozlar! Botda yangi bo'lim qo'shildi 🎉»</i>\n\n"
            "❌ Bekor qilish uchun: /bekor",
            parse_mode="HTML"
        )


@router.message(Command("bekor"))
async def cmd_bekor(message: Message, state: FSMContext):
    """Admin amalini bekor qilish."""
    if not is_admin(message.from_user.id):
        return
    await state.clear()
    await message.answer("✅ Bekor qilindi")


async def _do_broadcast(message: Message, text: str):
    """Barcha foydalanuvchilarga xabar yuboradi."""
    users = await db.get_all_users()
    sent = 0
    failed = 0
    for user in users:
        try:
            await message.bot.send_message(user["user_id"], text, parse_mode="HTML")
            sent += 1
        except Exception:
            failed += 1
    await message.answer(
        f"📢 <b>E'lon yuborildi!</b>\n\n✅ Yetkazildi: {sent} ta\n❌ Yuborilmadi: {failed} ta",
        parse_mode="HTML"
    )


@router.callback_query(F.data == "admin_dashboard")
async def admin_dashboard(callback: CallbackQuery):
    """Show dashboard."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔")
        return
    
    stats = await db.get_stats()
    await callback.message.edit_text(
        get_text("admin_dashboard", "uz",
                 users=stats["users"],
                 orders=stats["orders"],
                 revenue=stats["revenue"],
                 pending=stats["pending_orders"]),
        reply_markup=get_admin_panel_kb(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "admin_orders")
async def admin_orders(callback: CallbackQuery):
    """Show pending orders."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔")
        return
    
    orders = await db.get_pending_admin_orders()
    
    if not orders:
        await callback.answer("📦 Yangi buyurtmalar yo'q")
        return
    
    for order in orders[:10]:
        user = await db.get_user(order["user_id"])
        username = user["username"] if user else "Unknown"
        
        text = (
            f"📦 <b>Buyurtma #{order['order_id']}</b>\n\n"
            f"👤 @{username}\n"
            f"🛒 {order['service_name']}\n"
            f"💰 {order['price']} so'm\n"
            f"📋 {order['details'][:200]}\n"
            f"📊 Status: {order['status']}"
        )
        await callback.message.answer(
            text,
            reply_markup=get_admin_order_kb(order["order_id"]),
            parse_mode="HTML"
        )
    
    await callback.answer()


@router.callback_query(F.data == "admin_payments")
async def admin_payments(callback: CallbackQuery):
    """Show pending payments."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔")
        return
    
    payments = await db.get_pending_payments()
    
    if not payments:
        await callback.answer("💳 Kutilayotgan to'lovlar yo'q")
        return
    
    for payment in payments[:10]:
        user = await db.get_user(payment["user_id"])
        username = user["username"] if user else "Unknown"
        text = (
            f"💳 <b>To'lov #{payment['payment_id']}</b>\n\n"
            f"👤 @{username}\n"
            f"💰 {payment['amount']} so'm\n"
            f"📋 Usul: {payment['method']}"
        )
        from keyboards.inline_kb import get_admin_payment_kb
        await callback.message.answer(
            text,
            reply_markup=get_admin_payment_kb(payment["payment_id"]),
            parse_mode="HTML"
        )
    
    await callback.answer()


@router.callback_query(F.data == "admin_users")
async def admin_users(callback: CallbackQuery):
    """Show users stats."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔")
        return
    
    count = await db.get_users_count()
    await callback.message.answer(f"👥 Jami foydalanuvchilar: <b>{count}</b>", parse_mode="HTML")
    await callback.answer()


# ===== ADMIN ORDER ACTIONS =====

@router.callback_query(F.data.startswith("adm_accept_"))
async def admin_accept_order(callback: CallbackQuery):
    """Accept an order."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔")
        return
    
    order_id = int(callback.data.replace("adm_accept_", ""))
    await db.update_order_status(order_id, "accepted")
    
    order = await db.get_order(order_id)
    if order:
        try:
            lang = await db.get_user_language(order["user_id"])
            await callback.bot.send_message(
                order["user_id"],
                f"✅ Buyurtma #{order_id} qabul qilindi!\n⏳ Tez orada bajariladi.",
                parse_mode="HTML"
            )
        except Exception:
            pass
    
    await callback.message.edit_text(
        callback.message.text + "\n\n✅ <b>QABUL QILINDI</b>",
        reply_markup=get_admin_order_kb(order_id),
        parse_mode="HTML"
    )
    await callback.answer("✅ Qabul qilindi")


@router.callback_query(F.data.startswith("adm_progress_"))
async def admin_progress_order(callback: CallbackQuery):
    """Mark order as in progress."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔")
        return
    
    order_id = int(callback.data.replace("adm_progress_", ""))
    await db.update_order_status(order_id, "in_progress")
    
    order = await db.get_order(order_id)
    if order:
        try:
            await callback.bot.send_message(
                order["user_id"],
                f"🔵 Buyurtma #{order_id} bajarilmoqda...",
                parse_mode="HTML"
            )
        except Exception:
            pass
    
    await callback.answer("🔵 Jarayonda")


@router.callback_query(F.data.startswith("adm_upload_"))
async def admin_upload_file(callback: CallbackQuery, state: FSMContext):
    """Request file upload for order."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔")
        return
    
    order_id = int(callback.data.replace("adm_upload_", ""))
    await state.update_data(upload_order_id=order_id)
    await state.set_state(AdminStates.uploading_file)
    
    await callback.message.answer(
        f"📎 Buyurtma #{order_id} uchun tayyor faylni yuboring:",
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(AdminStates.uploading_file, F.document)
async def admin_file_received(message: Message, state: FSMContext):
    """Handle admin file upload."""
    if not is_admin(message.from_user.id):
        return
    
    data = await state.get_data()
    order_id = data.get("upload_order_id")
    
    if not order_id:
        await state.clear()
        return
    
    order = await db.get_order(order_id)
    if not order:
        await message.answer("❌ Buyurtma topilmadi")
        await state.clear()
        return
    
    # Save file
    file_id = message.document.file_id
    file_name = message.document.file_name or f"file_{order_id}"
    
    await db.save_file(order["user_id"], order_id, file_name, file_id, 
                       file_name.split(".")[-1] if "." in file_name else "file")
    await db.update_order_status(order_id, "ready")
    
    # Send to user
    try:
        lang = await db.get_user_language(order["user_id"])
        await message.bot.send_document(
            order["user_id"],
            file_id,
            caption=f"✅ Buyurtma #{order_id} tayyor!\n\n📂 Fayl: {file_name}"
        )
        
        # Ask for rating
        from keyboards.inline_kb import get_rating_kb
        await message.bot.send_message(
            order["user_id"],
            get_text("rate_order", lang),
            reply_markup=get_rating_kb()
        )
    except Exception as e:
        await message.answer(f"⚠️ Foydalanuvchiga yuborishda xatolik: {e}")
    
    await message.answer(f"✅ Fayl #{order_id} buyurtma uchun yuborildi!")
    await state.clear()


@router.callback_query(F.data.startswith("adm_reject_"))
async def admin_reject_order(callback: CallbackQuery):
    """Reject an order."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔")
        return
    
    order_id = int(callback.data.replace("adm_reject_", ""))
    order = await db.get_order(order_id)
    
    if order:
        await db.update_order_status(order_id, "cancelled")
        # Refund
        await db.add_balance(order["user_id"], order["price"])
        
        try:
            await callback.bot.send_message(
                order["user_id"],
                f"❌ Buyurtma #{order_id} bekor qilindi.\n💰 {order['price']} so'm qaytarildi.",
                parse_mode="HTML"
            )
        except Exception:
            pass
    
    await callback.message.edit_text(
        callback.message.text + "\n\n❌ <b>RAD ETILDI</b>",
        parse_mode="HTML"
    )
    await callback.answer("❌ Rad etildi")


# ===== PAYMENT CONFIRMATION =====

@router.callback_query(F.data.startswith("pay_confirm_"))
async def admin_confirm_payment(callback: CallbackQuery):
    """Confirm a payment."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔")
        return
    
    payment_id = int(callback.data.replace("pay_confirm_", ""))
    result = await db.confirm_payment(payment_id)
    
    if result:
        user_id, amount = result
        try:
            lang = await db.get_user_language(user_id)
            await callback.bot.send_message(
                user_id,
                get_text("payment_confirmed", lang, amount=amount),
                parse_mode="HTML"
            )
        except Exception:
            pass

        # Balans to'ldirildi — kutilayotgan buyurtma bo'lsa, davom ettirishni taklif qilamiz
        try:
            from handlers.resume import notify_if_can_resume
            await notify_if_can_resume(callback.bot, user_id)
        except Exception:
            pass

        await callback.message.edit_caption(
            caption=callback.message.caption + "\n\n✅ <b>TASDIQLANDI</b>",
            parse_mode="HTML"
        )
    
    await callback.answer("✅ Tasdiqlandi")


@router.callback_query(F.data.startswith("pay_reject_"))
async def admin_reject_payment(callback: CallbackQuery):
    """Reject a payment."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔")
        return
    
    payment_id = int(callback.data.replace("pay_reject_", ""))
    
    await callback.message.edit_caption(
        caption=callback.message.caption + "\n\n❌ <b>RAD ETILDI</b>",
        parse_mode="HTML"
    )
    await callback.answer("❌ Rad etildi")


# ===== BROADCAST =====

@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_start(callback: CallbackQuery, state: FSMContext):
    """Start broadcast."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔")
        return
    
    await state.set_state(AdminStates.broadcasting)
    await callback.message.answer("📢 Xabar matnini yuboring (barcha foydalanuvchilarga yuboriladi):")
    await callback.answer()


@router.message(AdminStates.broadcasting)
async def admin_broadcast_send(message: Message, state: FSMContext):
    """Send broadcast message."""
    if not is_admin(message.from_user.id):
        return
    if message.text and message.text.strip() in ["/bekor", "bekor", "❌"]:
        await state.clear()
        await message.answer("✅ Bekor qilindi")
        return
    await _do_broadcast(message, message.text)
    await state.clear()


# ===== PROMO CODES =====

@router.callback_query(F.data == "admin_promos")
async def admin_promos(callback: CallbackQuery, state: FSMContext):
    """Promo code management."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔")
        return
    
    await state.set_state(AdminStates.adding_promo)
    await callback.message.answer(
        "🎫 Yangi promo kod yaratish:\n\n"
        "Format: KOD SUMMA FOYDALANISH_SONI\n"
        "Masalan: BONUS5000 5000 100\n\n"
        "Yoki 'bekor' deb yozing."
    )
    await callback.answer()


@router.message(AdminStates.adding_promo)
async def admin_create_promo(message: Message, state: FSMContext):
    """Create promo code."""
    if not is_admin(message.from_user.id):
        return
    
    if message.text.lower() == "bekor":
        await state.clear()
        await message.answer("❌ Bekor qilindi")
        return
    
    try:
        parts = message.text.split()
        code = parts[0].upper()
        amount = int(parts[1])
        max_uses = int(parts[2]) if len(parts) > 2 else 100
        
        await db.create_promo(code, discount_amount=amount, max_uses=max_uses)
        await message.answer(
            f"✅ Promo kod yaratildi!\n\n"
            f"🎫 Kod: <code>{code}</code>\n"
            f"💰 Summa: {amount} so'm\n"
            f"👥 Max foydalanish: {max_uses}",
            parse_mode="HTML"
        )
    except (ValueError, IndexError):
        await message.answer("❌ Noto'g'ri format. Qayta kiriting.")
        return
    
    await state.clear()
