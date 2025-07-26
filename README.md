# Beszel Home Assistant Integration

[![HACS](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)

Monitor system statistics from Beszel servers in Home Assistant.

## Configuration

1. Go to **Settings** > **Devices & Services**
2. Click **+ ADD INTEGRATION** 
3. Search for "Beszel"
4. Enter your Beszel API details:
   - **Host**: API endpoint (e.g., `http://server:port`)
   - **Username**: API username
   - **Password**: API password

## Features

- Agent version
- CPU (cores, model, threads, usage)
- Disk (read/write speeds, total, usage, percent)
- GPU statistics
- Kernel version
- Memory (buffer/cache, percent, total, usage, ZFS ARC)
- Network (received/sent speeds)
- OS version
- Per-filesystem statistics
- Swap (percent, total, usage)
- System status and uptime
- Temperatures

## Installation

### HACS (Recommended)

1. Add custom repository: `https://github.com/maxexcloo/beszel-homeassistant-integration`
2. Category: Integration
3. Install and restart Home Assistant

### Manual

1. Copy `custom_components/beszel/` to `config/custom_components/`
2. Restart Home Assistant

## Prerequisites

- Beszel agent/server with API endpoint
- Home Assistant 2025.1.0+

## Sensors

Creates sensor entities for each monitored system with detailed statistics and per-device sensors for multiple GPUs/filesystems.
