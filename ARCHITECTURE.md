# Architecture

## Overview

The integration polls one or more Beszel Hubs through PocketBase and exposes each
monitored system as a Home Assistant device with diagnostic sensors.

## Components

### API Client

- Authenticates against current `_superusers` and legacy `users` collections.
- Normalises Hub URLs and refreshes expired authentication.
- Runs the synchronous PocketBase client outside Home Assistant's event loop.

### Configuration Flow

- Prevents duplicate Hub and account combinations.
- Supports reauthentication and complete reconfiguration from the UI.
- Tests credentials before creating or updating an entry.

### Data Coordinator

- Fetches the systems list once per 60-second update.
- Fetches each system's latest statistics concurrently.
- Preserves the last system snapshot when an individual request fails and marks
  that system's entities unavailable until it recovers.
- Raises global connection failures through Home Assistant's coordinator retry
  handling.

### Sensors

- Discovers new systems and metrics after every coordinator update.
- Exposes battery, CPU, disk, filesystem, GPU, memory, network, operating system,
  swap, temperature, uptime, and status data when reported.
- Scopes entity and device identifiers to the config entry so multiple Hubs cannot
  collide.
- Uses stable native units and returns `None` for data Beszel does not report.

## Data Flow

1. The configuration flow validates and stores normalised Hub credentials.
2. Integration setup performs the first coordinator refresh.
3. The sensor platform creates entities for the reported snapshot.
4. Each later refresh updates existing entities and discovers newly reported data.
5. An individual system failure retains its cached snapshot while making that
   system unavailable; successful systems continue updating.
