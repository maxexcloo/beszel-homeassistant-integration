"""The Beszel integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .api import BeszelApiClient
from .const import DEFAULT_UPDATE_INTERVAL_SECONDS, DOMAIN, PLATFORMS
from .coordinator import BeszelDataUpdateCoordinator


async def async_setup_entry(hass, entry):
    """Set up Beszel from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    api_client = BeszelApiClient(
        entry.data["Host"], entry.data["Username"], entry.data["Password"]
    )

    coordinator = BeszelDataUpdateCoordinator(
        hass,
        api_client=api_client,
        update_interval_seconds=DEFAULT_UPDATE_INTERVAL_SECONDS,
    )

    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
