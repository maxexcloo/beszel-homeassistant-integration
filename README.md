# Beszel Home Assistant Integration

[![HACS](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)
[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/maxexcloo/beszel-homeassistant-integration)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Monitor system statistics from Beszel servers in Home Assistant. This integration provides comprehensive system monitoring with dynamic sensor creation and multi-system support.

## Quick Start

1. Install via HACS or manually copy to `custom_components/beszel/`
2. Restart Home Assistant
3. Go to **Settings** → **Devices & Services** → **Add Integration**
4. Search for "Beszel" and configure with your server details

## Features

- **Agent Information**: Version tracking and system identification
- **CPU Monitoring**: Cores, model, threads, and usage percentage
- **Disk Statistics**: Read/write speeds, total space, usage, and utilization percentage
- **GPU Support**: Multi-GPU statistics including memory and power consumption
- **Kernel Information**: Version and system details
- **Memory Tracking**: Buffer/cache, percentage, total, usage, and ZFS ARC
- **Network Statistics**: Received/sent speeds and throughput
- **OS Information**: Version and distribution details
- **Per-Filesystem Monitoring**: Individual filesystem statistics
- **Swap Memory**: Percentage, total, and usage tracking
- **System Health**: Status monitoring and uptime tracking
- **Temperature Sensors**: Hardware temperature monitoring

## Installation

### HACS (Recommended)

```bash
# Add custom repository in HACS
1. Go to HACS → Integrations → Custom repositories
2. Add: https://github.com/maxexcloo/beszel-homeassistant-integration
3. Category: Integration
4. Install "Beszel" and restart Home Assistant
```

### Manual Installation

```bash
# Copy integration files
mkdir -p config/custom_components/beszel
cp -r custom_components/beszel/* config/custom_components/beszel/
# Restart Home Assistant
```

## Usage

### Configuration

1. Navigate to **Settings** → **Devices & Services**
2. Click **+ ADD INTEGRATION**
3. Search for "Beszel"
4. Enter your Beszel server details:
   - **Host**: API endpoint (e.g., `http://192.168.1.100:45876`)
   - **Username**: Your Beszel API username
   - **Password**: Your Beszel API password

### Example Configuration

```yaml
# Example sensors created automatically
sensor.beszel_server_cpu_usage
sensor.beszel_server_memory_percent
sensor.beszel_server_disk_usage
sensor.beszel_server_gpu_0_usage
sensor.beszel_server_filesystem_root_percent
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes following the code standards in CLAUDE.md
4. Format code: `black custom_components/`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
