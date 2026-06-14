from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
from locales import get_text
from keyboards.main_kb import get_main_menu_kb, get_cancel_kb
from services.ai_service import ai_chat

router = Router()


class AIHelperStates(StatesGroup):
    chatting = State()


@router.message(F.text.in_(["🤖 NOVA AI Yordamchi", "🤖 AI Yordamchi", "🤖 NOVA AI Помощник", "🤖 AI Помощник", "🤖 NOVA AI Helper", "🤖 AI Helper"]))
async def ai_helper_start(message: Message, state: FSMContext):
    """Start NOVA AI helper conversation."""
    lang = await db.get_user_language(message.from_user.id)
    await state.set_state(AIHelperStates.chatting)
    await message.answer(
        get_text("ai_helper_prompt", lang),
        reply_markup=get_cancel_kb(lang),
        parse_mode="HTML"
    )


@router.message(AIHelperStates.chatting)
async def ai_helper_message(message: Message, state: FSMContext):
    """Handle NOVA AI helper messages."""
    lang = await db.get_user_language(message.from_user.id)
    
    # Check for cancel/back
    if message.text and message.text.lower() in ["bekor", "отмена", "cancel", "❌ bekor qilish", "❌ отмена", "❌ cancel", "⬅️ ortga", "⬅️ назад", "⬅️ back"]:
        await state.clear()
        await message.answer(
            get_text("main_menu", lang),
            reply_markup=get_main_menu_kb(lang),
            parse_mode="HTML"
        )
        return
    
    # Process with NOVA AI
    try:
        response = await ai_chat(message.text, lang)
        await message.answer(f"🤖 <b>NOVA AI:</b> {response}", parse_mode="HTML")
    except Exception:
        await message.answer(get_text("error_generic", lang))
