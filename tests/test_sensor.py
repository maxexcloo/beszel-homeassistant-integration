"""Tests for Beszel sensors."""

import unittest
from unittest.mock import MagicMock

from support import FakeHomeAssistant, SensorDeviceClass, UnitOfTime

from custom_components.beszel.const import DOMAIN
from custom_components.beszel.sensor import (
    _create_available_sensors,
    async_setup_entry,
)


class BeszelSensorTests(unittest.IsolatedAsyncioTestCase):
    """Exercise Beszel sensor discovery behaviour."""

    def test_sensor_discovery_uses_reported_values_and_scoped_ids(self):
        """Discovery omits missing rates and scopes identifiers."""
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

        self.assertIn("beszel_entry_system_stats_cpu", unique_ids)
        self.assertNotIn("beszel_entry_system_stats_dr", unique_ids)
        self.assertNotIn("beszel_entry_system_stats_dw", unique_ids)

        uptime = next(
            sensor for sensor in sensors if sensor.unique_id.endswith("_info_u")
        )
        self.assertIs(uptime.device_class, SensorDeviceClass.DURATION)
        self.assertIs(uptime.native_unit_of_measurement, UnitOfTime.SECONDS)
        self.assertEqual(uptime.native_value, 90)
        self.assertEqual(
            uptime.device_info["identifiers"], {("beszel", "entry_system")}
        )

    def test_new_metrics_are_discovered_on_later_data(self):
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
        later_ids = {
            sensor.unique_id for sensor in _create_available_sensors(coordinator)
        }

        self.assertNotIn("beszel_entry_system_stats_dr", initial_ids)
        self.assertIn("beszel_entry_system_stats_dr", later_ids)
        self.assertIn(
            "beszel_entry_system_stats_disk_io_utilisation_percent", later_ids
        )

    async def test_platform_adds_new_metrics_after_setup(self):
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
        hass = FakeHomeAssistant()
        hass.data[DOMAIN] = {"entry": coordinator}

        entry = MagicMock()
        entry.entry_id = "entry"
        async_add_entities = MagicMock()

        await async_setup_entry(hass, entry, async_add_entities)
        initial_entities = async_add_entities.call_args.args[0]
        self.assertEqual(
            {entity.unique_id for entity in initial_entities},
            {"beszel_entry_system_status_status"},
        )

        coordinator.data["system"]["stats"] = {"cpu": 12.5}
        listener = coordinator.async_add_listener.call_args.args[0]
        listener()

        later_entities = async_add_entities.call_args.args[0]
        self.assertEqual(
            {entity.unique_id for entity in later_entities},
            {"beszel_entry_system_stats_cpu"},
        )
