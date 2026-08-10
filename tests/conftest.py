"""Minimal Home Assistant test doubles used by the unit tests."""

import sys
from enum import Enum
from types import ModuleType, SimpleNamespace
from uuid import uuid4

import pytest


class _Entity:
    """Expose Home Assistant-style class attributes as properties."""

    def __getattr__(self, name):
        attr_name = f"_attr_{name}"
        if attr_name in self.__dict__:
            return self.__dict__[attr_name]
        raise AttributeError(name)


class _SensorEntity(_Entity):
    """Minimal sensor entity base class."""


class _CoordinatorEntity(_Entity):
    """Minimal coordinator-backed entity base class."""

    def __init__(self, coordinator):
        self.coordinator = coordinator

    @property
    def available(self):
        """Return the coordinator availability."""
        return self.coordinator.last_update_success

    def _handle_coordinator_update(self):
        """Handle a coordinator update."""


class _DataUpdateCoordinator:
    """Minimal data update coordinator base class."""

    def __init__(self, hass, logger, *, name, update_interval):
        self.data = None
        self.hass = hass
        self.last_update_success = True
        self.logger = logger
        self.name = name
        self.update_interval = update_interval

    async def async_config_entry_first_refresh(self):
        """Fetch the initial data snapshot."""
        self.data = await self._async_update_data()


class _ConfigFlow:
    """Minimal config flow base class."""

    def __init_subclass__(cls, *, domain=None, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.DOMAIN = domain

    def __init__(self):
        self.hass = None
        self._unique_id = None

    async def async_set_unique_id(self, unique_id):
        """Store the proposed unique identifier."""
        self._unique_id = unique_id

    def _abort_if_unique_id_configured(self):
        """Accept an unconfigured unique identifier."""

    def async_create_entry(self, *, title, data):
        """Return a config-entry flow result."""
        return {
            "data": data,
            "result": SimpleNamespace(unique_id=self._unique_id),
            "title": title,
            "type": _FlowResultType.CREATE_ENTRY,
        }

    def async_show_form(self, *, step_id, data_schema, errors):
        """Return a form flow result."""
        return {
            "data_schema": data_schema,
            "errors": errors,
            "step_id": step_id,
            "type": _FlowResultType.FORM,
        }


class _FlowResultType(Enum):
    CREATE_ENTRY = "create_entry"
    FORM = "form"


class _SensorDeviceClass(Enum):
    BATTERY = "battery"
    DATA_RATE = "data_rate"
    DATA_SIZE = "data_size"
    DURATION = "duration"
    ENUM = "enum"
    POWER = "power"
    TEMPERATURE = "temperature"


class _SensorStateClass(Enum):
    MEASUREMENT = "measurement"


class _Platform(Enum):
    SENSOR = "sensor"


class _UnitOfDataRate(Enum):
    MEGABYTES_PER_SECOND = "MB/s"


class _UnitOfInformation(Enum):
    GIGABYTES = "GB"
    MEGABYTES = "MB"


class _UnitOfPower(Enum):
    WATT = "W"


class _UnitOfTemperature(Enum):
    CELSIUS = "°C"


class _UnitOfTime(Enum):
    MILLISECONDS = "ms"
    SECONDS = "s"


class _EntityRegistry:
    """In-memory entity registry."""

    def __init__(self):
        self.entities = {}

    def async_get_or_create(self, platform, domain, unique_id, *, config_entry):
        """Create an entity registry entry."""
        entity_id = f"{platform}.{unique_id}"
        entity = SimpleNamespace(
            config_entry_id=config_entry.entry_id,
            entity_id=entity_id,
            unique_id=unique_id,
        )
        self.entities[entity_id] = entity
        return entity

    def async_get(self, entity_id):
        """Return an entity registry entry."""
        return self.entities.get(entity_id)

    def async_update_entity(self, entity_id, *, new_unique_id):
        """Update an entity registry entry."""
        self.entities[entity_id].unique_id = new_unique_id


class _DeviceRegistry:
    """In-memory device registry."""

    def __init__(self):
        self.devices = {}

    def async_get_or_create(self, *, config_entry_id, identifiers):
        """Create a device registry entry."""
        device_id = uuid4().hex
        device = SimpleNamespace(
            config_entries={config_entry_id},
            id=device_id,
            identifiers=identifiers,
        )
        self.devices[device_id] = device
        return device

    def async_get(self, device_id):
        """Return a device registry entry."""
        return self.devices.get(device_id)

    def async_update_device(self, device_id, *, new_identifiers):
        """Update a device registry entry."""
        self.devices[device_id].identifiers = new_identifiers


class _ConfigEntries:
    """Minimal config entry manager."""

    def async_update_entry(self, entry, **changes):
        """Apply changes to a config entry."""
        for key, value in changes.items():
            setattr(entry, key, value)


class FakeHomeAssistant:
    """Small Home Assistant object used by unit tests."""

    def __init__(self):
        self.config_entries = _ConfigEntries()
        self.data = {}
        self.device_registry = _DeviceRegistry()
        self.entity_registry = _EntityRegistry()


def _module(name, **attributes):
    """Install a module test double."""
    module = ModuleType(name)
    for attribute, value in attributes.items():
        setattr(module, attribute, value)
    sys.modules[name] = module
    return module


def _install_homeassistant_test_doubles():
    """Install only the Home Assistant interfaces imported by this project."""
    homeassistant = _module("homeassistant")
    components = _module("homeassistant.components")
    helpers = _module("homeassistant.helpers")

    config_entries = _module("homeassistant.config_entries", ConfigFlow=_ConfigFlow)
    const = _module(
        "homeassistant.const",
        CONF_HOST="host",
        CONF_PASSWORD="password",
        CONF_USERNAME="username",
        PERCENTAGE="%",
        Platform=_Platform,
        UnitOfDataRate=_UnitOfDataRate,
        UnitOfInformation=_UnitOfInformation,
        UnitOfPower=_UnitOfPower,
        UnitOfTemperature=_UnitOfTemperature,
        UnitOfTime=_UnitOfTime,
    )
    core = _module("homeassistant.core", callback=lambda function: function)
    data_entry_flow = _module(
        "homeassistant.data_entry_flow", FlowResultType=_FlowResultType
    )
    exceptions = _module(
        "homeassistant.exceptions",
        ConfigEntryAuthFailed=type("ConfigEntryAuthFailed", (Exception,), {}),
    )
    sensor = _module(
        "homeassistant.components.sensor",
        SensorDeviceClass=_SensorDeviceClass,
        SensorEntity=_SensorEntity,
        SensorStateClass=_SensorStateClass,
    )
    device_registry = _module(
        "homeassistant.helpers.device_registry",
        async_entries_for_config_entry=lambda registry, entry_id: [
            device
            for device in registry.devices.values()
            if entry_id in device.config_entries
        ],
        async_get=lambda hass: hass.device_registry,
    )
    entity_registry = _module(
        "homeassistant.helpers.entity_registry",
        async_entries_for_config_entry=lambda registry, entry_id: [
            entity
            for entity in registry.entities.values()
            if entity.config_entry_id == entry_id
        ],
        async_get=lambda hass: hass.entity_registry,
    )
    update_coordinator = _module(
        "homeassistant.helpers.update_coordinator",
        CoordinatorEntity=_CoordinatorEntity,
        DataUpdateCoordinator=_DataUpdateCoordinator,
        UpdateFailed=type("UpdateFailed", (Exception,), {}),
    )

    homeassistant.components = components
    homeassistant.config_entries = config_entries
    homeassistant.const = const
    homeassistant.core = core
    homeassistant.data_entry_flow = data_entry_flow
    homeassistant.exceptions = exceptions
    homeassistant.helpers = helpers
    components.sensor = sensor
    helpers.device_registry = device_registry
    helpers.entity_registry = entity_registry
    helpers.update_coordinator = update_coordinator


_install_homeassistant_test_doubles()


@pytest.fixture
def hass():
    """Return a minimal Home Assistant test double."""
    return FakeHomeAssistant()
