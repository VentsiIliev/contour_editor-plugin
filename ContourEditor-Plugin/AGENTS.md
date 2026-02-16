# ContourEditor Plugin - AI Agent Guide
## Architecture Overview
This is a **PyQt6-based contour editing widget** designed as a reusable, backend-agnostic plugin. The core principle is **dependency injection** - the editor knows nothing about domain-specific concepts (robots, workpieces, etc.).
### Key Architectural Layers
1. **Core Editor** (`contourEditorDecorators/ContourEditor.py`) - The base QFrame with rendering, event handling, and state management
2. **Decorator Pattern** - Features are added via composition:
   - `ContourEditorWithRulers` wraps the editor with ruler widgets
   - `ContourEditorWithBottomToolBar` adds zoom controls
   - `MainApplicationFrame` (`ContourEditor.py`) is the top-level widget with toolbar and side panels
3. **Manager Pattern** - State is segregated into focused managers (all in `managers/`):
   - `WorkpieceManager` - contour/layer data
   - `ViewportController` - zoom, pan, image state
   - `ToolManager` - tool modes (drag, select, measure)
   - `SelectionManager` - point selection state
   - `EventManager`, `ModeManager`, `OverlayManager`, etc.
4. **Provider Pattern** - External systems inject implementations via singletons:
   - `SegmentManagerProvider` - MUST be configured before creating editor (no default)
   - `SettingsProviderRegistry`, `DialogProvider`, `WidgetProvider`, `IconProvider`, `WorkpieceFormProvider`
### Data Flow & Boundaries
```
Domain Objects (Workpiece) 
  ↓ WorkpieceAdapter
ContourEditorData (domain-agnostic)
  ↓ Segment/Layer interfaces
ContourEditor internal state
```
**WorkpieceAdapter** (`adapters/WorkpieceAdapter.py`) is the ONLY place that knows about domain-specific Workpiece objects. It converts between:
- `Workpiece` → `ContourEditorData` (via `from_workpiece()`)
- `ContourEditorData` → dict for workpiece updates (via `to_workpiece_data()`)
**ContourEditorData** (`EditorDataModel.py`) is the canonical domain-agnostic format:
- Organizes Segments by Layer names ("Workpiece", "Contour", "Fill")
- Provides `to_dict()`/`from_dict()` for serialization
- NO knowledge of domain concepts
## Critical Setup Pattern
Before instantiating any editor widget, you MUST register a segment manager:
```python
from contour_editor import SegmentManagerProvider
from your_backend import YourSegmentManager
SegmentManagerProvider.get_instance().set_manager_class(YourSegmentManager)
```
Without this, editor initialization will raise `RuntimeError`. The editor is intentionally backend-agnostic and refuses to provide a default implementation.
## Mode System
The editor uses a **state machine** pattern (`EditorStateMachine/`) with mode objects in `EditorStateMachine/Modes/`:
- **Edit Mode** - default, select/drag points
- **Drag Mode** (Pan) - click-drag to pan viewport
- **Multi-Select Mode** - click multiple points to batch select
- **Rectangle Select Mode** - drag to select points in area
- **Pickup Point Mode** - click to set a reference point
- **Ruler Mode** - measure distances
Modes are managed by `ModeManager` and handle their own mouse events via delegation pattern.
## Settings & Constants
**Two-tier settings system:**
1. **Global constants** (`constants.py`) - defaults for colors, sizes, thresholds
2. **User overrides** (`ConstantsManager.py`) - loads from `contour_editor_settings.json`, falls back to constants.py
To modify visual appearance, edit `constants.py` or call `ConstantsManager.save_settings(data)` to persist user changes.
**Global segment settings** are stored in `global_segment_settings.json` (layer-specific defaults like line width, glue type).
## Coordinate Spaces
Always be aware of **two coordinate systems**:
- **Image space** - coordinates in the source image (used for point storage, geometry)
- **Screen space** - viewport coordinates after zoom/pan transform
Use `utils/coordinate_utils.py`:
- `map_to_image_space(screen_pos, translation, scale)` - screen → image
- `map_to_screen_space(img_pos, translation, scale)` - image → screen
Hit detection uses screen-space thresholds (e.g., 10px) converted to image space: `threshold_img = 10 / scale_factor`
## Event Handling
Events flow through `handlers/`:
- `mouse_event_handler.py` - dispatches to appropriate mode/manager
- `gesture_handler.py` - pinch-to-zoom support
- `zoom_handler.py` - wheel zoom
The pattern: handlers are **pure functions** that take `(editor, event)` and delegate to mode objects or managers.
## Rendering Pipeline
`paintEvent` → `EditorRenderer.render()` → individual draw functions in `rendering/renderer.py`
**Transform order matters:**
1. Apply viewport transform (translate + scale)
2. Draw image-space elements (segments, points, rulers)
3. Reset transform
4. Draw screen-space overlays (crosshair, UI elements)
## Common Patterns
**Backward compatibility via properties:** The editor used to store state directly. Now it uses properties that delegate to managers:
```python
@property
def scale_factor(self):
    return self.viewport_controller.scale_factor
```
**Signal-based communication:** Widgets communicate via PyQt signals, not direct method calls:
```python
self.editor.update_camera_feed_requested.connect(self.parent.refresh_camera)
```
**Layer naming convention:**
- "Workpiece" - external boundary (red)
- "Contour" - spray pattern paths (cyan)
- "Fill" - fill regions (green)
## Testing
No formal test suite exists. Manual testing via `test.py` (contains a RadialMenu example, not actual tests).
To test editor changes:
1. Run `MainApplicationFrame` as standalone widget
2. Load DXF files from `dxf/` directory
3. Verify operations: zoom, pan, point drag, undo/redo, save
## Common Pitfalls
1. **Forgetting to register SegmentManager** - will crash on editor init
2. **Mixing coordinate spaces** - always convert before hit testing or drawing
3. **Modifying constants.py directly** - changes won't persist; use ConstantsManager
4. **Direct widget coupling** - use providers for cross-boundary integration
5. **Assuming segments have settings** - segments may have empty `settings` dict
## File Organization Clues
- `contourEditorDecorators/ContourEditor.py` - 400+ line monolith, the actual editor core
- `ContourEditor.py` - top-level application frame (confusing naming!)
- `managers/` - state management, split by concern
- `handlers/` - event processing logic
- `rendering/` - paint operations
- `widgets/` - UI components (dialogs, toolbars, side panels)
- `model/` - domain-agnostic data classes
- `adapters/` - conversion layer to/from domain objects
- `providers/` - dependency injection interfaces
- `interfaces/` - abstract types for plugin points
## Making Changes
**To add a new tool mode:**
1. Create mode class in `EditorStateMachine/Modes/` extending `BaseMode`
2. Register in `ModeManager.__init__()`
3. Add mode constant to `constants.py`
4. Add UI trigger in appropriate toolbar/menu
**To change rendering:**
1. Modify draw functions in `rendering/renderer.py`
2. Update constants in `constants.py` for appearance
3. Ensure proper coordinate space (image vs screen)
**To add segment metadata:**
1. Extend `Segment.settings` dict (arbitrary JSON)
2. Handle in `WorkpieceAdapter` if domain-specific
3. Update UI in `SegmentSettingsWidget` for editing
## Post-Restructuring Notes (February 2026)
The package was successfully restructured with the following changes:
**New Structure:**
- `config/` - All settings files (constants.py, constants_manager.py, JSONs)
- `core/` - Editor widgets (editor.py, main_frame.py, editor_with_rulers.py, editor_with_toolbar.py)
- `data/` - Data models (editor_data_model.py, segment_provider.py, settings_provider_registry.py)
- `state/` - State machine and mode handlers (all modes in state/mode_handlers/)
- `assets/` - Icons and DXF files (renamed from icons/)
- `tests/` - Test code separated from production
**Updated Import Paths:**
```python
# Old paths (deprecated, but still work via shims)
from contour_editor.constants import DRAG_MODE
from contour_editor.EditorDataModel import ContourEditorData
# New paths (recommended)
from contour_editor.config.constants import DRAG_MODE
from contour_editor.data.editor_data_model import ContourEditorData
```
**Key File Renames:**
- `ContourEditor.py` → `core/main_frame.py` (top-level application)
- `contourEditorDecorators/ContourEditor.py` → `core/editor.py` (base editor)
- `EditorStateMachine/Modes/*.py` → `state/mode_handlers/*.py` (all lowercase)
All old import paths continue to work via compatibility shims with deprecation warnings.
