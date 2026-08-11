"""Tests for the Beszel config flow."""

import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from support import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USERNAME,
    FakeHomeAssistant,
    FlowResultType,
)

from custom_components.beszel.api import BeszelApiAuthError
from custom_components.beszel.config_flow import BeszelConfigFlow


class BeszelConfigFlowTests(unittest.IsolatedAsyncioTestCase):
    """Exercise the Beszel config flow."""

    async def test_user_flow_normalises_host(self):
        """The user flow stores lower-case keys and a normalised host."""
        with patch("custom_components.beszel.config_flow.BeszelApiClient") as api_class:
            api_class.return_value.async_authenticate = AsyncMock()
            api_class.return_value.host = "http://beszel.local"
            flow = BeszelConfigFlow()
            flow.hass = FakeHomeAssistant()
            result = await flow.async_step_user(
                {
                    CONF_HOST: "beszel.local/",
                    CONF_USERNAME: "user",
                    CONF_PASSWORD: "password",
                }
            )

        self.assertIs(result["type"], FlowResultType.CREATE_ENTRY)
        self.assertEqual(
            result["data"],
            {
                CONF_HOST: "http://beszel.local",
                CONF_PASSWORD: "password",
                CONF_USERNAME: "user",
            },
        )
        self.assertEqual(result["result"].unique_id, "http://beszel.local_user")

    async def test_user_flow_reports_invalid_authentication(self):
        """Invalid credentials return the translated authentication error."""
        with patch("custom_components.beszel.config_flow.BeszelApiClient") as api_class:
            api_class.return_value.async_authenticate = AsyncMock(
                side_effect=BeszelApiAuthError("invalid credentials")
            )
            flow = BeszelConfigFlow()
            flow.hass = FakeHomeAssistant()
            result = await flow.async_step_user(
                {
                    CONF_HOST: "beszel.local",
                    CONF_PASSWORD: "wrong",
                    CONF_USERNAME: "user",
                }
            )

        self.assertIs(result["type"], FlowResultType.FORM)
        self.assertEqual(result["errors"], {"base": "invalid_auth"})

    async def test_reauthentication_updates_only_the_password(self):
        """Reauthentication retains the configured Hub and username."""
        entry = SimpleNamespace(
            data={
                CONF_HOST: "http://beszel.local",
                CONF_PASSWORD: "old",
                CONF_USERNAME: "user",
            }
        )
        with patch("custom_components.beszel.config_flow.BeszelApiClient") as api_class:
            api_class.return_value.async_authenticate = AsyncMock()
            flow = BeszelConfigFlow()
            flow._get_reauth_entry = MagicMock(return_value=entry)
            flow.async_update_reload_and_abort = MagicMock(
                return_value={"type": "abort"}
            )
            result = await flow.async_step_reauth_confirm(
                {CONF_PASSWORD: "new-password"}
            )

        self.assertEqual(result, {"type": "abort"})
        self.assertEqual(
            flow.async_update_reload_and_abort.call_args.kwargs["data"],
            {
                CONF_HOST: "http://beszel.local",
                CONF_PASSWORD: "new-password",
                CONF_USERNAME: "user",
            },
        )
