from contour_editor.persistence.config.ui_config import (
    ContourEditorUiConfig,
    CustomEditorButtonSpec,
    EditorButton,
    ToolbarPlacement,
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


def test_custom_topbar_button_emits_its_action_id(qapp):
    config = ContourEditorUiConfig(
        custom_buttons=(
            CustomEditorButtonSpec(
                action_id="paint_action",
                icon_name="fa5s.spray-can",
                tooltip="Paint action",
                placement=ToolbarPlacement.TOP_RIGHT,
            ),
        ),
    )
    toolbar = TopBarWidget(config)
    received = []
    toolbar.custom_action_requested.connect(received.append)

    toolbar.custom_buttons["paint_action"].click()

    assert received == ["paint_action"]


def test_custom_bottom_button_emits_its_action_id(qapp):
    config = ContourEditorUiConfig(
        custom_buttons=(
            CustomEditorButtonSpec(
                action_id="bottom_action",
                icon_name="fa5s.crosshairs",
                placement=ToolbarPlacement.BOTTOM,
            ),
        ),
    )
    toolbar = BottomToolBar(ui_config=config)
    received = []
    toolbar.custom_action_requested.connect(received.append)

    toolbar.custom_buttons["bottom_action"].click()

    assert received == ["bottom_action"]
