"""API for Beszel."""

import asyncio
from typing import Any, List, Dict

from pocketbase import PocketBase
from pocketbase.utils import ClientResponseError, validate_token


class BeszelApiAuthError(Exception):
    """Custom exception for authentication errors."""


class BeszelApiClient:
    """Beszel API Client."""

    def __init__(self, host: str, username: str, password: str) -> None:
        """Initialize the API client."""
        if not host.startswith(("http://", "https://")):
            host = f"http://{host}"
        self._host = host
        self._username = username
        self._password = password
        self._client = PocketBase(self._host)
        self._is_authenticated = False

    async def async_authenticate(self) -> None:
        """Authenticate with the Beszel Hub."""
        if (
            self._is_authenticated
            and self._client.auth_store.token
            and self._client.auth_store.model
            and validate_token(self._client.auth_store.token)
        ):
            return

        try:
            await asyncio.to_thread(
                self._client.collection("users").auth_with_password,
                self._username,
                self._password,
            )
            self._is_authenticated = True
        except ClientResponseError as e:
            self._is_authenticated = False
            raise BeszelApiAuthError("Authentication failed") from e

    async def _ensure_auth(self) -> None:
        """Ensure the client is authenticated before making a request."""
        if not (
            self._is_authenticated
            and self._client.auth_store.token
            and self._client.auth_store.model
            and validate_token(self._client.auth_store.token)
        ):
            await self.async_authenticate()

    async def async_get_systems(self) -> List[Dict[str, Any]]:
        """Fetch all systems from the Beszel Hub."""
        await self._ensure_auth()
        try:
            records = await asyncio.to_thread(
                self._client.collection("systems").get_full_list,
                query_params={"sort": "-status,name"},
            )
            return [vars(record) for record in records]
        except ClientResponseError as e:
            if e.status == 401 or e.status == 403:
                self._is_authenticated = False
                raise BeszelApiAuthError(
                    "Token likely expired, re-authentication needed"
                ) from e
            raise

    async def async_get_latest_system_stats(
        self, system_id: str
    ) -> Dict[str, Any] | None:
        """Fetch the latest stats for a specific system."""
        await self._ensure_auth()
        try:
            records = await asyncio.to_thread(
                self._client.collection("system_stats").get_full_list,
                batch=1,
                query_params={
                    "filter": f'system="{system_id}"',
                    "sort": "-created",
                },
            )
            if records:
                return vars(records[0]).get("stats", {})
            return None
        except ClientResponseError as e:
            if e.status == 401 or e.status == 403:
                self._is_authenticated = False
                raise BeszelApiAuthError(
                    "Token likely expired, re-authentication needed"
                ) from e
            raise
        except IndexError:
            # This can happen if a system is registered but has no stats yet.
            return None
