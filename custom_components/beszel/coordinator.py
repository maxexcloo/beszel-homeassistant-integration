"""DataUpdateCoordinator for the Beszel integration."""

import asyncio
import logging
from datetime import timedelta

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import BeszelApiAuthError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class BeszelDataUpdateCoordinator(DataUpdateCoordinator):
    """Manages fetching data from the Beszel API."""

    def __init__(self, hass, api_client, config_entry_id, update_interval_seconds):
        """Initialise the data update coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval_seconds),
        )
        self.api_client = api_client
        self.config_entry_id = config_entry_id
        self.systems_list = []

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        try:
            systems = await self.api_client.async_get_systems()
            if not isinstance(systems, list):
                raise TypeError("Beszel Hub returned an invalid systems response")

            self.systems_list = systems
            if not systems:
                _LOGGER.info("No systems found on Beszel Hub %s", self.api_client.host)
                return {}

            all_system_data = {}
            systems_with_ids = []
            for system in systems:
                if isinstance(system, dict) and system.get("id"):
                    systems_with_ids.append(system)
                    continue
                _LOGGER.warning(
                    "Ignoring system without an ID from Beszel Hub %s: %r",
                    self.api_client.host,
                    system,
                )
            tasks = [
                self._fetch_individual_system_data(system)
                for system in systems_with_ids
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for system, result in zip(systems_with_ids, results, strict=True):
                system_id = system["id"]
                if isinstance(result, asyncio.CancelledError):
                    raise result
                if isinstance(result, BeszelApiAuthError):
                    raise result
                if isinstance(result, Exception):
                    _LOGGER.error(
                        "Error fetching data from Beszel Hub %s for system %s (%s): %s",
                        self.api_client.host,
                        system.get("name", system_id),
                        system_id,
                        result,
                    )
                    cached_data = (self.data or {}).get(system_id, {})
                    if not isinstance(cached_data, dict):
                        cached_data = {}
                    info = system.get("info")
                    if info is None:
                        info = cached_data.get("info")
                    all_system_data[system_id] = {
                        **cached_data,
                        "error": str(result),
                        "id": system_id,
                        "info": info,
                        "name": system.get("name", system_id),
                        "stats": cached_data.get("stats"),
                        "status": system.get("status", "unknown"),
                    }
                else:
                    all_system_data[system_id] = result

            return all_system_data

        except BeszelApiAuthError as err:
            raise ConfigEntryAuthFailed(
                f"Authentication failed for Beszel Hub {self.api_client.host}: {err}"
            ) from err
        except Exception as err:
            raise UpdateFailed(
                f"Error communicating with Beszel Hub {self.api_client.host}: {err}"
            ) from err

    async def _fetch_individual_system_data(self, system):
        """Fetch stats and 'info' for a single system."""
        system_id = system["id"]
        stats = await self.api_client.async_get_latest_system_stats(system_id)

        return {
            "id": system_id,
            "info": system.get("info"),
            "name": system.get("name", system_id),
            "stats": stats,
            "status": system.get("status", "unknown"),
        }
