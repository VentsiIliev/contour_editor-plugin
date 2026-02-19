"""
Public API for Contour Editor Plugin

This module provides two types of APIs:
1. Generic (domain-agnostic) - Uses contour_editor package
2. Workpiece-specific - Uses workpiece_editor package

Use the appropriate functions based on your use case.
"""


# Generic API (domain-agnostic)
def export_editor_data():
    """
    Export segments and settings as domain-agnostic ContourEditorData.

    This function exports raw contour data without any workpiece-specific transformations.
    Use this when integrating with non-workpiece systems.

    Returns:
        ContourEditorData: Domain-agnostic data model
    """
    pass


def configure_generic_editor():
    """
    Configure a domain-agnostic contour editor using ContourEditorBuilder.

    This returns a builder instance that you can further configure:

    Example:
        builder = configure_generic_editor()
        editor = (builder
                 .with_segment_manager(MySegmentManager)
                 .with_settings(config, provider)
                 .build())

    Returns:
        ContourEditorBuilder: Builder instance for configuration
    """
    from contour_editor import ContourEditorBuilder
    return ContourEditorBuilder()


# Workpiece-specific API
def export_workpiece_data():
    """
    Export segments and settings as workpiece-compatible data structure.

    This function transforms editor data into the format expected by workpiece systems,
    including main_contour, spray_pattern, etc.

    Returns:
        dict: Workpiece-compatible data with main_contour and spray_pattern
    """
    pass


def load_workpiece(workpiece):
    """
    Load a workpiece object into the editor.

    Args:
        workpiece: Workpiece object implementing the required interface
                  (get_main_contour, get_spray_pattern_contours, etc.)

    Returns:
        tuple: (workpiece, contours_by_layer)
    """
    from workpiece_editor import load_workpiece as _load_workpiece
    return _load_workpiece(workpiece)


def configure_workpiece_editor():
    """
    Configure a workpiece-aware contour editor using WorkpieceEditorBuilder.

    This returns a builder that automatically includes workpiece support:

    Example:
        builder = configure_workpiece_editor()
        editor = (builder
                 .with_segment_manager(BezierSegmentManager)
                 .with_settings(config, provider)
                 .with_form(form_factory)
                 .on_save(save_callback)
                 .build())

    Returns:
        WorkpieceEditorBuilder: Builder instance with workpiece support
    """
    from workpiece_editor import WorkpieceEditorBuilder
    return WorkpieceEditorBuilder()


# Configuration helpers (domain-agnostic)
def configure_segment_manager(manager_class):
    """
    Configure segment manager backend.

    Args:
        manager_class: Class implementing ISegmentManager interface
    """
    from contour_editor import SegmentManagerProvider
    SegmentManagerProvider.get_instance().set_manager_class(manager_class)


def configure_settings(config, provider=None):
    """
    Configure settings backend.

    Args:
        config: SettingsConfig instance
        provider: Optional ISettingsProvider implementation
    """
    from contour_editor import SettingsProviderRegistry
    from contour_editor.ui.new_widgets.SegmentSettingsWidget import configure_segment_settings

    if provider:
        SettingsProviderRegistry.get_instance().set_provider(provider)
    if config:
        configure_segment_settings(config)


def configure_widgets(widget_factory):
    """
    Configure custom widgets.

    Args:
        widget_factory: Factory for creating custom widgets
    """
    from contour_editor import WidgetProvider
    WidgetProvider.get().set_custom_factory(widget_factory)


def configure_additional_data_form(form_factory):
    """
    Configure an additional data form.

    Args:
        form_factory: Factory for creating form widgets
    """
    from contour_editor import AdditionalFormProvider
    AdditionalFormProvider.get().set_factory(form_factory)


def build_generic_editor(parent=None):
    """
    Build a basic domain-agnostic contour editor.

    Args:
        parent: Parent widget

    Returns:
        MainApplicationFrame: Editor instance
    """
    from contour_editor import ContourEditorBuilder, BezierSegmentManager
    return (ContourEditorBuilder()
            .with_parent(parent)
            .with_segment_manager(BezierSegmentManager)
            .build())


def build_workpiece_editor(parent=None):
    """
    Build a workpiece-aware contour editor.

    Args:
        parent: Parent widget

    Returns:
        MainApplicationFrame: Editor instance with workpiece support
    """
    from workpiece_editor import WorkpieceEditorBuilder, BezierSegmentManager
    return (WorkpieceEditorBuilder()
            .with_parent(parent)
            .with_segment_manager(BezierSegmentManager)
            .build())

