"""Config flow for the Beszel integration."""

import logging

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME

from .api import BeszelApiAuthError, BeszelApiClient
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class BeszelConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Beszel."""

    VERSION = 2

    async def _async_validate_input(self, user_input):
        """Validate Beszel connection details."""
        api_client = BeszelApiClient(
            user_input[CONF_HOST],
            user_input[CONF_USERNAME],
            user_input[CONF_PASSWORD],
        )
        await api_client.async_authenticate()
        return api_client

    def _schema_with_defaults(self, data):
        """Return the connection schema populated with safe defaults."""
        return vol.Schema(
            {
                vol.Required(CONF_HOST, default=data.get(CONF_HOST, "")): str,
                vol.Required(CONF_USERNAME, default=data.get(CONF_USERNAME, "")): str,
                vol.Required(CONF_PASSWORD): str,
            }
        )

    async def async_step_reauth(self, entry_data):
        """Start reauthentication for an existing entry."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None):
        """Confirm updated credentials for an existing entry."""
        entry = self._get_reauth_entry()
        errors = {}

        if user_input is not None:
            updated_data = {**entry.data, CONF_PASSWORD: user_input[CONF_PASSWORD]}
            try:
                await self._async_validate_input(updated_data)
            except BeszelApiAuthError:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception during reauthentication")
                errors["base"] = "cannot_connect"
            else:
                return self.async_update_reload_and_abort(entry, data=updated_data)

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_PASSWORD): str}),
            errors=errors,
        )

    async def async_step_reconfigure(self, user_input=None):
        """Reconfigure an existing entry."""
        entry = self._get_reconfigure_entry()
        errors = {}

        if user_input is not None:
            try:
                api_client = await self._async_validate_input(user_input)
            except BeszelApiAuthError:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception during reconfiguration")
                errors["base"] = "cannot_connect"
            else:
                unique_id = f"{api_client.host}_{user_input[CONF_USERNAME]}"
                existing_entry = (
                    self.hass.config_entries.async_entry_for_domain_unique_id(
                        DOMAIN, unique_id
                    )
                )
                if existing_entry and existing_entry.entry_id != entry.entry_id:
                    errors["base"] = "already_configured"
                else:
                    return self.async_update_reload_and_abort(
                        entry,
                        unique_id=unique_id,
                        title=api_client.host,
                        data={**user_input, CONF_HOST: api_client.host},
                    )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self._schema_with_defaults(entry.data),
            errors=errors,
        )

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            try:
                api_client = await self._async_validate_input(user_input)
            except BeszelApiAuthError:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception during setup")
                errors["base"] = "cannot_connect"
            else:
                unique_id = f"{api_client.host}_{user_input[CONF_USERNAME]}"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=api_client.host,
                    data={**user_input, CONF_HOST: api_client.host},
                )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )
