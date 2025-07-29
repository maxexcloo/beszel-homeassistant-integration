# CLAUDE.md - Development Guide

## Project Overview
**Purpose**: Home Assistant integration for Beszel server monitoring  
**Status**: Active

## Commands
```bash
# Development
black custom_components/   # Format code

# Build
# No specific build commands required - Home Assistant integration
```

## Tech Stack
- **Language**: Python 3.12+
- **Framework**: Home Assistant 2025.1.0+
- **Testing**: Home Assistant testing framework

## Code Standards

### Organization
- **Config/Data**: Alphabetical and recursive (imports, dependencies, object keys)
- **Documentation**: Sort sections, lists, and references alphabetically when logical
- **Files**: Alphabetical in documentation and directories
- **Functions**: Group by purpose, alphabetical within groups
- **Variables**: Alphabetical within scope

### Quality
- **Comments**: Minimal - only for complex business logic
- **Documentation**: Update README.md and docs with every feature change
- **Formatting**: Run black before commits
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

## Git Workflow
```bash
# After every change
black custom_components/
git add . && git commit -m "type: description"

# Always commit after verified working changes
# Keep commits small and focused
```

---

*Simple context for AI assistants working on this open source project.*
