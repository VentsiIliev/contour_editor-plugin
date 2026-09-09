from contour_editor.persistence.config.ui_config import (
    ContourEditorUiConfig,
    EditorButton,
)
from contour_editor.ui.new_widgets.BottomToolBar import BottomToolBar
from contour_editor.ui.new_widgets.TopbarWidget import TopBarWidget


def test_ui_config_shows_all_buttons_by_default(qapp):
    config = ContourEditorUiConfig()

    assert all(config.is_visible(button) for button in EditorButton)


def test_topbar_hides_only_configured_buttons(qapp):
    config = ContourEditorUiConfig.hide(
        EditorButton.GENERATE_PATTERN,
        EditorButton.PREVIEW,
    )

    toolbar = TopBarWidget(config)

    assert toolbar.generate_button.isHidden()
    assert toolbar.preview_button.isHidden()
    assert not toolbar.save_button.isHidden()


def test_bottom_toolbar_hides_only_configured_buttons(qapp):
    config = ContourEditorUiConfig.hide(EditorButton.PAN)

    toolbar = BottomToolBar(ui_config=config)

    assert toolbar.pan_toggle_button.isHidden()
    assert not toolbar.zoom_in_button.isHidden()
