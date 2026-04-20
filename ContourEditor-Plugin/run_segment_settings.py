from PyQt6.QtWidgets import QApplication
from src.contour_editor.ui.new_widgets.SegmentSettingsWidget import SegmentSettingsWidget, configure_segment_settings
from src.contour_editor.persistence.model.SettingsConfig import SettingsConfig, SettingsGroup

if __name__ == "__main__":
    app = QApplication([])

    config = SettingsConfig(
        default_settings={
            "Temperature": "25.0",
            "Pressure": "100",
            "Speed": "50.0",
            "Feed Rate": "10.0",
            "Tool Diameter": "5.0",
            "Material Type": "Type A",
            "Coating": "None",
            "Tolerance": "0.01",
            "Surface Finish": "Smooth",
            "Option Field": "Choice A"
        },
        groups=[
            SettingsGroup(title="Material Settings", keys=["Material Type", "Coating", "Tolerance", "Surface Finish"]),
            SettingsGroup(title="Machine Settings", keys=["Speed", "Feed Rate", "Tool Diameter"]),
            SettingsGroup(title="Environment", keys=["Temperature", "Pressure", "Option Field"])
        ],
        combo_field_key="Material Type"
    )

    configure_segment_settings(config)

    # Debug: verify configuration
    from src.contour_editor.services.settings_service import SettingsService
    service = SettingsService.get_instance()
    print(f"DEBUG: Groups configured: {service.get_settings_groups()}")
    print(f"DEBUG: Number of groups: {len(service.get_settings_groups())}")

    keys = ["Temperature", "Pressure", "Speed", "Feed Rate", "Tool Diameter",
            "Material Type", "Coating", "Tolerance", "Surface Finish", "Option Field"]
    combo_enums = [
        ["Option Field", ["Choice A", "Choice B", "Choice C"]],
        ["Material Type", ["Type A", "Type B", "Type C"]],
        ["Coating", ["None", "Chrome", "Zinc", "Paint"]],
        ["Surface Finish", ["Smooth", "Rough", "Polished"]]
    ]

    widget = SegmentSettingsWidget(keys, combo_enums, global_settings=True)
    widget.setWindowTitle("Segment Settings - Tabbed View")
    widget.resize(600, 500)
    widget.show()
    app.exec()
