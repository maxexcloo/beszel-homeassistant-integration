"""Config flow for Beszel integration."""

import logging
from typing import Any

import voluptuous as vol
from pocketbase.utils import ClientResponseError

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .const import DOMAIN
from .api import BeszelApiClient, BeszelApiAuthError

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("Host"): str,
        vol.Required("Username"): str,
        vol.Required("Password"): str,
    }
)


class BeszelConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Beszel."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                api_client = BeszelApiClient(
                    user_input["Host"],
                    user_input["Username"],
                    user_input["Password"],
                )
                await api_client.async_authenticate()
            except BeszelApiAuthError:
                errors["base"] = "invalid_auth"
            except ClientResponseError as exc:
                _LOGGER.error("PocketBase API error during connection setup: %s", exc)
                errors["base"] = "cannot_connect"
            except Exception as exc:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception during setup: %s", exc)
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(
                    f"{user_input['Host']}_{user_input['Username']}"
                )
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input["Host"], data=user_input
                )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )
