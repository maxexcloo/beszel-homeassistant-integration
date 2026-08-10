"""Tests for the Beszel config flow."""

import unittest
from unittest.mock import AsyncMock, patch

from support import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USERNAME,
    FakeHomeAssistant,
    FlowResultType,
)

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
