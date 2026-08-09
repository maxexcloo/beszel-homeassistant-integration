"""Tests for the Beszel config flow."""

from unittest.mock import AsyncMock, patch

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.data_entry_flow import FlowResultType

from custom_components.beszel.const import DOMAIN


async def test_user_flow_normalises_host(hass):
    """The user flow stores lower-case keys and a normalised host."""
    with (
        patch("custom_components.beszel.async_setup_entry", return_value=True),
        patch("custom_components.beszel.config_flow.BeszelApiClient") as api_class,
    ):
        api_class.return_value.async_authenticate = AsyncMock()
        api_class.return_value.host = "http://beszel.local"
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_USER},
            data={
                CONF_HOST: "beszel.local/",
                CONF_USERNAME: "user",
                CONF_PASSWORD: "password",
            },
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == {
        CONF_HOST: "http://beszel.local",
        CONF_PASSWORD: "password",
        CONF_USERNAME: "user",
    }
    assert result["result"].unique_id == "http://beszel.local_user"
