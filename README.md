# Beszel Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)

The `beszel` integration allows you to monitor system statistics from servers running the Beszel agent. It fetches data such as CPU usage, memory usage, disk space, network traffic, and more, making it available as sensors within Home Assistant.

## Features

*   Monitors various system metrics including:
    *   CPU (usage, model, cores, threads)
    *   Memory (used, total, percent, buffer/cache, ZFS ARC)
    *   Swap (used, total, percent)
    *   Disk (used, total, percent)
    *   Network (sent/received speeds)
    *   System Uptime
    *   Agent Version
    *   OS and Kernel Version
    *   System Status (up, down, etc.)
    *   Temperatures (including specific CPU temperature if available)
    *   GPU statistics (if available)
    *   Per-filesystem statistics (if available)
*   Configurable update interval.
*   Automatic discovery of multiple systems if your Beszel API endpoint provides them.

## Prerequisites

*   A running instance of the Beszel agent/server that exposes an API endpoint.
*   Home Assistant version 2025.1.0 or newer.

## Installation

### Via HACS (Recommended)

1.  Ensure HACS is installed.
2.  Go to HACS > Integrations.
3.  Click the three dots in the top right corner and select "Custom repositories".
4.  Enter the URL of this repository (`https://github.com/maxexcloo/beszel-homeassistant-integration`) in the "Repository" field.
5.  Select "Integration" as the category.
6.  Click "Add".
7.  The "Beszel" integration should now appear in the HACS integrations list. Click "Install".
8.  Restart Home Assistant.

### Manual Installation

1.  Copy the `custom_components/beszel` directory to your Home Assistant `config/custom_components/` directory.
2.  Restart Home Assistant.

## Configuration

To add the Beszel integration to your Home Assistant instance:

1.  Go to **Settings** > **Devices & Services**.
2.  Click the **+ ADD INTEGRATION** button in the bottom right.
3.  Search for "Beszel" and select it.
4.  In the configuration dialog, enter:
    *   **Host**: The hostname or IP address of your Beszel API (e.g., `http://your-beszel-server.local:port` or `https://your-beszel-server.com`).
    *   **Username**: Your Beszel API username.
    *   **Password**: Your Beszel API password.
5.  Click **Submit**.

The integration will attempt to connect to the Beszel API and, if successful, will set up entities for each monitored system and its statistics.

## Sensors

The integration creates a variety of sensor entities for each system reported by the Beszel API. These include overall system information and detailed statistics. For systems with multiple GPUs or additional filesystems, dedicated sensors will be created for each.

## Contributions

Contributions are welcome! Please feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License.
