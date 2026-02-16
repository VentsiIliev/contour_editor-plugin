# Phase 6: Testing Infrastructure - Implementation Plan
## Date: February 12, 2026
## 🎯 Goal
Build comprehensive test suite with 80%+ coverage for services and core components.
---
## 📋 Test Implementation Order
### Stage 1: Foundation & Setup (30 minutes)
**Goal:** Set up testing infrastructure and utilities
#### 1.1 Setup pytest configuration
**File:** `pytest.ini`
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --cov=src/contour_editor/services
    --cov=src/contour_editor/commands
    --cov=src/contour_editor/core/event_bus.py
    --cov-report=html
    --cov-report=term-missing
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
```
#### 1.2 Create test utilities
**File:** `tests/conftest.py`
- Shared fixtures for all tests
- Mock factories
- Test data generators
#### 1.3 Create test fixtures
**File:** `tests/fixtures/test_data.py`
- Sample segment data
- Sample contour points
- Sample settings
**Estimated Time:** 30 minutes
---
### Stage 2: Core Infrastructure Tests (2 hours)
**Goal:** Test the foundation (EventBus, CommandHistory)
#### 2.1 Test EventBus
**File:** `tests/unit/test_event_bus.py`
**Priority:** HIGH - Foundation for everything
**Test Cases:**
1. `test_event_bus_singleton` - Verify singleton pattern
2. `test_segment_visibility_changed_signal` - Test signal emission
3. `test_segment_deleted_signal` - Test deletion events
4. `test_segment_added_signal` - Test addition events
5. `test_segment_layer_changed_signal` - Test layer change events
6. `test_points_changed_signal` - Test point update events
7. `test_selection_changed_signal` - Test selection events
8. `test_active_segment_changed_signal` - Test active segment events
9. `test_multiple_subscribers` - Test multiple listeners
10. `test_signal_disconnect` - Test cleanup
**Mocks Needed:**
- Mock signal receivers (QObject with slots)
**Estimated Time:** 45 minutes
---
#### 2.2 Test CommandHistory
**File:** `tests/unit/test_command_history.py`
**Priority:** HIGH - Undo/redo foundation
**Test Cases:**
1. `test_command_history_singleton` - Verify singleton
2. `test_execute_command` - Test command execution
3. `test_undo_single_command` - Test single undo
4. `test_redo_single_command` - Test single redo
5. `test_undo_multiple_commands` - Test undo stack
6. `test_redo_multiple_commands` - Test redo stack
7. `test_can_undo` - Test undo availability
8. `test_can_redo` - Test redo availability
9. `test_clear_history` - Test history reset
10. `test_execute_clears_redo_stack` - Test redo invalidation
11. `test_command_execution_failure` - Test error handling
**Mocks Needed:**
- Mock Command implementations
- Mock manager
**Estimated Time:** 45 minutes
---
#### 2.3 Test Command Pattern
**File:** `tests/unit/test_commands.py`
**Priority:** HIGH - All undoable operations
**Test Cases:**
**AddSegmentCommand:**
1. `test_add_segment_execute` - Test segment creation
2. `test_add_segment_undo` - Test segment removal on undo
3. `test_add_segment_redo` - Test segment re-creation on redo
4. `test_add_segment_emits_event` - Test event emission
**DeleteSegmentCommand:**
5. `test_delete_segment_execute` - Test segment deletion
6. `test_delete_segment_undo` - Test segment restoration
7. `test_delete_segment_redo` - Test re-deletion
8. `test_delete_segment_emits_event` - Test event emission
9. `test_delete_segment_invalid_index` - Test error handling
**ToggleSegmentVisibilityCommand:**
10. `test_toggle_visibility_execute` - Test visibility toggle
11. `test_toggle_visibility_undo` - Test visibility restore
12. `test_toggle_visibility_emits_event` - Test event emission
**ChangeSegmentLayerCommand:**
13. `test_change_layer_execute` - Test layer change
14. `test_change_layer_undo` - Test layer restore
15. `test_change_layer_emits_event` - Test event emission
**Mocks Needed:**
- Mock BezierSegmentManager
- Mock EventBus
- Mock segments
**Estimated Time:** 30 minutes
---
### Stage 3: Service Layer Tests (3 hours)
**Goal:** Test all business logic services
#### 3.1 Test SegmentService
**File:** `tests/unit/test_segment_service.py`
**Priority:** CRITICAL - Core business logic
**Test Cases:**
**Command-based operations:**
1. `test_add_segment` - Test segment creation
2. `test_add_segment_returns_index` - Test return value
3. `test_delete_segment` - Test deletion
4. `test_toggle_visibility` - Test visibility toggle
5. `test_change_layer` - Test layer assignment
**Direct operations:**
6. `test_add_control_point` - Test control point addition
7. `test_add_control_point_invalid_index` - Test error handling
8. `test_add_anchor_point` - Test anchor point insertion
9. `test_disconnect_line` - Test line disconnection
10. `test_disconnect_line_no_segment` - Test error handling
11. `test_set_active_segment` - Test active segment setting
12. `test_set_active_segment_emits_event` - Test event emission
**Layer operations:**
13. `test_set_layer_visibility` - Test layer visibility
14. `test_set_layer_visibility_updates_segments` - Test cascade
15. `test_set_layer_locked` - Test layer locking
16. `test_set_layer_locked_emits_event` - Test event emission
**Mocks Needed:**
- Mock BezierSegmentManager
- Mock CommandHistory
- Mock EventBus
- Mock segments with layers
**Estimated Time:** 1.5 hours
---
#### 3.2 Test ContourProcessingService
**File:** `tests/unit/test_contour_processing_service.py`
**Priority:** HIGH - Geometry operations
**Test Cases:**
**Contour extraction:**
1. `test_get_workpiece_contour_points` - Test contour extraction
2. `test_get_workpiece_contour_points_no_workpiece` - Test None handling
3. `test_get_workpiece_contour_points_invalid_layer` - Test error handling
**Shrink operations:**
4. `test_shrink_contour` - Test contour shrinking
5. `test_shrink_contour_invalid_amount` - Test validation
6. `test_shrink_contour_too_small` - Test minimum size
**Spray pattern:**
7. `test_generate_spray_pattern` - Test pattern generation
8. `test_generate_spray_pattern_with_shrink` - Test with offset
9. `test_generate_spray_pattern_invalid_contour` - Test validation
10. `test_generate_spray_pattern_empty_result` - Test edge case
**Segment creation:**
11. `test_create_segments_from_points` - Test batch creation
12. `test_create_segments_from_points_empty` - Test empty input
13. `test_create_fill_pattern` - Test continuous path
14. `test_create_fill_pattern_zigzag` - Test zigzag connection
15. `test_create_contour_pattern` - Test individual segments
16. `test_create_contour_pattern_alternating` - Test direction
**Mocks Needed:**
- Mock BezierSegmentManager
- Sample numpy contour arrays
- Mock segments
**Estimated Time:** 1 hour
---
#### 3.3 Test SettingsService
**File:** `tests/unit/test_settings_service.py`
**Priority:** MEDIUM - Settings management
**Test Cases:**
**Singleton & Configuration:**
1. `test_settings_service_singleton` - Test singleton pattern
2. `test_configure` - Test configuration setup
3. `test_get_defaults` - Test default retrieval
4. `test_update_defaults` - Test default updates
**File operations:**
5. `test_load_from_file` - Test settings loading
6. `test_load_from_file_not_exists` - Test missing file
7. `test_save_to_file` - Test settings saving
8. `test_save_to_file_creates_directory` - Test directory creation
9. `test_save_to_file_error_handling` - Test write errors
**Settings management:**
10. `test_get_combo_field_key` - Test combo field retrieval
11. `test_get_settings_groups` - Test group retrieval
12. `test_apply_to_all_segments` - Test batch apply
13. `test_apply_to_all_segments_empty` - Test empty manager
**Mocks Needed:**
- Mock SettingsConfig
- Mock file system (tmp_path fixture)
- Mock BezierSegmentManager
**Estimated Time:** 30 minutes
---
### Stage 4: Widget Component Tests (2 hours)
**Goal:** Test refactored widget components
#### 4.1 Test Data Models
**File:** `tests/unit/test_models.py`
**Priority:** LOW - Simple data structures
**Test Cases:**
1. `test_list_item_data_layer` - Test layer item data
2. `test_list_item_data_segment` - Test segment item data
3. `test_list_item_data_point` - Test point item data
4. `test_list_item_data_repr` - Test string representation
**Estimated Time:** 15 minutes
---
#### 4.2 Test SegmentActions
**File:** `tests/unit/test_segment_actions.py`
**Priority:** MEDIUM - Action delegation
**Test Cases:**
1. `test_delete_segment_with_service` - Test service delegation
2. `test_delete_segment_without_service` - Test fallback
3. `test_assign_segment_layer` - Test layer assignment
4. `test_set_layer_visibility` - Test layer visibility
5. `test_set_active_segment_ui` - Test UI updates
6. `test_make_add_segment_callback` - Test callback factory
7. `test_make_layer_lock_toggle` - Test lock toggle factory
**Mocks Needed:**
- Mock ContourEditor
- Mock EventBus
- Mock CommandHistory
- Mock SegmentService
- Mock QListWidget
**Estimated Time:** 45 minutes
---
#### 4.3 Test PointManagerCoordinator
**File:** `tests/unit/test_point_manager_coordinator.py`
**Priority:** MEDIUM - Widget orchestration
**Test Cases:**
1. `test_initialization` - Test coordinator setup
2. `test_refresh_points` - Test refresh logic
3. `test_on_layer_expand_toggle` - Test layer expand/collapse
4. `test_on_segment_expand_toggle` - Test segment expand/collapse
5. `test_on_item_clicked_segment` - Test segment selection
6. `test_on_item_clicked_point` - Test point selection
7. `test_restore_selection` - Test selection persistence
8. `test_items_match` - Test item comparison
9. `test_get_current_selected_layer` - Test layer retrieval
**Mocks Needed:**
- Mock ContourEditor
- Mock QListWidget with items
- Mock segments
**Estimated Time:** 1 hour
---
### Stage 5: Integration Tests (2 hours)
**Goal:** Test end-to-end workflows
#### 5.1 Segment Workflow Integration
**File:** `tests/integration/test_segment_workflow.py`
**Priority:** HIGH - Critical user flows
**Test Cases:**
1. `test_add_delete_segment_workflow` - Full add/delete cycle
2. `test_segment_visibility_workflow` - Toggle visibility with undo
3. `test_segment_layer_change_workflow` - Change layers with undo
4. `test_multiple_segment_operations` - Complex operation sequence
5. `test_undo_redo_workflow` - Full undo/redo cycle
**Estimated Time:** 45 minutes
---
#### 5.2 Spray Pattern Workflow Integration
**File:** `tests/integration/test_spray_pattern_workflow.py`
**Priority:** HIGH - Key feature
**Test Cases:**
1. `test_generate_spray_pattern_workflow` - End-to-end pattern generation
2. `test_shrink_contour_workflow` - Shrink with segment creation
3. `test_fill_pattern_workflow` - Fill pattern generation
4. `test_contour_pattern_workflow` - Contour pattern generation
5. `test_pattern_with_layer_management` - Pattern + layer operations
**Estimated Time:** 45 minutes
---
#### 5.3 Settings Workflow Integration
**File:** `tests/integration/test_settings_workflow.py`
**Priority:** MEDIUM - Settings persistence
**Test Cases:**
1. `test_save_load_settings_workflow` - Save and reload
2. `test_apply_to_all_segments_workflow` - Batch settings apply
3. `test_default_settings_workflow` - Default management
4. `test_settings_persistence_workflow` - Cross-session persistence
**Estimated Time:** 30 minutes
---
### Stage 6: Test Fixtures & Utilities (1 hour)
**Goal:** Create reusable test data and helpers
#### 6.1 Create Fixtures
**File:** `tests/fixtures/test_data.py`
**Fixtures:**
- `sample_segments()` - List of test segments
- `sample_contour_points()` - Numpy contour arrays
- `sample_settings()` - Test settings dictionaries
- `mock_manager()` - Pre-configured mock manager
- `mock_event_bus()` - Mock EventBus
- `mock_command_history()` - Mock CommandHistory
**Estimated Time:** 30 minutes
---
#### 6.2 Create Test Helpers
**File:** `tests/utils/helpers.py`
**Helpers:**
- `create_mock_segment(index, layer_name)` - Segment factory
- `create_mock_layer(name, visible, locked)` - Layer factory
- `assert_event_emitted(signal, expected_args)` - Event assertion
- `assert_command_executed(cmd, manager)` - Command assertion
**Estimated Time:** 30 minutes
---
## 📦 Required Dependencies
```bash
pip install pytest pytest-cov pytest-qt pytest-mock
```
**Package Purposes:**
- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `pytest-qt` - Qt-specific testing utilities
- `pytest-mock` - Enhanced mocking capabilities
---
## 🎯 Success Criteria
### Coverage Targets:
- **Services:** 90%+ coverage
- **Commands:** 95%+ coverage
- **EventBus/CommandHistory:** 100% coverage
- **Widget Components:** 70%+ coverage
- **Overall:** 80%+ coverage
### Quality Metrics:
- All tests pass ✅
- No flaky tests
- Test execution < 60 seconds
- Clear test names and documentation
- Proper mocking (no external dependencies)
---
## 📊 Implementation Timeline
### Day 1 (4 hours):
- ✅ Stage 1: Foundation & Setup (30 min)
- ✅ Stage 2: Core Infrastructure Tests (2 hours)
- ✅ Stage 3.1: SegmentService Tests (1.5 hours)
### Day 2 (4 hours):
- ✅ Stage 3.2: ContourProcessingService Tests (1 hour)
- ✅ Stage 3.3: SettingsService Tests (30 min)
- ✅ Stage 4: Widget Component Tests (2 hours)
- ✅ Buffer for issues (30 min)
### Day 3 (3 hours):
- ✅ Stage 5: Integration Tests (2 hours)
- ✅ Stage 6: Fixtures & Utilities (1 hour)
**Total Estimated Time:** 11 hours (across 3 days)
---
## 🚀 Quick Start Commands
```bash
# 1. Install dependencies
pip install pytest pytest-cov pytest-qt pytest-mock
# 2. Create test directory structure
mkdir -p tests/{unit,integration,fixtures,utils}
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/integration/__init__.py
touch tests/fixtures/__init__.py
touch tests/utils/__init__.py
# 3. Run tests with coverage
pytest tests/ -v --cov=src/contour_editor/services --cov-report=html
# 4. View coverage report
open htmlcov/index.html  # On Mac
xdg-open htmlcov/index.html  # On Linux
```
---
## 📝 Test Writing Guidelines
### Naming Convention:
- Test files: `test_<module_name>.py`
- Test classes: `Test<ComponentName>`
- Test functions: `test_<what_it_tests>`
### Structure:
```python
def test_feature_name():
    # Arrange - Set up test data and mocks
    manager = Mock()
    service = SegmentService(manager, cmd_history, event_bus)
    # Act - Execute the operation
    result = service.add_segment("Contour")
    # Assert - Verify the outcome
    assert result == expected_index
    manager.create_segment.assert_called_once()
```
### Best Practices:
1. **One assertion per test** (when possible)
2. **Clear test names** describing what's tested
3. **Use fixtures** for common setup
4. **Mock external dependencies** (don't test Qt)
5. **Test both success and failure cases**
6. **Keep tests fast** (< 100ms each)
---
## 🔍 Priority Matrix
### CRITICAL (Must Have):
- ✅ EventBus tests
- ✅ CommandHistory tests
- ✅ Command pattern tests
- ✅ SegmentService tests
- ✅ Segment workflow integration tests
### HIGH (Should Have):
- ✅ ContourProcessingService tests
- ✅ Spray pattern workflow tests
- ✅ SegmentActions tests
### MEDIUM (Nice to Have):
- ✅ SettingsService tests
- ✅ PointManagerCoordinator tests
- ✅ Settings workflow tests
### LOW (Optional):
- ✅ Models tests
- ✅ Test utilities
---
## 📚 Documentation
Each test file should have:
```python
"""
Tests for <ComponentName>.
This module tests:
- Feature A
- Feature B
- Edge cases and error handling
"""
```
Each test function should have:
```python
def test_feature_name():
    """Test that feature X does Y when Z happens."""
```
---
## ✅ Checklist
### Before Starting:
- [ ] Install pytest and dependencies
- [ ] Create directory structure
- [ ] Read testing guidelines
- [ ] Review module to be tested
### For Each Test Module:
- [ ] Write fixtures in conftest.py
- [ ] Write test cases following plan
- [ ] Run tests and verify they pass
- [ ] Check coverage report
- [ ] Add missing test cases
- [ ] Refactor tests if needed
- [ ] Document any skipped tests
### After Completion:
- [ ] All tests pass
- [ ] Coverage > 80%
- [ ] No flaky tests
- [ ] Documentation complete
- [ ] Code review ready
---
## 🎉 Next Steps After Testing
1. **CI/CD Integration** - Add tests to GitHub Actions
2. **Pre-commit Hooks** - Run tests before commits
3. **Coverage Badges** - Add coverage badge to README
4. **Mutation Testing** - Verify test quality with mutmut
5. **Performance Testing** - Add benchmarks for critical paths
---
## Date
February 12, 2026
## Status
📋 **PLAN COMPLETE - Ready to implement!**
Start with Stage 1 (Foundation & Setup) and work through sequentially.
