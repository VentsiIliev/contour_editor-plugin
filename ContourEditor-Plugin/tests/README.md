# ContourEditor Test Suite
## Overview
Comprehensive test suite for the ContourEditor plugin with 109 tests achieving 71% code coverage.
## Test Structure
```
tests/
├── conftest.py              # Shared fixtures and configuration
├── unit/                    # Unit tests (95 tests)
│   ├── test_event_bus.py
│   ├── test_command_history.py
│   ├── test_commands.py
│   ├── test_segment_service.py
│   ├── test_contour_processing_service.py
│   ├── test_settings_service.py
│   ├── test_models.py
│   └── test_smoke.py
├── integration/             # Integration tests (14 tests)
│   ├── test_segment_workflow.py
│   ├── test_spray_pattern_workflow.py
│   └── test_settings_workflow.py
└── utils/                   # Test utilities and helpers
    ├── __init__.py
    └── helpers.py
```
## Running Tests
### Run All Tests
```bash
PYTHONPATH=src python3 -m pytest tests/ -v
# or
./RUN_TESTS.sh all
```
### Run Specific Test Categories
```bash
# Unit tests only
PYTHONPATH=src python3 -m pytest tests/unit/ -v
# Integration tests only
PYTHONPATH=src python3 -m pytest tests/integration/ -v
# Specific test file
PYTHONPATH=src python3 -m pytest tests/unit/test_segment_service.py -v
```
### Run Tests with Coverage
```bash
PYTHONPATH=src python3 -m pytest tests/ -v --cov=src/contour_editor --cov-report=html
open htmlcov/index.html  # View coverage report
```
### Run Specific Tests
```bash
# By test name
PYTHONPATH=src python3 -m pytest tests/unit/test_commands.py::test_add_segment_execute -v
# By marker
PYTHONPATH=src python3 -m pytest tests/ -m unit -v
```
## Available Fixtures
### Basic Fixtures (conftest.py)
#### `mock_manager`
Mock BezierSegmentManager with common methods.
```python
def test_example(mock_manager):
    mock_manager.segments = [...]
    mock_manager.get_segments.return_value = mock_manager.segments
```
#### `mock_event_bus`
Real EventBus instance (singleton reset for each test).
```python
def test_example(mock_event_bus):
    # Subscribe to events
    mock_event_bus.segment_added.connect(handler)
```
#### `mock_command_history`
Real CommandHistory instance (singleton reset for each test).
```python
def test_example(mock_command_history):
    mock_command_history.execute(command)
    assert mock_command_history.can_undo()
```
#### `sample_contour_points`
Square contour as numpy array (100x100).
```python
def test_example(sample_contour_points):
    assert sample_contour_points.shape == (5, 2)
```
#### `sample_segments`
List of 3 mock segments with different layers.
```python
def test_example(sample_segments):
    assert len(sample_segments) == 3
    assert sample_segments[0].layer.name == "Contour"
```
### Factory Fixtures
#### `mock_segment_factory`
Create custom mock segments.
```python
def test_example(mock_segment_factory):
    seg = mock_segment_factory(index=5, layer_name="Fill", num_points=6)
    assert seg.layer.name == "Fill"
```
#### `mock_layer_factory`
Create custom mock layers.
```python
def test_example(mock_layer_factory):
    layer = mock_layer_factory("Custom", visible=False, locked=True)
    assert layer.locked is True
```
#### `mock_command_factory`
Create mock commands with side effects.
```python
def test_example(mock_command_factory):
    cmd = mock_command_factory(
        execute_side_effect=lambda: segments.append(seg),
        undo_side_effect=lambda: segments.pop()
    )
```
## Test Utilities (tests/utils/helpers.py)
### Mock Creation
```python
from tests.utils.helpers import create_mock_segment, create_mock_layer
# Create a segment
seg = create_mock_segment(index=0, layer_name="Contour", visible=True)
# Create a layer
layer = create_mock_layer(name="Fill", visible=True, locked=False)
# Create a manager with segments
manager = create_mock_manager_with_segments(num_segments=5, layer_name="Contour")
```
### Assertions
```python
from tests.utils.helpers import (
    assert_segments_equal,
    assert_points_equal,
    assert_layer_properties,
    assert_command_history_state,
    compare_numpy_arrays
)
# Compare segments
assert_segments_equal(seg1, seg2, check_visibility=True, check_layer=True)
# Compare points
assert_points_equal(point1, point2, label="Control Point")
# Check layer properties
assert_layer_properties(layer, expected_name="Contour", expected_visible=True)
# Check command history state
assert_command_history_state(history, can_undo=True, can_redo=False, stack_size=3)
# Compare numpy arrays
assert compare_numpy_arrays(arr1, arr2, tolerance=1e-6)
```
### Test Data Creation
```python
from tests.utils.helpers import (
    create_test_contour,
    create_test_zigzag_pattern,
    create_test_settings
)
# Create contours
square = create_test_contour(shape="square", size=100, offset=(10, 10))
triangle = create_test_contour(shape="triangle", size=50)
hexagon = create_test_contour(shape="hexagon", size=75)
# Create zigzag pattern
zigzag = create_test_zigzag_pattern(num_lines=5, width=100, spacing=10)
# Create settings
settings = create_test_settings(layer="Fill", visible=True, color="#FF0000")
```
### Qt Helpers
```python
from tests.utils.helpers import (
    create_qpoint_list,
    qpoint_to_tuple,
    qpoint_list_to_tuples
)
# Create QPointF list from tuples
points = create_qpoint_list([(0, 0), (100, 100), (200, 50)])
# Convert QPointF to tuple
coords = qpoint_to_tuple(point)  # Returns (x, y)
# Convert list of QPointF to tuples
coords_list = qpoint_list_to_tuples(points)
```
## Writing New Tests
### Test Structure Template
```python
"""
Tests for <ComponentName>.
This module tests:
- Feature A
- Feature B
- Edge cases
"""
import pytest
from unittest.mock import Mock, patch
def test_feature_name(mock_manager, mock_event_bus):
    """Test that feature X does Y when Z happens."""
    # Arrange
    service = MyService(mock_manager, mock_event_bus)
    test_data = {...}
    # Act
    result = service.do_something(test_data)
    # Assert
    assert result == expected_value
    mock_manager.some_method.assert_called_once()
```
### Best Practices
1. **One assertion per test** - Focus on testing one thing
2. **Clear test names** - `test_<what>_<when>_<expected>`
3. **Use fixtures** - Reuse common setup code
4. **Mock external dependencies** - Don't test Qt or file system
5. **Test happy path and edge cases** - Both success and failure
6. **Keep tests fast** - Each test should run in < 100ms
7. **Make tests independent** - No test should depend on another
### Example: Testing a Service
```python
def test_add_segment_creates_and_emits_event(
    mock_manager,
    mock_command_history,
    mock_event_bus
):
    """Test that adding a segment creates it and emits event."""
    # Arrange
    from contour_editor.services.segment_service import SegmentService
    service = SegmentService(mock_manager, mock_command_history, mock_event_bus)
    # Mock command
    with patch('contour_editor.services.segment_service.AddSegmentCommand') as MockCmd:
        mock_cmd = Mock()
        mock_cmd.seg_index = 0
        MockCmd.return_value = mock_cmd
        # Act
        result = service.add_segment("Contour")
        # Assert
        assert result == 0
        MockCmd.assert_called_once_with(mock_manager, "Contour")
        mock_command_history.execute.assert_called_once_with(mock_cmd)
```
## Coverage Goals
- **Overall:** 71% (Target: 80%)
- **Services:** 70-100%
- **Commands:** 95%
- **Core Infrastructure:** 78%+
- **Models:** 100%
## CI/CD Integration
Tests are ready for CI/CD integration:
```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install pytest pytest-cov pytest-qt pytest-mock
    PYTHONPATH=src pytest tests/ -v --cov=src/contour_editor
```
## Troubleshooting
### Import Errors
Ensure `PYTHONPATH=src` is set before running tests.
### Qt Display Errors
Tests should not require a display. If you get Qt display errors, the test may be creating real Qt widgets instead of mocks.
### Slow Tests
Check for:
- File I/O operations (use `tmp_path` fixture)
- Network calls (should be mocked)
- Real Qt widget creation (use mocks)
### Flaky Tests
- Ensure proper cleanup in fixtures
- Reset singletons between tests
- Avoid shared mutable state
## Documentation
- [TESTING_PLAN.md](../TESTING_PLAN.md) - Detailed test implementation plan
- [TESTING_COMPLETE.md](../TESTING_COMPLETE.md) - Testing phase completion summary
- [STAGE3_COMPLETE.md](../STAGE3_COMPLETE.md) - Service layer tests summary
- [STAGE5_COMPLETE.md](../STAGE5_COMPLETE.md) - Integration tests summary
## Contact
For questions or issues with tests, refer to the documentation above or check existing tests for examples.
---
**Status:** ✅ 109 tests passing, 71% coverage, production ready!
