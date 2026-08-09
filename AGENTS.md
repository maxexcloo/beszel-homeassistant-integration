# AGENTS.md - Development Guide

## Project Overview

Home Assistant integration for monitoring one or more Beszel Hubs and their systems.

## Commands

```bash
mise run build   # Confirm that no build is required
mise run check   # Run linting, formatting checks, and tests
mise run dev     # Run the development validation cycle
mise run fmt     # Fix and format Python with Ruff
mise run lint    # Check Python with Ruff
mise run setup   # Install locked test dependencies
mise run test    # Run pytest
```

## Code Standards

### Organisation

- Keep configuration, imports, mappings, tasks, and unordered peers alphabetical.
- Keep interface, lifecycle, fallback, and procedural order when it is meaningful.
- Group functions by purpose and sort them alphabetically within each group.
- Use snake_case for project-owned Python names.

### Quality

- Add focused Home Assistant tests for behavioural changes.
- Keep comments minimal and limited to complex business logic.
- Keep implementation simple and readable; do not add type hints.
- Run `mise run fmt` and `mise run check` before committing.
- Update `README.md` and architecture documentation with feature changes.
- Use Ruff for Python formatting and linting; do not use Black.
- Use trailing newlines in every file.

## Error Handling

- Include Beszel Hub and system context in logs.
- Preserve cached system data during partial API failures.
- Raise authentication failures so Home Assistant can start reauthentication.
- Return unavailable data as `None`; do not convert missing measurements to zero.

## Project Structure

- `custom_components/beszel/`: Integration implementation and translations.
- `tests/`: Home Assistant integration tests.
- `.github/workflows/`: Ruff, pytest, Hassfest, and HACS validation.
- `.mise.toml`: Pinned tools and development tasks.
- `ARCHITECTURE.md`: Technical design and data flow.
- `README.md`: Installation, usage, and contribution guidance.

## Project Specifications

- Coordinator-based polling every 60 seconds.
- Dynamic discovery of systems, GPUs, filesystems, temperatures, and metrics.
- Hub-scoped devices and entities for safe multi-Hub configuration.
- PocketBase 0.17.3 API integration.
- Python 3.12.0 or newer.
- Home Assistant 2025.1.0 or newer.
