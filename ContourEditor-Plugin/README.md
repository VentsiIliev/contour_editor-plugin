# Contour Editor Plugin

A domain-agnostic, extensible contour editing framework for PyQt6 applications with workpiece-specific extensions.

## Overview

This plugin provides two main components:

1. **Pure Contour Editor** - Domain-agnostic contour editing without workpiece-specific functionality
2. **Workpiece Editor** - Extended editor with workpiece forms, spray patterns, and specialized settings

### Key Features

- Bezier curve segment editing with visual handles
- Undo/redo command history
- Customizable settings framework with provider pattern
- Form integration for workpiece-specific data
- Export/import functionality
- Extensible architecture for custom segment managers
- Comprehensive test coverage

## Project Structure

```
ContourEditor-Plugin/
├── package-dist/          # Build configuration and distribution files
│   ├── BUILD_WHEEL.sh     # Build script for creating wheel package
│   ├── pyproject.toml     # Package configuration
│   ├── MANIFEST.in        # Package manifest
│   └── LICENSE            # License file
├── src/
│   ├── contour_editor/    # Pure contour editor module
│   ├── workpiece_editor/  # Workpiece-specific extensions
│   └── public_api.py      # Public API exports
├── tests/                 # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   ├── workpiece_editor/  # Workpiece editor tests
│   └── conftest.py        # Pytest configuration
├── run_contour_editor.py  # Launch pure contour editor
└── run_workpiece_editor.py # Launch workpiece editor
```

## Requirements

- Python 3.8+
- PyQt6
- NumPy
- SciPy
- Matplotlib

## Building the Package

### Prerequisites

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate     # On Windows
```

Install build dependencies:

```bash
pip install build wheel setuptools
```

### Build Wheel Package

```bash
cd package-dist
chmod +x BUILD_WHEEL.sh
./BUILD_WHEEL.sh
```

The wheel file will be created in `package-dist/dist/`.

### Build Verification

Verify wheel contents:

```bash
cd package-dist
./verify_wheel_contents.sh
```

## Installation

### From Wheel File

```bash
# In your target project's virtual environment
pip install /path/to/contour_editor-plugin/ContourEditor-Plugin/package-dist/dist/contour_editor_plugin-*.whl
```

### Editable Install (Development)

```bash
# In your target project's virtual environment
pip install -e /path/to/contour_editor-plugin/ContourEditor-Plugin/package-dist
```

### From SVN Repository

```bash
pip install svn+https://your-svn-repo-url/path/to/contour_editor-plugin/ContourEditor-Plugin/package-dist#egg=contour_editor_plugin
```

## Usage

### As a Standalone Application

#### Pure Contour Editor

```bash
python run_contour_editor.py
```

Launches the domain-agnostic contour editor without workpiece-specific features.

#### Workpiece Editor

```bash
python run_workpiece_editor.py
```

Launches the extended editor with workpiece forms and spray pattern support.

### As a Library in Your Project

```python
from contour_editor_plugin import build_contour_editor, build_workpiece_editor

# Build pure contour editor
editor = build_contour_editor(
    segment_manager_class=MySegmentManager,
    settings_provider=MySettingsProvider()
)

# Or build workpiece editor
workpiece_editor = build_workpiece_editor(
    segment_settings_provider=MySegmentSettingsProvider(),
    form_settings_provider=MyFormSettingsProvider(),
    execute_handler=my_execute_handler
)
```

### Custom Settings Provider

```python
from contour_editor_plugin import ISettingsProvider

class MySettingsProvider(ISettingsProvider):
    def get_all_setting_keys(self):
        return ["speed", "power", "passes"]
    
    def get_default_values(self):
        return {"speed": "100", "power": "50", "passes": "1"}
    
    def get_setting_label(self, key: str):
        return key.replace('_', ' ').title()
    
    def get_settings_tabs_config(self):
        return [("Settings", ["speed", "power", "passes"])]
```

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test Suites

```bash
# Unit tests only
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Workpiece editor tests
pytest tests/workpiece_editor/

# Specific test file
pytest tests/unit/test_main_frame_execute_requested.py
```

### Run with Coverage

```bash
pytest --cov=src --cov-report=html --cov-report=term
```

Coverage report will be available in `htmlcov/index.html`.

### Run with Verbose Output

```bash
pytest -v
```

### Run Smoke Tests

```bash
pytest tests/test_smoke.py
```

## Development

### Setting Up Development Environment

```bash
# Clone from SVN
svn checkout <repo-url>

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

### Code Style

The project follows PEP 8 style guidelines. Key conventions:

- Use type hints where applicable
- Follow existing naming conventions
- Add tests for new features
- Update documentation as needed

### Testing Guidelines

- Write unit tests for individual components
- Add integration tests for component interactions
- Use fixtures from `conftest.py` for common setups
- Mock external dependencies
- Aim for high test coverage

## Architecture

### Builder Pattern

The plugin uses builder pattern for flexible editor construction:

```python
editor = (ContourEditorBuilder()
          .with_segment_manager(BezierSegmentManager)
          .with_settings(config, provider)
          .with_form(form)
          .build())
```

### Command Pattern

Undo/redo functionality implemented via command pattern:

- `BaseCommand` - Abstract command interface
- `SegmentCommands` - Concrete command implementations
- `CommandHistory` - Command history manager

### Provider Pattern

Settings and configuration use provider pattern for extensibility:

- `ISettingsProvider` - Settings provider interface
- `ISegmentSettingsProvider` - Segment-specific settings
- `IFormSettingsProvider` - Form-specific settings

### Signal-Based Architecture

Components communicate via PyQt signals:

- `execute_requested` - Emitted when execution is requested with complete data
- `start_requested` - Emitted when start button is clicked
- Custom signals for component-specific events

## API Reference

### Public API

```python
from contour_editor_plugin import (
    # Builders
    build_contour_editor,
    build_workpiece_editor,
    ContourEditorBuilder,
    WorkpieceEditorBuilder,
    
    # Segment Managers
    BezierSegmentManager,
    
    # Providers
    ISettingsProvider,
    ISegmentSettingsProvider,
    IFormSettingsProvider,
    
    # Configuration
    SettingsConfig,
    SettingsGroup,
    
    # Forms
    CreateWorkpieceForm,
    create_workpiece_form_config
)
```

## Troubleshooting

### Import Errors

If you encounter import errors, ensure:

1. Virtual environment is activated
2. Package is installed: `pip list | grep contour-editor-plugin`
3. Python path includes src directory (for development mode)

### Build Errors

If build fails with "externally-managed-environment":

```bash
# Use virtual environment instead of system Python
python3 -m venv venv
source venv/bin/activate
pip install build wheel
cd package-dist
./BUILD_WHEEL.sh
```

### Test Errors

If tests fail with missing segment manager:

```python
# In test setup, register segment manager
from contour_editor.providers import SegmentManagerProvider
SegmentManagerProvider.get_instance().set_manager_class(BezierSegmentManager)
```

## License

See LICENSE file in package-dist directory.

## Contributing

1. Checkout from SVN repository
2. Create feature branch
3. Add tests for new functionality
4. Ensure all tests pass: `pytest`
5. Commit changes to SVN
6. Request code review

## Support

For issues or questions:

1. Check existing documentation
2. Review test examples in `tests/` directory
3. Examine example launchers: `run_contour_editor.py` and `run_workpiece_editor.py`

## Changelog

See commit history in SVN repository for detailed changes.
