"""Sensor platform for Beszel."""

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfDataRate,
    UnitOfInformation,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_AGENT_VERSION,
    ATTR_BATTERY,
    ATTR_CORES,
    ATTR_CPU_MODEL,
    ATTR_CPU_PERCENT,
    ATTR_DISK_IO_STATS,
    ATTR_DISK_PERCENT,
    ATTR_DISK_READ_PS_MB,
    ATTR_DISK_TOTAL_GB,
    ATTR_DISK_USED_GB,
    ATTR_DISK_WRITE_PS_MB,
    ATTR_EXTRA_FS,
    ATTR_FS_DISK_IO_STATS,
    ATTR_FS_DISK_PERCENT,
    ATTR_FS_DISK_READ_PS_MB,
    ATTR_FS_DISK_TOTAL_GB,
    ATTR_FS_DISK_USED_GB,
    ATTR_FS_DISK_WRITE_PS_MB,
    ATTR_GPU_DATA,
    ATTR_GPU_MEM_TOTAL_MB,
    ATTR_GPU_MEM_USED_MB,
    ATTR_GPU_NAME,
    ATTR_GPU_POWER_PACKAGE_W,
    ATTR_GPU_POWER_W,
    ATTR_GPU_USAGE_PERCENT,
    ATTR_KERNEL_VERSION,
    ATTR_MEM_BUFF_CACHE_GB,
    ATTR_MEM_PERCENT,
    ATTR_MEM_TOTAL_GB,
    ATTR_MEM_USED_GB,
    ATTR_MEM_ZFS_ARC_GB,
    ATTR_NET_RECV_PS_MB,
    ATTR_NET_SENT_PS_MB,
    ATTR_OS,
    ATTR_SWAP_PERCENT,
    ATTR_SWAP_TOTAL_GB,
    ATTR_SWAP_USED_GB,
    ATTR_TEMPERATURES,
    ATTR_THREADS,
    ATTR_UPTIME,
    DOMAIN,
)


def _array_value(data, key, index, precision=2):
    """Return a rounded value from a Beszel array metric."""
    values = data.get(key)
    if not isinstance(values, (list, tuple)) or len(values) <= index:
        return None
    value = values[index]
    if value is None:
        return None
    try:
        return round(float(value), precision)
    except (TypeError, ValueError):
        return None


def _battery_percent(data):
    """Return the Beszel battery percentage."""
    if not _has_battery(data):
        return None
    value = _array_value(data, ATTR_BATTERY, 0, precision=0)
    return int(value) if value is not None else None


def _battery_state(data):
    """Return the Beszel battery charge state."""
    if not _has_battery(data):
        return None
    states = {
        0: "Unknown",
        1: "Empty",
        2: "Full",
        3: "Charging",
        4: "Discharging",
        5: "Idle",
    }
    value = _array_value(data, ATTR_BATTERY, 1, precision=0)
    return states.get(int(value), "Unknown") if value is not None else None


def _has_battery(data):
    """Return whether Beszel reports a battery."""
    values = data.get(ATTR_BATTERY)
    return (
        isinstance(values, (list, tuple))
        and len(values) >= 2
        and list(values[:2]) != [0, 0]
    )


def _used_percent(data, total_key, used_key):
    """Return a percentage only when both source values are reported."""
    total = data.get(total_key)
    used = data.get(used_key)
    if total is None or used is None:
        return None
    try:
        return round((float(used) / float(total)) * 100, 2) if float(total) else 0
    except (TypeError, ValueError):
        return None


SENSOR_TYPES_INFO = [
    (
        ATTR_AGENT_VERSION,
        "Agent Version",
        None,
        None,
        None,
        "mdi:information-outline",
        "info",
        True,
    ),
    (ATTR_CORES, "CPU Cores", None, None, None, "mdi:cpu-64-bit", "info", True),
    (ATTR_CPU_MODEL, "CPU Model", None, None, None, "mdi:cpu-64-bit", "info", True),
    (ATTR_KERNEL_VERSION, "Kernel Version", None, None, None, "mdi:chip", "info", True),
    (ATTR_OS, "Operating System", None, None, None, "mdi:linux", "info", True),
    (ATTR_THREADS, "CPU Threads", None, None, None, "mdi:cpu-64-bit", "info", True),
    (
        ATTR_UPTIME,
        "Uptime",
        UnitOfTime.SECONDS,
        SensorDeviceClass.DURATION,
        SensorStateClass.MEASUREMENT,
        "mdi:timer-sand",
        "info",
        True,
    ),
]

SENSOR_TYPES_STATS = [
    (
        "battery_percent",
        "Battery Level",
        PERCENTAGE,
        SensorDeviceClass.BATTERY,
        SensorStateClass.MEASUREMENT,
        "mdi:battery",
        "stats",
        True,
        None,
        _battery_percent,
    ),
    (
        "battery_state",
        "Battery State",
        None,
        SensorDeviceClass.ENUM,
        None,
        "mdi:battery-charging",
        "stats",
        True,
        ["Charging", "Discharging", "Empty", "Full", "Idle", "Unknown"],
        _battery_state,
    ),
    (
        ATTR_CPU_PERCENT,
        "CPU Usage",
        PERCENTAGE,
        None,
        SensorStateClass.MEASUREMENT,
        "mdi:cpu-64-bit",
        "stats",
        True,
    ),
    (
        ATTR_DISK_PERCENT,
        "Disk Usage",
        PERCENTAGE,
        None,
        SensorStateClass.MEASUREMENT,
        "mdi:harddisk",
        "stats",
        True,
    ),
    (
        ATTR_DISK_READ_PS_MB,
        "Disk Read Speed",
        UnitOfDataRate.MEGABYTES_PER_SECOND,
        SensorDeviceClass.DATA_RATE,
        SensorStateClass.MEASUREMENT,
        "mdi:arrow-down-bold-circle-outline",
        "stats",
        True,
    ),
    (
        ATTR_DISK_TOTAL_GB,
        "Disk Total",
        UnitOfInformation.GIGABYTES,
        SensorDeviceClass.DATA_SIZE,
        SensorStateClass.MEASUREMENT,
        "mdi:harddisk",
        "stats",
        True,
    ),
    (
        ATTR_DISK_USED_GB,
        "Disk Used",
        UnitOfInformation.GIGABYTES,
        SensorDeviceClass.DATA_SIZE,
        SensorStateClass.MEASUREMENT,
        "mdi:harddisk",
        "stats",
        True,
    ),
    (
        ATTR_DISK_WRITE_PS_MB,
        "Disk Write Speed",
        UnitOfDataRate.MEGABYTES_PER_SECOND,
        SensorDeviceClass.DATA_RATE,
        SensorStateClass.MEASUREMENT,
        "mdi:arrow-up-bold-circle-outline",
        "stats",
        True,
    ),
    (
        "disk_io_utilisation_percent",
        "Disk I/O Utilisation",
        PERCENTAGE,
        None,
        SensorStateClass.MEASUREMENT,
        "mdi:harddisk",
        "stats",
        True,
        None,
        lambda data: _array_value(data, ATTR_DISK_IO_STATS, 2),
    ),
    (
        "disk_read_await_ms",
        "Disk Read Await",
        UnitOfTime.MILLISECONDS,
        SensorDeviceClass.DURATION,
        SensorStateClass.MEASUREMENT,
        "mdi:timer-outline",
        "stats",
        True,
        None,
        lambda data: _array_value(data, ATTR_DISK_IO_STATS, 3),
    ),
    (
        "disk_read_time_percent",
        "Disk Read Time",
        PERCENTAGE,
        None,
        SensorStateClass.MEASUREMENT,
        "mdi:harddisk",
        "stats",
        True,
        None,
        lambda data: _array_value(data, ATTR_DISK_IO_STATS, 0),
    ),
    (
        "disk_weighted_io_percent",
        "Disk Weighted I/O",
        PERCENTAGE,
        None,
        SensorStateClass.MEASUREMENT,
        "mdi:harddisk",
        "stats",
        True,
        None,
        lambda data: _array_value(data, ATTR_DISK_IO_STATS, 5),
    ),
    (
        "disk_write_await_ms",
        "Disk Write Await",
        UnitOfTime.MILLISECONDS,
        SensorDeviceClass.DURATION,
        SensorStateClass.MEASUREMENT,
        "mdi:timer-outline",
        "stats",
        True,
        None,
        lambda data: _array_value(data, ATTR_DISK_IO_STATS, 4),
    ),
    (
        "disk_write_time_percent",
        "Disk Write Time",
        PERCENTAGE,
        None,
        SensorStateClass.MEASUREMENT,
        "mdi:harddisk",
        "stats",
        True,
        None,
        lambda data: _array_value(data, ATTR_DISK_IO_STATS, 1),
    ),
    (
        ATTR_MEM_BUFF_CACHE_GB,
        "Memory Buffer/Cache",
        UnitOfInformation.GIGABYTES,
        SensorDeviceClass.DATA_SIZE,
        SensorStateClass.MEASUREMENT,
        "mdi:memory",
        "stats",
        True,
    ),
    (
        ATTR_MEM_PERCENT,
        "Memory Usage",
        PERCENTAGE,
        None,
        SensorStateClass.MEASUREMENT,
        "mdi:memory",
        "stats",
        True,
    ),
    (
        ATTR_MEM_TOTAL_GB,
        "Memory Total",
        UnitOfInformation.GIGABYTES,
        SensorDeviceClass.DATA_SIZE,
        SensorStateClass.MEASUREMENT,
        "mdi:memory",
        "stats",
        True,
    ),
    (
        ATTR_MEM_USED_GB,
        "Memory Used",
        UnitOfInformation.GIGABYTES,
        SensorDeviceClass.DATA_SIZE,
        SensorStateClass.MEASUREMENT,
        "mdi:memory",
        "stats",
        True,
    ),
    (
        ATTR_MEM_ZFS_ARC_GB,
        "Memory ZFS ARC",
        UnitOfInformation.GIGABYTES,
        SensorDeviceClass.DATA_SIZE,
        SensorStateClass.MEASUREMENT,
        "mdi:memory",
        "stats",
        True,
    ),
    (
        ATTR_NET_RECV_PS_MB,
        "Network Received Speed",
        UnitOfDataRate.MEGABYTES_PER_SECOND,
        SensorDeviceClass.DATA_RATE,
        SensorStateClass.MEASUREMENT,
        "mdi:download-network-outline",
        "stats",
        True,
    ),
    (
        ATTR_NET_SENT_PS_MB,
        "Network Sent Speed",
        UnitOfDataRate.MEGABYTES_PER_SECOND,
        SensorDeviceClass.DATA_RATE,
        SensorStateClass.MEASUREMENT,
        "mdi:upload-network-outline",
        "stats",
        True,
    ),
    (
        ATTR_SWAP_PERCENT,
        "Swap Usage",
        PERCENTAGE,
        None,
        SensorStateClass.MEASUREMENT,
        "mdi:harddisk",
        "stats",
        True,
        None,
        lambda data: _used_percent(data, ATTR_SWAP_TOTAL_GB, ATTR_SWAP_USED_GB),
    ),
    (
        ATTR_SWAP_TOTAL_GB,
        "Swap Total",
        UnitOfInformation.GIGABYTES,
        SensorDeviceClass.DATA_SIZE,
        SensorStateClass.MEASUREMENT,
        "mdi:harddisk",
        "stats",
        True,
    ),
    (
        ATTR_SWAP_USED_GB,
        "Swap Used",
        UnitOfInformation.GIGABYTES,
        SensorDeviceClass.DATA_SIZE,
        SensorStateClass.MEASUREMENT,
        "mdi:harddisk",
        "stats",
        True,
    ),
    (
        "status",
        "Status",
        None,
        SensorDeviceClass.ENUM,
        None,
        "mdi:server-network",
        "status",
        True,
        ["Down", "Paused", "Pending", "Unknown", "Up"],
    ),
]


def _create_extra_fs_sensors(coordinator, system_id, system_name, fs_name):
    """Helper to create sensors for an extra filesystem."""
    fs_sensor_types = [
        (
            ATTR_FS_DISK_PERCENT,
            f"{fs_name} Usage",
            PERCENTAGE,
            None,
            SensorStateClass.MEASUREMENT,
            "mdi:harddisk",
            True,
            lambda data: _used_percent(
                data, ATTR_FS_DISK_TOTAL_GB, ATTR_FS_DISK_USED_GB
            ),
        ),
        (
            ATTR_FS_DISK_READ_PS_MB,
            f"{fs_name} Read Speed",
            UnitOfDataRate.MEGABYTES_PER_SECOND,
            SensorDeviceClass.DATA_RATE,
            SensorStateClass.MEASUREMENT,
            "mdi:arrow-down-bold-circle-outline",
            True,
        ),
        (
            ATTR_FS_DISK_TOTAL_GB,
            f"{fs_name} Total",
            UnitOfInformation.GIGABYTES,
            SensorDeviceClass.DATA_SIZE,
            SensorStateClass.MEASUREMENT,
            "mdi:harddisk",
            True,
        ),
        (
            ATTR_FS_DISK_USED_GB,
            f"{fs_name} Used",
            UnitOfInformation.GIGABYTES,
            SensorDeviceClass.DATA_SIZE,
            SensorStateClass.MEASUREMENT,
            "mdi:harddisk",
            True,
        ),
        (
            ATTR_FS_DISK_WRITE_PS_MB,
            f"{fs_name} Write Speed",
            UnitOfDataRate.MEGABYTES_PER_SECOND,
            SensorDeviceClass.DATA_RATE,
            SensorStateClass.MEASUREMENT,
            "mdi:arrow-up-bold-circle-outline",
            True,
        ),
        (
            "io_utilisation_percent",
            f"{fs_name} I/O Utilisation",
            PERCENTAGE,
            None,
            SensorStateClass.MEASUREMENT,
            "mdi:harddisk",
            True,
            lambda data: _array_value(data, ATTR_FS_DISK_IO_STATS, 2),
        ),
        (
            "read_await_ms",
            f"{fs_name} Read Await",
            UnitOfTime.MILLISECONDS,
            SensorDeviceClass.DURATION,
            SensorStateClass.MEASUREMENT,
            "mdi:timer-outline",
            True,
            lambda data: _array_value(data, ATTR_FS_DISK_IO_STATS, 3),
        ),
        (
            "read_time_percent",
            f"{fs_name} Read Time",
            PERCENTAGE,
            None,
            SensorStateClass.MEASUREMENT,
            "mdi:harddisk",
            True,
            lambda data: _array_value(data, ATTR_FS_DISK_IO_STATS, 0),
        ),
        (
            "weighted_io_percent",
            f"{fs_name} Weighted I/O",
            PERCENTAGE,
            None,
            SensorStateClass.MEASUREMENT,
            "mdi:harddisk",
            True,
            lambda data: _array_value(data, ATTR_FS_DISK_IO_STATS, 5),
        ),
        (
            "write_await_ms",
            f"{fs_name} Write Await",
            UnitOfTime.MILLISECONDS,
            SensorDeviceClass.DURATION,
            SensorStateClass.MEASUREMENT,
            "mdi:timer-outline",
            True,
            lambda data: _array_value(data, ATTR_FS_DISK_IO_STATS, 4),
        ),
        (
            "write_time_percent",
            f"{fs_name} Write Time",
            PERCENTAGE,
            None,
            SensorStateClass.MEASUREMENT,
            "mdi:harddisk",
            True,
            lambda data: _array_value(data, ATTR_FS_DISK_IO_STATS, 1),
        ),
    ]

    sensors = []
    for (
        api_key_suffix,
        name_suffix_full,
        unit,
        dev_class,
        state_class,
        icon,
        enabled,
        *rest,
    ) in fs_sensor_types:
        value_func = rest[0] if rest else None
        sensor = BeszelNestedSensor(
            coordinator,
            system_id,
            system_name,
            ATTR_EXTRA_FS,
            fs_name,
            api_key_suffix,
            name_suffix_full,
            unit,
            dev_class,
            state_class,
            icon,
            enabled,
            value_func=value_func,
        )
        if sensor.native_value is not None:
            sensors.append(sensor)
    return sensors


def _create_gpu_sensors(
    coordinator, system_id, system_name, gpu_id_key, gpu_name_display
):
    """Helper to create sensors for a GPU."""
    gpu_sensor_types = [
        (
            ATTR_GPU_MEM_TOTAL_MB,
            f"{gpu_name_display} Memory Total",
            UnitOfInformation.MEGABYTES,
            SensorDeviceClass.DATA_SIZE,
            SensorStateClass.MEASUREMENT,
            "mdi:memory",
            True,
        ),
        (
            ATTR_GPU_MEM_USED_MB,
            f"{gpu_name_display} Memory Used",
            UnitOfInformation.MEGABYTES,
            SensorDeviceClass.DATA_SIZE,
            SensorStateClass.MEASUREMENT,
            "mdi:memory",
            True,
        ),
        (
            ATTR_GPU_POWER_W,
            f"{gpu_name_display} Power Draw",
            UnitOfPower.WATT,
            SensorDeviceClass.POWER,
            SensorStateClass.MEASUREMENT,
            "mdi:lightning-bolt",
            True,
        ),
        (
            ATTR_GPU_POWER_PACKAGE_W,
            f"{gpu_name_display} Package Power",
            UnitOfPower.WATT,
            SensorDeviceClass.POWER,
            SensorStateClass.MEASUREMENT,
            "mdi:lightning-bolt-outline",
            True,
        ),
        (
            ATTR_GPU_USAGE_PERCENT,
            f"{gpu_name_display} Usage",
            PERCENTAGE,
            None,
            SensorStateClass.MEASUREMENT,
            "mdi:expansion-card",
            True,
        ),
    ]

    sensors = []
    for (
        api_key_suffix,
        name_suffix_full,
        unit,
        dev_class,
        state_class,
        icon,
        enabled,
    ) in gpu_sensor_types:
        sensor = BeszelNestedSensor(
            coordinator,
            system_id,
            system_name,
            ATTR_GPU_DATA,
            gpu_id_key,
            api_key_suffix,
            name_suffix_full,
            unit,
            dev_class,
            state_class,
            icon,
            enabled,
        )
        if sensor.native_value is not None:
            sensors.append(sensor)
    return sensors


def _create_available_sensors(coordinator):
    """Create sensors for all values currently reported by Beszel."""
    entities = []
    for system_id, system_data in (coordinator.data or {}).items():
        system_name = system_data.get("name", system_id)

        for sensor_type in (*SENSOR_TYPES_INFO, *SENSOR_TYPES_STATS):
            (
                api_key,
                name_suffix,
                unit,
                dev_class,
                state_class,
                icon,
                data_key,
                enabled,
                *rest,
            ) = sensor_type
            options = rest[0] if rest else None
            value_func = rest[1] if len(rest) > 1 else None
            sensor = BeszelSensor(
                coordinator,
                system_id,
                system_name,
                api_key,
                name_suffix,
                unit,
                dev_class,
                state_class,
                icon,
                data_key,
                enabled,
                options=options,
                value_func=value_func,
            )
            value = sensor.native_value
            if data_key == "status" or (
                value is not None
                and not (isinstance(value, str) and value.lower() == "unknown")
            ):
                entities.append(sensor)

        extra_fs_data = system_data.get("stats", {}).get(ATTR_EXTRA_FS, {})
        for fs_name in extra_fs_data:
            entities.extend(
                _create_extra_fs_sensors(coordinator, system_id, system_name, fs_name)
            )

        gpu_data_map = system_data.get("stats", {}).get(ATTR_GPU_DATA, {})
        for gpu_id, gpu_stats in gpu_data_map.items():
            gpu_name = gpu_stats.get(ATTR_GPU_NAME, gpu_id)
            entities.extend(
                _create_gpu_sensors(
                    coordinator, system_id, system_name, gpu_id, gpu_name
                )
            )

        temperatures = system_data.get("stats", {}).get(ATTR_TEMPERATURES, {})
        for temperature_name in temperatures:
            sensor = BeszelTemperatureSensor(
                coordinator, system_id, system_name, temperature_name
            )
            if sensor.native_value is not None:
                entities.append(sensor)

    return entities


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Beszel sensor entities based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    known_unique_ids = set()

    @callback
    def async_discover_entities():
        new_entities = []
        for entity in _create_available_sensors(coordinator):
            if entity.unique_id in known_unique_ids:
                continue
            known_unique_ids.add(entity.unique_id)
            new_entities.append(entity)
        if new_entities:
            async_add_entities(new_entities)

    async_discover_entities()
    entry.async_on_unload(coordinator.async_add_listener(async_discover_entities))


class BeszelNestedSensor(CoordinatorEntity, SensorEntity):
    """Sensor for values nested within a sub-dictionary (e.g., extra_fs, gpu_data)."""

    def __init__(
        self,
        coordinator,
        system_id,
        system_name,
        parent_key,
        item_key,
        api_value_key,
        name_full,
        unit,
        device_class,
        state_class,
        icon,
        enabled_by_default=True,
        value_func=None,
    ):
        """Initialise the nested sensor."""
        super().__init__(coordinator)
        self._system_id = system_id
        self._system_name = system_name
        self._attr_device_class = device_class
        self._attr_entity_registry_enabled_default = enabled_by_default
        self._attr_name = name_full
        self._attr_native_unit_of_measurement = unit
        self._attr_state_class = state_class
        self._attr_icon = icon
        self._attr_has_entity_name = True

        unique_part = f"{parent_key}_{item_key}_{api_value_key}"
        self._attr_unique_id = (
            f"{DOMAIN}_{coordinator.config_entry_id}_{system_id}_stats_{unique_part}"
        )

        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{coordinator.config_entry_id}_{system_id}")},
            "manufacturer": "Beszel",
            "model": "Monitored System",
            "name": system_name,
        }

        self._api_value_key = api_value_key
        self._item_key = item_key
        self._parent_key = parent_key
        self._value_func = value_func

    @property
    def system_data(self):
        """Shortcut to get the data for this sensor's system."""
        return (self.coordinator.data or {}).get(self._system_id, {})

    @property
    def available(self):
        """Return whether this system has current data."""
        return (
            super().available
            and bool(self.system_data)
            and "error" not in self.system_data
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        parent_dict = self.system_data.get("stats", {}).get(self._parent_key, {})
        item_dict = parent_dict.get(self._item_key, {})

        if self._value_func:
            return self._value_func(item_dict)

        value = item_dict.get(self._api_value_key)

        if value is not None and self._attr_native_unit_of_measurement == PERCENTAGE:
            try:
                return round(float(value), 2)
            except (TypeError, ValueError):
                return None
        return value


class BeszelSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Beszel Sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator,
        system_id,
        system_name,
        api_key,
        name_suffix,
        unit,
        device_class,
        state_class,
        icon,
        data_source_key,
        enabled_by_default=True,
        options=None,
        value_func=None,
    ):
        """Initialise the sensor."""
        super().__init__(coordinator)
        self._api_key = api_key
        self._data_source_key = data_source_key
        self._system_id = system_id
        self._system_name = system_name
        self._attr_device_class = device_class
        self._attr_entity_registry_enabled_default = enabled_by_default
        self._attr_name = name_suffix
        self._attr_native_unit_of_measurement = unit
        self._attr_state_class = state_class
        self._attr_unique_id = (
            f"{DOMAIN}_{coordinator.config_entry_id}_{self._system_id}_"
            f"{self._data_source_key}_{self._api_key}"
        )
        self._icon_definition = icon
        self._value_func = value_func

        if device_class == SensorDeviceClass.ENUM and options:
            self._attr_options = options

        self._attr_device_info = {
            "identifiers": {
                (DOMAIN, f"{coordinator.config_entry_id}_{self._system_id}")
            },
            "manufacturer": "Beszel",
            "model": "Monitored System",
            "name": self._system_name,
        }

        initial_system_data = (coordinator.data or {}).get(self._system_id, {})
        if initial_system_data and not initial_system_data.get("error"):
            agent_version = initial_system_data.get("info", {}).get(
                ATTR_AGENT_VERSION, "Unknown"
            )
            os_type_raw = initial_system_data.get("info", {}).get(ATTR_OS)
            os_name = self._map_os_type_to_name(os_type_raw)
            self._attr_device_info["sw_version"] = agent_version
            if os_name != "Unknown":
                self._attr_device_info["model"] = os_name

    @callback
    def _handle_coordinator_update(self):
        """Handle updated data from the coordinator."""
        current_data = (self.coordinator.data or {}).get(self._system_id, {})
        if current_data and not current_data.get("error"):
            new_agent_version = current_data.get("info", {}).get(ATTR_AGENT_VERSION)
            new_os_raw = current_data.get("info", {}).get(ATTR_OS)
            new_os_name = self._map_os_type_to_name(new_os_raw)

            if (
                new_agent_version
                and self._attr_device_info.get("sw_version") != new_agent_version
            ):
                self._attr_device_info["sw_version"] = new_agent_version

            if (
                new_os_name != "Unknown"
                and self._attr_device_info.get("model") != new_os_name
            ):
                self._attr_device_info["model"] = new_os_name

        super()._handle_coordinator_update()

    def _map_os_type_to_icon(self, os_type_raw):
        """Map OS type code to an icon string."""
        if os_type_raw == 0:
            return "mdi:linux"
        if os_type_raw == 1:
            return "mdi:apple"
        if os_type_raw == 2:
            return "mdi:microsoft-windows"
        if os_type_raw == 3:
            return "mdi:freebsd"
        return None

    def _map_os_type_to_name(self, os_type_raw):
        """Map OS type code to a human-readable name."""
        if os_type_raw == 0:
            return "Linux"
        if os_type_raw == 1:
            return "Darwin (macOS)"
        if os_type_raw == 2:
            return "Windows"
        if os_type_raw == 3:
            return "FreeBSD"
        return "Unknown"

    @property
    def available(self):
        """Return True if entity is available."""
        if not super().available:
            return False

        system_specific_data = (self.coordinator.data or {}).get(self._system_id)
        return bool(system_specific_data) and "error" not in system_specific_data

    @property
    def icon(self):
        """Return the icon of the sensor."""
        if self._api_key == ATTR_OS and self._data_source_key == "info":
            os_type_raw = self.system_data.get("info", {}).get(ATTR_OS)
            mapped_icon = self._map_os_type_to_icon(os_type_raw)
            if mapped_icon:
                return mapped_icon
        return self._icon_definition

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self._data_source_key == "status":
            current_status = self.system_data.get("status", "unknown")
            return str(current_status).title()

        if self._api_key == ATTR_UPTIME and self._data_source_key == "info":
            raw_seconds_val = self.system_data.get("info", {}).get(ATTR_UPTIME)
            if raw_seconds_val is None:
                return None
            try:
                total_seconds = float(raw_seconds_val)
            except (TypeError, ValueError):
                return None

            if total_seconds < 0:
                return None

            return int(total_seconds) if total_seconds.is_integer() else total_seconds

        data_dict = self.system_data.get(self._data_source_key, {})

        if not isinstance(data_dict, dict):
            return None

        if self._value_func:
            return self._value_func(data_dict)

        value = data_dict.get(self._api_key)

        if self._api_key == ATTR_OS and self._data_source_key == "info":
            return self._map_os_type_to_name(value)

        if value is not None and self._attr_native_unit_of_measurement == PERCENTAGE:
            try:
                return round(float(value), 2)
            except (TypeError, ValueError):
                return None
        return value

    @property
    def system_data(self):
        """Shortcut to get the data for this sensor's system."""
        return (self.coordinator.data or {}).get(self._system_id, {})


class BeszelTemperatureSensor(BeszelSensor):
    """Representation of a Beszel Temperature Sensor."""

    def __init__(self, coordinator, system_id, system_name, temp_sensor_key):
        """Initialise the temperature sensor."""
        self._temp_sensor_key = temp_sensor_key
        key_lower_for_name = temp_sensor_key.lower()

        if "cpu" in key_lower_for_name and "thermal" in key_lower_for_name:
            name_to_use = "CPU Temperature"
        else:
            processed_key_name = temp_sensor_key.replace("_", " ").title()
            if "Nvme" in processed_key_name:
                processed_key_name = processed_key_name.replace("Nvme", "NVME")
            name_to_use = f"Temperature {processed_key_name}"

        super().__init__(
            coordinator,
            system_id,
            system_name,
            temp_sensor_key,
            name_to_use,
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
            "mdi:thermometer",
            "stats",
            True,
        )

    @property
    def icon(self):
        """Return the icon of the temperature sensor."""
        key_lower = self._temp_sensor_key.lower()
        if "cpu" in key_lower or "thermal" in key_lower:
            return "mdi:cpu-64-bit"
        return super().icon

    @property
    def native_value(self):
        """Return the state of the sensor."""
        temps_dict = self.system_data.get("stats", {}).get(ATTR_TEMPERATURES, {})
        value = temps_dict.get(self._temp_sensor_key)
        if value is not None:
            try:
                return round(float(value), 1)
            except (TypeError, ValueError):
                return None
        return None
