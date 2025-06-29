from typing import Any, Callable, Dict

from aiogram import BaseMiddleware

class BackendMiddleware(BaseMiddleware):
# Прокидывает экземпляр бэка в каждый хендлер через data['backend']
    def __init__(self, backend_client)-> None:
        self.backend = backend_client
    
    async def __call__(self, handler: Callable, event:Any,data:Dict[str,Any],):
        data["backend"] = self.backend
        return await handler(event,data)
