import aiohttp
from config import settings


class BackendClient:
    def __init__(self) -> None:
        # AnyUrl → str, иначе .rstrip() не сработает
        self._base_url = str(settings.api_base_url).rstrip("/")
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if not self._session or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def get_user(self, user_id: int) -> dict:
        session = await self._get_session()
        async with session.get(f"{self._base_url}/users/{user_id}") as resp:
            resp.raise_for_status()
            return await resp.json()

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()


backend = BackendClient()
