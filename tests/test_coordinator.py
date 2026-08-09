"""Tests for the Beszel data coordinator."""

from custom_components.beszel.coordinator import BeszelDataUpdateCoordinator


class FakeApiClient:
    """Return deterministic Beszel data."""

    async def async_authenticate(self):
        """Authenticate successfully."""

    async def async_get_latest_system_stats(self, system_id):
        """Return stats or fail for one system."""
        if system_id == "failed":
            raise RuntimeError("stats unavailable")
        return {"cpu": 12.5}

    async def async_get_systems(self):
        """Return one malformed and two valid systems."""
        return [
            {"name": "Malformed"},
            {"id": "healthy", "name": "Healthy", "status": "up"},
            {"id": "failed", "name": "Failed", "status": "down"},
        ]


async def test_results_remain_mapped_and_failures_use_cache(hass):
    """Malformed systems do not shift results and failures retain cached data."""
    coordinator = BeszelDataUpdateCoordinator(
        hass,
        api_client=FakeApiClient(),
        config_entry_id="entry",
        update_interval_seconds=60,
    )
    coordinator.data = {
        "failed": {
            "id": "failed",
            "info": {},
            "name": "Failed",
            "stats": {"cpu": 20},
            "status": "up",
        }
    }

    data = await coordinator._async_update_data()

    assert data["healthy"]["stats"] == {"cpu": 12.5}
    assert data["failed"]["stats"] == {"cpu": 20}
    assert data["failed"]["status"] == "down"
    assert data["failed"]["error"] == "stats unavailable"
