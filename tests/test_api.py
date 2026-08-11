"""Tests for the Beszel API client."""

import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import support  # noqa: F401
from pocketbase.utils import ClientResponseError

from custom_components.beszel.api import BeszelApiAuthError, BeszelApiClient


class BeszelApiClientTests(unittest.IsolatedAsyncioTestCase):
    """Exercise Beszel API authentication behaviour."""

    async def test_authentication_falls_back_to_users(self):
        """Authentication supports current and legacy PocketBase collections."""
        superusers = MagicMock()
        superusers.auth_with_password.side_effect = ClientResponseError(status=404)
        users = MagicMock()

        pocketbase = MagicMock()
        pocketbase.collection.side_effect = {
            "_superusers": superusers,
            "users": users,
        }.get

        with patch("custom_components.beszel.api.PocketBase", return_value=pocketbase):
            client = BeszelApiClient("beszel.local/", "user", "password")
            await client.async_authenticate()

        self.assertEqual(client.host, "http://beszel.local")
        superusers.auth_with_password.assert_called_once_with("user", "password")
        users.auth_with_password.assert_called_once_with("user", "password")

    async def test_authentication_prefers_superusers(self):
        """Authentication stops after the current collection succeeds."""
        superusers = MagicMock()
        users = MagicMock()

        pocketbase = MagicMock()
        pocketbase.collection.side_effect = {
            "_superusers": superusers,
            "users": users,
        }.get

        with patch("custom_components.beszel.api.PocketBase", return_value=pocketbase):
            client = BeszelApiClient("https://beszel.local", "user", "password")
            await client.async_authenticate()

        superusers.auth_with_password.assert_called_once_with("user", "password")
        users.auth_with_password.assert_not_called()

    async def test_missing_latest_statistics_returns_none(self):
        """The absence of a statistics record remains unavailable data."""
        collection = MagicMock()
        collection.get_list.return_value = SimpleNamespace(items=[])
        pocketbase = MagicMock()
        pocketbase.collection.return_value = collection

        with patch("custom_components.beszel.api.PocketBase", return_value=pocketbase):
            client = BeszelApiClient("beszel.local", "user", "password")
            client._ensure_auth = AsyncMock()
            result = await client.async_get_latest_system_stats("system")

        self.assertIsNone(result)

    async def test_statistics_authentication_failure_is_raised(self):
        """An expired statistics token is exposed as an authentication error."""
        collection = MagicMock()
        collection.get_list.side_effect = ClientResponseError(status=401)
        pocketbase = MagicMock()
        pocketbase.collection.return_value = collection

        with patch("custom_components.beszel.api.PocketBase", return_value=pocketbase):
            client = BeszelApiClient("beszel.local", "user", "password")
            client._ensure_auth = AsyncMock()
            client._is_authenticated = True
            with self.assertRaises(BeszelApiAuthError):
                await client.async_get_latest_system_stats("system")

        self.assertFalse(client._is_authenticated)
