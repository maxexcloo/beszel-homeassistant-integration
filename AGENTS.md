# AGENTS.md - Development Guide

## Project Overview
**Purpose**: Home Assistant integration for Beszel server monitoring  
**Status**: Active

## Commands
```bash
# Build
mise run build           # No build required for Home Assistant integration

# Development
mise run dev             # Development validation cycle

# Format
mise run fmt             # Code formatting

# Check
mise run check           # All validation (fmt)
```

## Tech Stack
- **Language**: Python 3.12+
- **Framework**: Home Assistant 2025.1.0+
- **Testing**: Home Assistant testing framework

## Code Standards

### Organization
- **Config/Data**: Alphabetical and recursive (imports, dependencies, object keys, mise tasks)
- **Documentation**: Sort sections, lists, and references alphabetically when logical
- **Files**: Alphabetical in documentation and directories
- **Functions**: Group by purpose, alphabetical within groups
- **Variables**: Alphabetical within scope

### Quality
- **Comments**: Minimal - only for complex business logic
- **Documentation**: Update README.md and docs with every feature change
- **Formatting**: Run `mise run fmt` before commits
- **KISS principle**: Keep it simple - prefer readable code over clever code
- **Naming**: Snake_case for Python, no type hints used
- **Trailing newlines**: Required in all files

## Project Structure
- **custom_components/beszel/**: Main integration directory
- **__init__.py**: Integration entry point
- **api.py**: Beszel API client using PocketBase
- **config_flow.py**: Configuration flow UI
- **const.py**: Constants and configuration
- **coordinator.py**: Data update coordinator
- **manifest.json**: Integration manifest
- **sensor.py**: Sensor entity definitions

## Project Specs
- **Dynamic Sensors**: Sensors created based on available server metrics
- **Multi-System Support**: Monitor multiple Beszel instances
- **Per-Device Sensors**: Individual sensors for GPUs and filesystems
- **Coordinator Pattern**: Centralized data fetching and caching
- **PocketBase Integration**: Uses pocketbase==0.15.0 for API communication

## README Guidelines
- **Structure**: Title → Description → Quick Start → Features → Installation → Usage → Contributing
- **Badges**: Include relevant status badges (build, version, license)
- **Code examples**: Always include working examples in code blocks
- **Installation**: Provide copy-paste commands that work
- **Quick Start**: Get users running in under 5 minutes

## Development Workflow Standards

### Environment Management
- Use **mise** for consistent development environments
- Define common tasks as mise scripts
- Pin tool versions in `.mise.toml`

### Required Development Tasks
- **build**: No build required for Home Assistant integration
- **check**: All validation (fmt)
- **dev**: Development validation cycle
- **fmt**: Code formatting
- **test**: No testing framework configured

## Error Handling Standards
- **Contextual errors**: Include device and server context in logs
- **Graceful degradation**: Continue with cached data during API failures
- **Informative messages**: Clear error responses for debugging
- **User-friendly output**: Meaningful status messages in Home Assistant

---

*Simple context for AI assistants working on this open source project.*
