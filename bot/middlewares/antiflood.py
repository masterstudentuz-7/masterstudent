from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
import time


class AntiFloodMiddleware(BaseMiddleware):
    """Simple anti-flood middleware."""
    
    def __init__(self, rate_limit: float = 0.5):
        self.rate_limit = rate_limit
        self.users: Dict[int, float] = {}
    
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
                    return  # Skip message (rate limited)
            
            self.users[user_id] = current_time
        
        return await handler(event, data)
