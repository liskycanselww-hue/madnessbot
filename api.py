import asyncio
from typing import Any, Dict, List, Optional
import httpx
from config import BASE_URL


class ApiError(Exception):
    pass


class ApiClient:
    def __init__(self) -> None:
        self.base_url = BASE_URL
        self.token: Optional[str] = None
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=httpx.Timeout(20.0, connect=10.0))

    def _headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def close(self) -> None:
        await self.client.aclose()

    async def _request(self, method: str, url: str, **kwargs: Any) -> Any:
        response = await self.client.request(method, url, headers=self._headers(), **kwargs)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            message = exc.response.text
            raise ApiError(f"API request failed {url}: {message}") from exc
        if response.status_code == 204:
            return None
        return response.json()

    async def login(self, init_data: str) -> Dict[str, Any]:
        payload = {"initData": init_data}
        data = await self._request("POST", "/api/auth/telegram", json=payload)
        return data

    async def get_character(self, character_id: str) -> Dict[str, Any]:
        data = await self._request("GET", f"/api/characters/{character_id}")
        return data

    async def get_raids(self) -> List[Dict[str, Any]]:
        data = await self._request("GET", "/api/raids", params={"active": True})
        if isinstance(data, dict):
            if "raids" in data and isinstance(data["raids"], list):
                return data["raids"]
            if "data" in data and isinstance(data["data"], list):
                return data["data"]
        if isinstance(data, list):
            return data
        return []

    async def join_raid(self, raid_id: str) -> Dict[str, Any]:
        payload = {"raid_id": raid_id}
        try:
            return await self._request("POST", f"/api/raids/{raid_id}/join", json=payload)
        except ApiError:
            return await self._request("POST", f"/api/raids/join", json=payload)

    async def attack(self, raid_id: Optional[str] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {}
        if raid_id:
            payload["raid_id"] = raid_id
        return await self._request("POST", "/api/battles/attack", json=payload)

    async def get_current_battle(self) -> Dict[str, Any]:
        return await self._request("GET", "/api/battles/current")

    async def claim_reward(self) -> Dict[str, Any]:
        try:
            return await self._request("POST", "/api/battles/reward")
        except ApiError:
            return await self._request("POST", "/api/battles/claim")

    async def use_stimulant(self, character_id: str) -> Dict[str, Any]:
        try:
            return await self._request("POST", f"/api/characters/{character_id}/stimulant")
        except ApiError:
            return await self._request("POST", "/api/battles/stimulant", json={"character_id": character_id})

    async def shout_to_raid(self, raid_id: str, message: str) -> Dict[str, Any]:
        payload = {"raid_id": raid_id, "message": message}
        try:
            return await self._request("POST", f"/api/raids/{raid_id}/shout", json=payload)
        except ApiError:
            return await self._request("POST", "/api/raids/shout", json=payload)
