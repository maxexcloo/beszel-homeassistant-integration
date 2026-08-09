"""Tests for Beszel sensors."""

from unittest.mock import MagicMock

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import UnitOfTime

from custom_components.beszel.const import DOMAIN
from custom_components.beszel.sensor import (
    _create_available_sensors,
    async_setup_entry,
)


def test_sensor_discovery_uses_reported_values_and_scoped_ids():
    """Discovery omits missing rates and scopes identifiers to the config entry."""
    coordinator = MagicMock()
    coordinator.config_entry_id = "entry"
    coordinator.data = {
        "system": {
            "id": "system",
            "info": {"u": 90},
            "name": "Server",
            "stats": {"cpu": 12.5},
            "status": "up",
        }
    }

    sensors = _create_available_sensors(coordinator)
    unique_ids = {sensor.unique_id for sensor in sensors}

    assert "beszel_entry_system_stats_cpu" in unique_ids
    assert "beszel_entry_system_stats_dr" not in unique_ids
    assert "beszel_entry_system_stats_dw" not in unique_ids

    uptime = next(sensor for sensor in sensors if sensor.unique_id.endswith("_info_u"))
    assert uptime.device_class is SensorDeviceClass.DURATION
    assert uptime.native_unit_of_measurement is UnitOfTime.SECONDS
    assert uptime.native_value == 90
    assert uptime.device_info["identifiers"] == {("beszel", "entry_system")}


def test_new_metrics_are_discovered_on_later_data():
    """A later coordinator snapshot exposes newly reported metrics."""
    coordinator = MagicMock()
    coordinator.config_entry_id = "entry"
    coordinator.data = {
        "system": {
            "id": "system",
            "info": {},
            "name": "Server",
            "stats": {},
            "status": "up",
        }
    }
    initial_ids = {
        sensor.unique_id for sensor in _create_available_sensors(coordinator)
    }

    coordinator.data["system"]["stats"] = {
        "dios": [1, 2, 3, 4, 5, 6],
        "dr": 1.5,
    }
    later_ids = {sensor.unique_id for sensor in _create_available_sensors(coordinator)}

    assert "beszel_entry_system_stats_dr" not in initial_ids
    assert "beszel_entry_system_stats_dr" in later_ids
    assert "beszel_entry_system_stats_disk_io_utilisation_percent" in later_ids


async def test_platform_adds_new_metrics_after_setup(hass):
    """The coordinator listener adds a metric that appears after setup."""
    coordinator = MagicMock()
    coordinator.config_entry_id = "entry"
    coordinator.data = {
        "system": {
            "id": "system",
            "info": {},
            "name": "Server",
            "stats": {},
            "status": "up",
        }
    }
    hass.data[DOMAIN] = {"entry": coordinator}

    entry = MagicMock()
    entry.entry_id = "entry"
    async_add_entities = MagicMock()

    await async_setup_entry(hass, entry, async_add_entities)
    initial_entities = async_add_entities.call_args.args[0]
    assert {entity.unique_id for entity in initial_entities} == {
        "beszel_entry_system_status_status"
    }

    coordinator.data["system"]["stats"] = {"cpu": 12.5}
    listener = coordinator.async_add_listener.call_args.args[0]
    listener()

    later_entities = async_add_entities.call_args.args[0]
    assert {entity.unique_id for entity in later_entities} == {
        "beszel_entry_system_stats_cpu"
    }
