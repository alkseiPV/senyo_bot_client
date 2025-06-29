import aiohttp
from typing import Any, Dict, Optional

from config import settings


class _BaseAPI:
    """
    Единственный низкоуровневый клиент для всего проекта.
    Создаёт и держит одну aiohttp-сессию.
    """

    def __init__(self) -> None:
        self._base_url: str = str(settings.api_base_url).rstrip("/")
        self._session: aiohttp.ClientSession | None = None
        self._timeout = aiohttp.ClientTimeout(total=30)

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self._timeout)
        return self._session

    # ------------ HTTP wrappers ------------ #
    async def get(self, path: str, **kw) -> Any:
        ses = await self._get_session()
        async with ses.get(f"{self._base_url}{path}", **kw) as r:
            r.raise_for_status()
            return await r.json()

    async def post(self, path: str, **kw) -> Any:
        ses = await self._get_session()
        async with ses.post(f"{self._base_url}{path}", **kw) as r:
            r.raise_for_status()
            return await _maybe_json(r)

    async def put(self, path: str, **kw) -> Any:
        ses = await self._get_session()
        async with ses.put(f"{self._base_url}{path}", **kw) as r:
            r.raise_for_status()
            return await _maybe_json(r)

    async def delete(self, path: str, **kw) -> Any:
        ses = await self._get_session()
        async with ses.delete(f"{self._base_url}{path}", **kw) as r:
            r.raise_for_status()
            return await _maybe_json(r)

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()


async def _maybe_json(resp: aiohttp.ClientResponse) -> Optional[Dict[str, Any]]:
    return await resp.json() if resp.content_type == "application/json" and resp.content_length else None


base_api = _BaseAPI()          # singleton, импортируем где нужно
