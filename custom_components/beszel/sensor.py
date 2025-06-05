"""Sensor platform for Beszel."""
import logging
from typing import Any, Dict, Optional, List

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import (
    PERCENTAGE,
    UnitOfInformation,
    UnitOfDataRate,
    UnitOfTemperature,
    UnitOfTime,
    UnitOfPower,
)


from .const import (
    DOMAIN,
    ATTR_KERNEL_VERSION, ATTR_CPU_PERCENT_INFO, ATTR_THREADS, ATTR_CORES,
    ATTR_CPU_MODEL, ATTR_UPTIME, ATTR_MEM_PERCENT_INFO, ATTR_DISK_PERCENT_INFO,
    ATTR_BANDWIDTH_MB, ATTR_AGENT_VERSION, ATTR_PODMAN, ATTR_GPU_PERCENT_INFO,
    ATTR_DASHBOARD_TEMP, ATTR_OS,
    ATTR_CPU_PERCENT, ATTR_CPU_MAX_PERCENT, ATTR_MEM_TOTAL_GB, ATTR_MEM_USED_GB,
    ATTR_MEM_PERCENT, ATTR_MEM_BUFF_CACHE_GB, ATTR_MEM_ZFS_ARC_GB, ATTR_SWAP_TOTAL_GB,
    ATTR_SWAP_USED_GB, ATTR_SWAP_PERCENT, ATTR_DISK_TOTAL_GB, ATTR_DISK_USED_GB, ATTR_DISK_PERCENT,
    ATTR_DISK_READ_PS_MB, ATTR_DISK_WRITE_PS_MB, ATTR_DISK_READ_MAX_PS_MB,
    ATTR_DISK_WRITE_MAX_PS_MB, ATTR_NET_SENT_PS_MB, ATTR_NET_RECV_PS_MB,
    ATTR_NET_SENT_MAX_PS_MB, ATTR_NET_RECV_MAX_PS_MB, ATTR_TEMPERATURES,
    ATTR_EXTRA_FS, ATTR_GPU_DATA,
    ATTR_GPU_NAME, ATTR_GPU_MEM_USED_MB, ATTR_GPU_MEM_TOTAL_MB, ATTR_GPU_USAGE_PERCENT,
    ATTR_GPU_POWER_W,
    ATTR_FS_DISK_TOTAL_GB, ATTR_FS_DISK_USED_GB, ATTR_FS_DISK_PERCENT, ATTR_FS_DISK_READ_PS_MB,
    ATTR_FS_DISK_WRITE_PS_MB, ATTR_FS_MAX_DISK_READ_PS_MB, ATTR_FS_MAX_DISK_WRITE_PS_MB,
)
from .coordinator import BeszelDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Define sensors based on Beszel API structure
# (key_in_api, name_suffix, unit, device_class, state_class, icon, data_source_key, enabled_by_default)
SENSOR_TYPES_INFO = [
    (ATTR_UPTIME, "Uptime", UnitOfTime.SECONDS, SensorDeviceClass.DURATION, SensorStateClass.TOTAL_INCREASING, "mdi:timer-sand", "info", True),
    (ATTR_AGENT_VERSION, "Agent Version", None, None, None, "mdi:information-outline", "agent_version_from_record", False),
    (ATTR_OS, "Operating System", None, None, None, "mdi:linux", "info", False), # Icon can be dynamic
    (ATTR_KERNEL_VERSION, "Kernel Version", None, None, None, "mdi:chip", "info", False),
    (ATTR_CPU_MODEL, "CPU Model", None, None, None, "mdi:cpu-64-bit", "info", False),
    (ATTR_CORES, "CPU Cores", None, None, None, "mdi:cpu-64-bit", "info", False),
    (ATTR_THREADS, "CPU Threads", None, None, None, "mdi:cpu-64-bit", "info", False),
    (ATTR_CPU_PERCENT_INFO, "Info CPU Usage", PERCENTAGE, SensorDeviceClass.POWER_FACTOR, SensorStateClass.MEASUREMENT, "mdi:gauge", "info", False),
    (ATTR_MEM_PERCENT_INFO, "Info Memory Usage", PERCENTAGE, SensorDeviceClass.POWER_FACTOR, SensorStateClass.MEASUREMENT, "mdi:gauge", "info", False),
    (ATTR_DISK_PERCENT_INFO, "Info Disk Usage", PERCENTAGE, SensorDeviceClass.POWER_FACTOR, SensorStateClass.MEASUREMENT, "mdi:gauge", "info", False),
    (ATTR_BANDWIDTH_MB, "Info Max Network Rate", UnitOfDataRate.MEGABYTES_PER_SECOND, SensorDeviceClass.DATA_RATE, SensorStateClass.MEASUREMENT, "mdi:gauge", "info", False),
    (ATTR_GPU_PERCENT_INFO, "Info GPU Usage", PERCENTAGE, SensorDeviceClass.POWER_FACTOR, SensorStateClass.MEASUREMENT, "mdi:gauge", "info", False),
    (ATTR_DASHBOARD_TEMP, "Info Dashboard Temperature", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, "mdi:thermometer", "info", False),
    (ATTR_PODMAN, "Podman Enabled", None, SensorDeviceClass.ENUM, None, "mdi:docker", "info", False, ["False", "True"]),
]

SENSOR_TYPES_STATS = [
    (ATTR_CPU_PERCENT, "CPU Usage", PERCENTAGE, SensorDeviceClass.POWER_FACTOR, SensorStateClass.MEASUREMENT, "mdi:cpu-64-bit", "stats", True),
    (ATTR_CPU_MAX_PERCENT, "CPU Max Usage", PERCENTAGE, SensorDeviceClass.POWER_FACTOR, SensorStateClass.MEASUREMENT, "mdi:cpu-64-bit", "stats", False),
    (ATTR_MEM_PERCENT, "Memory Usage", PERCENTAGE, SensorDeviceClass.POWER_FACTOR, SensorStateClass.MEASUREMENT, "mdi:memory", "stats", True),
    (ATTR_MEM_USED_GB, "Memory Used", UnitOfInformation.GIGABYTES, SensorDeviceClass.DATA_SIZE, SensorStateClass.MEASUREMENT, "mdi:memory", "stats", True),
    (ATTR_MEM_TOTAL_GB, "Memory Total", UnitOfInformation.GIGABYTES, SensorDeviceClass.DATA_SIZE, SensorStateClass.MEASUREMENT, "mdi:memory", "stats", False),
    (ATTR_MEM_BUFF_CACHE_GB, "Memory Buffer/Cache", UnitOfInformation.GIGABYTES, SensorDeviceClass.DATA_SIZE, SensorStateClass.MEASUREMENT, "mdi:memory", "stats", False),
    (ATTR_MEM_ZFS_ARC_GB, "Memory ZFS ARC", UnitOfInformation.GIGABYTES, SensorDeviceClass.DATA_SIZE, SensorStateClass.MEASUREMENT, "mdi:memory", "stats", False),
    (ATTR_SWAP_PERCENT, "Swap Usage", PERCENTAGE, SensorDeviceClass.POWER_FACTOR, SensorStateClass.MEASUREMENT, "mdi:harddisk", "stats", True, None, lambda data: round((data.get(ATTR_SWAP_USED_GB, 0) / data.get(ATTR_SWAP_TOTAL_GB, 1)) * 100, 2) if data.get(ATTR_SWAP_TOTAL_GB) else 0),
    (ATTR_SWAP_USED_GB, "Swap Used", UnitOfInformation.GIGABYTES, SensorDeviceClass.DATA_SIZE, SensorStateClass.MEASUREMENT, "mdi:harddisk", "stats", False),
    (ATTR_SWAP_TOTAL_GB, "Swap Total", UnitOfInformation.GIGABYTES, SensorDeviceClass.DATA_SIZE, SensorStateClass.MEASUREMENT, "mdi:harddisk", "stats", False),
    (ATTR_DISK_PERCENT, "Disk Usage", PERCENTAGE, SensorDeviceClass.POWER_FACTOR, SensorStateClass.MEASUREMENT, "mdi:harddisk", "stats", True),
    (ATTR_DISK_USED_GB, "Disk Used", UnitOfInformation.GIGABYTES, SensorDeviceClass.DATA_SIZE, SensorStateClass.MEASUREMENT, "mdi:harddisk", "stats", True),
    (ATTR_DISK_TOTAL_GB, "Disk Total", UnitOfInformation.GIGABYTES, SensorDeviceClass.DATA_SIZE, SensorStateClass.MEASUREMENT, "mdi:harddisk", "stats", False),
    (ATTR_DISK_READ_PS_MB, "Disk Read Speed", UnitOfDataRate.MEGABYTES_PER_SECOND, SensorDeviceClass.DATA_RATE, SensorStateClass.MEASUREMENT, "mdi:arrow-down-bold-circle-outline", "stats", True),
    (ATTR_DISK_WRITE_PS_MB, "Disk Write Speed", UnitOfDataRate.MEGABYTES_PER_SECOND, SensorDeviceClass.DATA_RATE, SensorStateClass.MEASUREMENT, "mdi:arrow-up-bold-circle-outline", "stats", True),
    (ATTR_DISK_READ_MAX_PS_MB, "Disk Read Max Speed", UnitOfDataRate.MEGABYTES_PER_SECOND, SensorDeviceClass.DATA_RATE, SensorStateClass.MEASUREMENT, "mdi:arrow-down-bold-circle", "stats", False),
    (ATTR_DISK_WRITE_MAX_PS_MB, "Disk Write Max Speed", UnitOfDataRate.MEGABYTES_PER_SECOND, SensorDeviceClass.DATA_RATE, SensorStateClass.MEASUREMENT, "mdi:arrow-up-bold-circle", "stats", False),
    (ATTR_NET_SENT_PS_MB, "Network Sent Speed", UnitOfDataRate.MEGABYTES_PER_SECOND, SensorDeviceClass.DATA_RATE, SensorStateClass.MEASUREMENT, "mdi:arrow-up-network", "stats", True),
    (ATTR_NET_RECV_PS_MB, "Network Received Speed", UnitOfDataRate.MEGABYTES_PER_SECOND, SensorDeviceClass.DATA_RATE, SensorStateClass.MEASUREMENT, "mdi:arrow-down-network", "stats", True),
    (ATTR_NET_SENT_MAX_PS_MB, "Network Sent Max Speed", UnitOfDataRate.MEGABYTES_PER_SECOND, SensorDeviceClass.DATA_RATE, SensorStateClass.MEASUREMENT, "mdi:arrow-up-network-outline", "stats", False),
    (ATTR_NET_RECV_MAX_PS_MB, "Network Received Max Speed", UnitOfDataRate.MEGABYTES_PER_SECOND, SensorDeviceClass.DATA_RATE, SensorStateClass.MEASUREMENT, "mdi:arrow-down-network-outline", "stats", False),
    ("status", "Status", None, SensorDeviceClass.ENUM, None, "mdi:server-network", "status", True, ["up", "down", "paused", "pending", "unknown"]),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Beszel sensor entities based on a config entry."""
    coordinator: BeszelDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Initial fetch to discover systems
    await coordinator.async_config_entry_first_refresh()

    entities_to_add: List[SensorEntity] = []

    if coordinator.data: # coordinator.data is Dict[system_id, system_data_dict]
        for system_id, system_data in coordinator.data.items():
            if "error" in system_data:
                _LOGGER.warning("Skipping system %s due to previous error: %s", system_id, system_data["error"])
                continue

            system_name = system_data.get("name", system_id)
            _LOGGER.debug("Setting up sensors for system: %s (ID: %s)", system_name, system_id)

            # Add static info sensors
            for api_key, name_suffix, unit, dev_class, state_class, icon, data_key, enabled, *rest in SENSOR_TYPES_INFO:
                options = rest[0] if rest else None
                entities_to_add.append(
                    BeszelSensor(
                        coordinator,
                        system_id,
                        system_name,
                        api_key,
                        name_suffix,
                        unit,
                        dev_class,
                        state_class,
                        icon,
                        data_key, # e.g., "device_info_summary" or "agent_version_from_record"
                        enabled,
                        options=options,
                    )
                )
            
            # Add dynamic stats sensors
            for api_key, name_suffix, unit, dev_class, state_class, icon, data_key, enabled, *rest in SENSOR_TYPES_STATS:
                options = rest[0] if rest and len(rest) > 0 else None
                value_func = rest[1] if rest and len(rest) > 1 else None
                entities_to_add.append(
                    BeszelSensor(
                        coordinator,
                        system_id,
                        system_name,
                        api_key,
                        name_suffix,
                        unit,
                        dev_class,
                        state_class,
                        icon,
                        data_key, # e.g., "stats" or "status"
                        enabled,
                        options=options,
                        value_func=value_func,
                    )
                )

            # Add temperature sensors (if any)
            temps = system_data.get("stats", {}).get(ATTR_TEMPERATURES, {})
            for temp_sensor_name in temps:
                entities_to_add.append(
                    BeszelTemperatureSensor(
                        coordinator,
                        system_id,
                        system_name,
                        temp_sensor_name,
                    )
                )
            
            # Add Extra Filesystem sensors
            extra_fs_data = system_data.get("stats", {}).get(ATTR_EXTRA_FS, {})
            for fs_name, fs_stats in extra_fs_data.items():
                entities_to_add.extend(
                    _create_extra_fs_sensors(coordinator, system_id, system_name, fs_name)
                )

            # Add GPU sensors
            gpu_data_map = system_data.get("stats", {}).get(ATTR_GPU_DATA, {})
            for gpu_id, gpu_stats in gpu_data_map.items(): # gpu_id might be a numeric string or a descriptive name
                gpu_name_from_stats = gpu_stats.get(ATTR_GPU_NAME, gpu_id)
                entities_to_add.extend(
                    _create_gpu_sensors(coordinator, system_id, system_name, gpu_id, gpu_name_from_stats)
                )


    if entities_to_add:
        async_add_entities(entities_to_add)
    else:
        _LOGGER.info("No systems or sensors to add for Beszel integration.")


def _create_extra_fs_sensors(coordinator, system_id, system_name, fs_name):
    """Helper to create sensors for an extra filesystem."""
    sensors = []
    fs_sensor_types = [
        (ATTR_FS_DISK_PERCENT, f"{fs_name} Usage", PERCENTAGE, SensorDeviceClass.POWER_FACTOR, SensorStateClass.MEASUREMENT, "mdi:harddisk", True, lambda data: round((data.get(ATTR_FS_DISK_USED_GB,0) / data.get(ATTR_FS_DISK_TOTAL_GB,1)) * 100, 2) if data.get(ATTR_FS_DISK_TOTAL_GB) else 0),
        (ATTR_FS_DISK_USED_GB, f"{fs_name} Used", UnitOfInformation.GIGABYTES, SensorDeviceClass.DATA_SIZE, SensorStateClass.MEASUREMENT, "mdi:harddisk", True),
        (ATTR_FS_DISK_TOTAL_GB, f"{fs_name} Total", UnitOfInformation.GIGABYTES, SensorDeviceClass.DATA_SIZE, SensorStateClass.MEASUREMENT, "mdi:harddisk", False),
        (ATTR_FS_DISK_READ_PS_MB, f"{fs_name} Read Speed", UnitOfDataRate.MEGABYTES_PER_SECOND, SensorDeviceClass.DATA_RATE, SensorStateClass.MEASUREMENT, "mdi:arrow-down-bold-circle-outline", True),
        (ATTR_FS_DISK_WRITE_PS_MB, f"{fs_name} Write Speed", UnitOfDataRate.MEGABYTES_PER_SECOND, SensorDeviceClass.DATA_RATE, SensorStateClass.MEASUREMENT, "mdi:arrow-up-bold-circle-outline", True),
        (ATTR_FS_MAX_DISK_READ_PS_MB, f"{fs_name} Max Read Speed", UnitOfDataRate.MEGABYTES_PER_SECOND, SensorDeviceClass.DATA_RATE, SensorStateClass.MEASUREMENT, "mdi:arrow-down-bold-circle", False),
        (ATTR_FS_MAX_DISK_WRITE_PS_MB, f"{fs_name} Max Write Speed", UnitOfDataRate.MEGABYTES_PER_SECOND, SensorDeviceClass.DATA_RATE, SensorStateClass.MEASUREMENT, "mdi:arrow-up-bold-circle", False),
    ]
    for api_key_suffix, name_suffix_full, unit, dev_class, state_class, icon, enabled, *rest in fs_sensor_types:
        value_func = rest[0] if rest else None
        sensors.append(
            BeszelNestedSensor(
                coordinator, system_id, system_name, ATTR_EXTRA_FS, fs_name, api_key_suffix,
                name_suffix_full, unit, dev_class, state_class, icon, enabled, value_func=value_func
            )
        )
    return sensors

def _create_gpu_sensors(coordinator, system_id, system_name, gpu_id_key, gpu_name_display):
    """Helper to create sensors for a GPU."""
    sensors = []
    gpu_sensor_types = [
        (ATTR_GPU_USAGE_PERCENT, f"{gpu_name_display} Usage", PERCENTAGE, SensorDeviceClass.POWER_FACTOR, SensorStateClass.MEASUREMENT, "mdi:expansion-card", True),
        (ATTR_GPU_MEM_USED_MB, f"{gpu_name_display} Memory Used", UnitOfInformation.MEGABYTES, SensorDeviceClass.DATA_SIZE, SensorStateClass.MEASUREMENT, "mdi:memory", True),
        (ATTR_GPU_MEM_TOTAL_MB, f"{gpu_name_display} Memory Total", UnitOfInformation.MEGABYTES, SensorDeviceClass.DATA_SIZE, SensorStateClass.MEASUREMENT, "mdi:memory", False),
        (ATTR_GPU_POWER_W, f"{gpu_name_display} Power Draw", UnitOfPower.WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, "mdi:lightning-bolt", True),
        # GPU Temperature is handled by BeszelTemperatureSensor if present in main ATTR_TEMPERATURES
        # If GPU temps are only inside ATTR_GPU_DATA, a specific sensor would be needed here.
        # Assuming Beszel puts GPU temps in the main ATTR_TEMPERATURES map for now.
    ]
    for api_key_suffix, name_suffix_full, unit, dev_class, state_class, icon, enabled in gpu_sensor_types:
        sensors.append(
            BeszelNestedSensor(
                coordinator, system_id, system_name, ATTR_GPU_DATA, gpu_id_key, api_key_suffix,
                name_suffix_full, unit, dev_class, state_class, icon, enabled
            )
        )
    return sensors


class BeszelSensor(CoordinatorEntity[BeszelDataUpdateCoordinator], SensorEntity):
    """Representation of a Beszel Sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: BeszelDataUpdateCoordinator,
        system_id: str,
        system_name: str,
        api_key: str,
        name_suffix: str,
        unit: Optional[str],
        device_class: Optional[SensorDeviceClass],
        state_class: Optional[SensorStateClass],
        icon: Optional[str],
        data_source_key: str, # "stats", "info", "device_info_summary", "status", "agent_version_from_record"
        enabled_by_default: bool = True,
        options: Optional[List[str]] = None, # For ENUM device_class
        value_func = None, # Optional function to calculate value
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._system_id = system_id
        self._system_name = system_name
        self._api_key = api_key
        self._data_source_key = data_source_key # Which part of system_data to use
        self._value_func = value_func

        self._attr_unique_id = f"{DOMAIN}_{system_id}_{api_key}"
        self._attr_name = f"{name_suffix}" # HA will prefix with device name
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._icon_definition = icon # Store for dynamic icon property
        self._attr_entity_registry_enabled_default = enabled_by_default
        if device_class == SensorDeviceClass.ENUM and options:
            self._attr_options = options


        # Device info for grouping sensors
        self._attr_device_info = {
            "identifiers": {(DOMAIN, self._system_id)},
            "name": self._system_name,
            "manufacturer": "Beszel",
            "model": "Monitored System", # Could be enhanced with OS type later
        }
        # Try to get agent version and OS from initial data for device info
        initial_system_data = coordinator.data.get(self._system_id, {})
        if initial_system_data and not initial_system_data.get("error"):
            agent_version = initial_system_data.get("agent_version_from_record", "Unknown")
            os_type_raw = initial_system_data.get("info", {}).get(ATTR_OS)
            os_name = self._map_os_type_to_name(os_type_raw)
            self._attr_device_info["sw_version"] = agent_version
            if os_name != "Unknown":
                 self._attr_device_info["model"] = os_name # Use OS as model

    def _map_os_type_to_name(self, os_type_raw: Any) -> str:
        """Map OS type code to a human-readable name."""
        # Based on beszel/site/src/lib/enums.ts
        if os_type_raw == 0: return "Linux"
        if os_type_raw == 1: return "Darwin (macOS)"
        if os_type_raw == 2: return "Windows"
        if os_type_raw == 3: return "FreeBSD"
        return "Unknown"

    def _map_os_type_to_icon(self, os_type_raw: Any) -> str | None:
        """Map OS type code to an icon string."""
        if os_type_raw == 0: return "mdi:linux"
        if os_type_raw == 1: return "mdi:apple"
        if os_type_raw == 2: return "mdi:microsoft-windows"
        if os_type_raw == 3: return "mdi:freebsd"
        return None # Fallback to default icon

    @property
    def icon(self) -> str | None:
        """Return the icon of the sensor."""
        if self._api_key == ATTR_OS and self._data_source_key == "info":
            os_type_raw = self.system_data.get("info", {}).get(ATTR_OS)
            mapped_icon = self._map_os_type_to_icon(os_type_raw)
            if mapped_icon:
                return mapped_icon
        return self._icon_definition

    @property
    def system_data(self) -> Dict[str, Any]:
        """Shortcut to get the data for this sensor's system."""
        return self.coordinator.data.get(self._system_id, {})

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        data_dict = self.system_data.get(self._data_source_key, {})

        if self._data_source_key == "status": # Special case for top-level status
            return self.system_data.get("status", "unknown")
        if self._data_source_key == "agent_version_from_record":
            return self.system_data.get("agent_version_from_record", "unknown")

        if not isinstance(data_dict, dict): # Ensure it's a dict before .get()
            if self._api_key == self._data_source_key: # e.g. for status
                 return data_dict # return the value directly
            return None

        if self._value_func:
            return self._value_func(data_dict)

        value = data_dict.get(self._api_key)

        if self._api_key == ATTR_OS and self._data_source_key == "info":
            return self._map_os_type_to_name(value)
        if self._api_key == ATTR_PODMAN and self._data_source_key == "info":
            return "True" if value else "False"

        if value is not None and self._attr_native_unit_of_measurement == PERCENTAGE:
            try:
                return round(float(value), 2)
            except (ValueError, TypeError):
                return value # Or None if preferred for non-numeric
        return value

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        # Update device info if agent version or OS changes
        current_data = self.coordinator.data.get(self._system_id, {})
        if current_data and not current_data.get("error"):
            new_agent_version = current_data.get("agent_version_from_record")
            new_os_raw = current_data.get("info", {}).get(ATTR_OS)
            new_os_name = self._map_os_type_to_name(new_os_raw)

            updated_device_info = False
            if new_agent_version and self._attr_device_info.get("sw_version") != new_agent_version:
                self._attr_device_info["sw_version"] = new_agent_version
                updated_device_info = True
            if new_os_name != "Unknown" and self._attr_device_info.get("model") != new_os_name:
                self._attr_device_info["model"] = new_os_name
                updated_device_info = True
            
            # If device info changed, we might need to inform HA, though it's usually static after setup.
            # For now, just updating the internal attribute.

        super()._handle_coordinator_update()


class BeszelTemperatureSensor(BeszelSensor):
    """Representation of a Beszel Temperature Sensor."""

    def __init__(
        self,
        coordinator: BeszelDataUpdateCoordinator,
        system_id: str,
        system_name: str,
        temp_sensor_key: str, # e.g., "coretemp_core0_input"
    ) -> None:
        """Initialize the temperature sensor."""
        super().__init__(
            coordinator,
            system_id,
            system_name,
            temp_sensor_key, # This will be the unique part of the ID
            f"Temperature {temp_sensor_key.replace('_', ' ').title()}", # Name suffix
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
            "mdi:thermometer",
            "stats", # Temperature data is within the "stats" dict
            True,
        )
        self._temp_sensor_key = temp_sensor_key

    @property
    def native_value(self) -> Optional[float]:
        """Return the state of the sensor."""
        temps_dict = self.system_data.get("stats", {}).get(ATTR_TEMPERATURES, {})
        value = temps_dict.get(self._temp_sensor_key)
        if value is not None:
            try:
                return round(float(value), 1)
            except (ValueError, TypeError):
                return None
        return None

class BeszelNestedSensor(BeszelSensor):
    """Sensor for values nested within a sub-dictionary (e.g., extra_fs, gpu_data)."""

    def __init__(
        self,
        coordinator: BeszelDataUpdateCoordinator,
        system_id: str,
        system_name: str,
        parent_key: str, # e.g., ATTR_EXTRA_FS or ATTR_GPU_DATA
        item_key: str,   # e.g., specific filesystem name or GPU ID/name
        api_value_key: str, # e.g., ATTR_FS_DISK_USED_GB or ATTR_GPU_USAGE_PERCENT
        name_full: str, # Full name for the sensor, e.g., "sda1 Disk Used"
        unit: Optional[str],
        device_class: Optional[SensorDeviceClass],
        state_class: Optional[SensorStateClass],
        icon: Optional[str],
        enabled_by_default: bool = True,
        value_func = None,
    ) -> None:
        """Initialize the nested sensor."""
        # Use a combination for unique ID
        unique_part = f"{parent_key}_{item_key}_{api_value_key}" # This becomes the api_key for the parent BeszelSensor
        super().__init__(
            coordinator, system_id, system_name,
            unique_part, # This unique_part is used to construct _attr_unique_id in the parent.
            name_full,   # name_suffix for BeszelSensor constructor (becomes entity name)
            unit, device_class, state_class, icon,
            "stats", # Data source is still 'stats' at the top level
            enabled_by_default,
            value_func=value_func,
        )
        self._parent_key = parent_key
        self._item_key = item_key
        self._api_value_key = api_value_key # The actual key for the value

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        parent_dict = self.system_data.get("stats", {}).get(self._parent_key, {})
        item_dict = parent_dict.get(self._item_key, {})

        if self._value_func: # If a custom value function is provided
             return self._value_func(item_dict)

        value = item_dict.get(self._api_value_key)

        if value is not None and self._attr_native_unit_of_measurement == PERCENTAGE:
            try:
                return round(float(value), 2)
            except (ValueError, TypeError):
                return value
        return value
