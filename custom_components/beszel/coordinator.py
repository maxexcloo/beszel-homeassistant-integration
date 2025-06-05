"""DataUpdateCoordinator for the Beszel integration."""

import asyncio
from datetime import timedelta
import logging
from typing import Dict, Any, List

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import BeszelApiClient, BeszelApiAuthError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class BeszelDataUpdateCoordinator(DataUpdateCoordinator[Dict[str, Any]]):
    """Manages fetching data from the Beszel API."""

    def __init__(
        self,
        hass: HomeAssistant,
        api_client: BeszelApiClient,
        update_interval_seconds: int,
    ) -> None:
        """Initialize the data update coordinator."""
        self.api_client = api_client
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval_seconds),
        )
        self.systems_list: List[Dict[str, Any]] = []  # Store the list of systems

    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            # Ensure client is authenticated
            await self.api_client.async_authenticate()

            # Fetch the list of systems first
            self.systems_list = await self.api_client.async_get_systems()
            if not self.systems_list:
                _LOGGER.info("No systems found.")
                return {}

            # For each system, fetch its latest stats and info
            all_system_data: Dict[str, Any] = {}
            tasks = []
            for system in self.systems_list:
                system_id = system.get("id")
                if not system_id:
                    continue  # Should not happen if API is consistent

                tasks.append(
                    self._fetch_individual_system_data(
                        system_id, system.get("name", system_id)
                    )
                )

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for i, system in enumerate(self.systems_list):
                system_id = system.get("id")
                if not system_id:
                    continue

                result = results[i]
                if isinstance(result, Exception):
                    _LOGGER.error(
                        "Error fetching data for system %s: %s", system_id, result
                    )
                    all_system_data[system_id] = {"error": str(result)}
                elif result:
                    all_system_data[system_id] = result
                else:  # Should not happen if _fetch_individual_system_data returns dict
                    all_system_data[system_id] = {
                        "error": "Unknown error fetching data"
                    }

            return all_system_data

        except BeszelApiAuthError as err:
            raise UpdateFailed(f"Authentication error: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    async def _fetch_individual_system_data(
        self, system_id: str, system_name: str
    ) -> Dict[str, Any]:
        """Fetch stats and info for a single system."""
        stats = await self.api_client.async_get_latest_system_stats(system_id)

        # The 'info' field from the system record itself (from self.systems_list)
        # is what's shown in the Beszel UI's system list and contains the summary info.
        # This is now the sole source for "info" type data for sensors.

        system_record = next(
            (s for s in self.systems_list if s.get("id") == system_id), None
        )
        device_info_summary = {}
        if system_record:
            device_info_summary = system_record.get("info", {})

        return {
            "id": system_id,
            "name": system_name,
            "stats": stats or {},
            # "info" key is now populated by device_info_summary for consistency,
            # as the separate async_get_system_info call was redundant.
            "info": device_info_summary,
            "status": (
                system_record.get("status", "unknown") if system_record else "unknown"
            ),
            "agent_version_from_record": (
                system_record.get("v", "unknown") if system_record else "unknown"
            ),  # Agent version from system record
        }
