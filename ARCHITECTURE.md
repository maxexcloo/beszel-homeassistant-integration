# ARCHITECTURE.md - Technical Design

## Overview

Home Assistant integration for monitoring Beszel server statistics with dynamic sensor creation and multi-system support.

## Core Components

### Configuration Flow
- **Config Entry**: User-friendly setup via Home Assistant UI
- **Multi-Server**: Support for multiple Beszel instances
- **Validation**: Connection testing during setup

### Data Coordinator
- **Auto-Update**: 30-second polling interval with exponential backoff
- **Caching**: In-memory data storage with error handling
- **Thread Safety**: Async coordination for concurrent requests

### Dynamic Sensors
- **Auto-Discovery**: Sensors created based on available metrics
- **Per-Device**: Individual sensors for GPUs and filesystems
- **State Management**: Proper device class and unit of measurement assignment

## Data Flow

1. **Initial Setup**: Config flow → Authentication → Server discovery → Sensor creation
2. **Data Updates**: Timer trigger → API fetch → Data parse → Sensor update → State broadcast
3. **Error Handling**: API failure → Cached data → Exponential backoff → Retry logic

## API Integration

### PocketBase Client
- **Authentication**: Username/password with token refresh
- **Data Fetching**: Systems and statistics endpoints
- **Error Handling**: Connection timeouts and API failures

### Server Metrics
- **Agent Information**: Version tracking and system identification
- **Hardware Stats**: CPU, memory, disk, GPU, and network metrics
- **System Info**: Kernel version and OS details

## Technology Stack

### Backend
- **Framework**: Home Assistant 2025.1.0+
- **Language**: Python 3.12+
- **API Client**: pocketbase==0.15.0

### Integration Pattern
- **Coordinator**: DataUpdateCoordinator for centralized updates
- **Config Flow**: ConfigEntry for user setup
- **Device Registry**: Automatic device creation and management

---

*Technical architecture documentation for the Beszel Home Assistant Integration project.*
