from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
import time


class AntiFloodMiddleware(BaseMiddleware):
    """Anti-flood middleware — spam himoyasi."""
    
    def __init__(self, rate_limit: float = 0.5):
        self.rate_limit = rate_limit
        self.users: Dict[int, float] = {}
        self.warnings: Dict[int, int] = {}
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, Message):
            user_id = event.from_user.id
            current_time = time.time()
            
            if user_id in self.users:
                last_time = self.users[user_id]
                if current_time - last_time < self.rate_limit:
                    self.warnings[user_id] = self.warnings.get(user_id, 0) + 1
                    if self.warnings[user_id] == 3:
                        await event.answer("⚠️ Iltimos, sekinroq yozing!")
                        self.warnings[user_id] = 0
                    return
            
            self.users[user_id] = current_time
        
        return await handler(event, data)


class UserActivityMiddleware(BaseMiddleware):
    """Foydalanuvchi aktivligini kuzatish."""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, (Message, CallbackQuery)):
            try:
                import database as db
                await db.update_user_activity(event.from_user.id)
            except Exception:
                pass
        
        return await handler(event, data)
