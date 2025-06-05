"""The Beszel integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS, DEFAULT_UPDATE_INTERVAL_SECONDS
from .coordinator import BeszelDataUpdateCoordinator
from .api import BeszelApiClient


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Beszel from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    host = entry.data["Host"]
    username = entry.data["Username"]
    password = entry.data["Password"]

    api_client = BeszelApiClient(host, username, password)

    coordinator = BeszelDataUpdateCoordinator(
        hass,
        api_client=api_client,
        update_interval_seconds=DEFAULT_UPDATE_INTERVAL_SECONDS,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
