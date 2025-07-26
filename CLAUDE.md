# Claude Development Guide

## Build Commands

- Format code: `black custom_components/`
- No specific build commands required - Home Assistant integration

## Code Structure

```
custom_components/beszel/
├── __init__.py      # Integration entry point
├── api.py          # Beszel API client  
├── config_flow.py  # Configuration flow
├── const.py        # Constants
├── coordinator.py  # Data update coordinator
├── manifest.json   # Integration manifest
└── sensor.py       # Sensor entities
```

## Dependencies

- Home Assistant 2025.1.0+
- pocketbase==0.15.0

## Development Notes

- Code formatted with black for consistency
- Code organized alphabetically where possible (imports, methods, variables)
- Config flow handles user setup and validation
- Coordinator pattern for data updates
- Integration uses PocketBase client for API communication  
- No type hints used (following KISS principles)
- Sensor entities created dynamically based on available metrics

## File Overview

- **api.py**: BeszelApiClient class handles authentication and data fetching
- **config_flow.py**: User configuration interface and validation  
- **coordinator.py**: DataUpdateCoordinator manages API polling
- **sensor.py**: Sensor entity definitions and state management

## Key Features

- Dynamic sensor creation based on available metrics
- Error handling and connection validation
- Multi-system support
- Per-device sensors for GPUs and filesystems
- Sorted alphabetically for maintainability

## Testing

Test manually through Home Assistant UI or use Home Assistant testing framework.
