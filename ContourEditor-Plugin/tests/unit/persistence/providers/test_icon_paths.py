import os
import pytest
def test_icon_provider_initialization():
    """Test that IconProvider initializes with correct path"""
    from contour_editor.persistence.providers import IconProvider
    provider = IconProvider.get()
    icons_dir = provider._provider.icons_dir
    assert os.path.exists(icons_dir), f"Icons directory does not exist: {icons_dir}"
    assert os.path.isdir(icons_dir), f"Icons path is not a directory: {icons_dir}"
    assert icons_dir.endswith(os.path.join('assets', 'icons')), f"Icons directory path incorrect: {icons_dir}"
    print(f"✓ Icons directory: {icons_dir}")
def test_all_standard_icons_exist():
    """Test that all standard icon files exist"""
    from contour_editor.persistence.providers import IconProvider
    provider = IconProvider.get()
    icons_dir = provider._provider.icons_dir
    # List of all standard icons used in the application
    standard_icons = [
        'open_folder',
        'hide',
        'pickup_point',
        'TOOLS',
        'drag',
        'MAGNIFIER',
        'DXF_BUTTON',
        'RECTANGLE_SELECTION',
        'reset_zoom',
        'zigzag',
        'zoom_in',
        'CAPTURE_IMAGE',
        'dropdown_open',
        'BIN_ICON',
        'PLUS_BUTTON',
        'RULER_ICON',
        'SAVE_BUTTON',
        'zoom_out',
        'offset',
        'redo',
        'BROKEN_CHAIN',
    ]
    missing_icons = []
    for icon_name in standard_icons:
        icon_path = os.path.join(icons_dir, f"{icon_name}.png")
        if not os.path.exists(icon_path):
            missing_icons.append(icon_name)
    if missing_icons:
        print(f"Missing icons: {', '.join(missing_icons)}")
    else:
        print(f"✓ All {len(standard_icons)} standard icons exist")
    assert len(missing_icons) == 0, f"Missing icon files: {', '.join(missing_icons)}"
def test_icon_provider_get_icon_valid(qapp):
    """Test that IconProvider returns valid QIcon for existing icons"""
    from PyQt6.QtGui import QIcon
    from contour_editor.persistence.providers import IconProvider
    provider = IconProvider.get()
    # Test with a known icon
    icon = provider.get_icon('zoom_in')
    assert isinstance(icon, QIcon), "get_icon should return QIcon instance"
    assert not icon.isNull(), "Icon should not be null for existing icon"
    print(f"✓ Successfully loaded 'zoom_in' icon")
def test_icon_provider_get_icon_missing(qapp):
    """Test that IconProvider handles missing icons gracefully"""
    from PyQt6.QtGui import QIcon
    from contour_editor.persistence.providers import IconProvider
    provider = IconProvider.get()
    # Test with non-existent icon
    icon = provider.get_icon('nonexistent_icon_xyz')
    assert isinstance(icon, QIcon), "get_icon should return QIcon instance even for missing icons"
    assert icon.isNull(), "Icon should be null for non-existent icon"
    print(f"✓ Correctly handles missing icons")


def test_segment_click_overlay_icon_exists(qapp):
    """Test that SegmentClickOverlay can load BROKEN_CHAIN icon via IconProvider"""
    from PyQt6.QtGui import QIcon
    from contour_editor.persistence.providers import IconProvider

    icon_provider = IconProvider.get()
    icon = icon_provider.get_icon('BROKEN_CHAIN')

    assert isinstance(icon, QIcon), "Should return QIcon"
    assert not icon.isNull(), "BROKEN_CHAIN icon should load successfully"
    print(f"✓ BROKEN_CHAIN icon loaded via IconProvider")


def test_all_icon_files_are_readable(qapp):
    """Test that all icon files can be loaded as QIcon"""
    from PyQt6.QtGui import QIcon
    from contour_editor.persistence.providers import IconProvider
    provider = IconProvider.get()
    icons_dir = provider._provider.icons_dir
    # Get all .png files in icons directory
    icon_files = [f for f in os.listdir(icons_dir) if f.endswith('.png')]
    assert len(icon_files) > 0, "No icon files found in icons directory"
    failed_icons = []
    for icon_file in icon_files:
        icon_name = icon_file[:-4]  # Remove .png extension
        icon = provider.get_icon(icon_name)
        if icon.isNull():
            failed_icons.append(icon_file)
    if failed_icons:
        print(f"Failed to load: {', '.join(failed_icons)}")
    else:
        print(f"✓ Successfully loaded all {len(icon_files)} icon files")
    assert len(failed_icons) == 0, f"Failed to load icons: {', '.join(failed_icons)}"
def test_icon_directory_structure():
    """Test that icon directory structure is correct after refactoring"""
    import contour_editor
    # Get contour_editor package directory
    contour_editor_dir = os.path.dirname(contour_editor.__file__)
    assets_dir = os.path.join(contour_editor_dir, 'assets')
    icons_dir = os.path.join(assets_dir, 'icons')
    assert os.path.exists(contour_editor_dir), f"Contour editor directory not found: {contour_editor_dir}"
    assert os.path.exists(assets_dir), f"Assets directory not found: {assets_dir}"
    assert os.path.exists(icons_dir), f"Icons directory not found: {icons_dir}"
    assert os.path.isdir(icons_dir), f"Icons path is not a directory: {icons_dir}"
    print(f"✓ Directory structure:")
    print(f"  contour_editor: {contour_editor_dir}")
    print(f"  assets: {assets_dir}")
    print(f"  icons: {icons_dir}")
def test_icon_provider_reset(qapp):
    """Test that IconProvider can be reset"""
    from contour_editor.persistence.providers import IconProvider
    provider = IconProvider.get()
    original_icons_dir = provider._provider.icons_dir
    # Reset should restore default provider
    provider.reset()
    assert provider._provider.icons_dir == original_icons_dir, "Reset should restore default icons directory"
    print(f"✓ IconProvider reset works correctly")
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
