"""Tests for the Beszel API client."""

from unittest.mock import MagicMock, patch

from pocketbase.utils import ClientResponseError

from custom_components.beszel.api import BeszelApiClient


async def test_authentication_falls_back_to_users():
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

    assert client.host == "http://beszel.local"
    superusers.auth_with_password.assert_called_once_with("user", "password")
    users.auth_with_password.assert_called_once_with("user", "password")


async def test_authentication_prefers_superusers():
    """Authentication stops after the current PocketBase collection succeeds."""
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
