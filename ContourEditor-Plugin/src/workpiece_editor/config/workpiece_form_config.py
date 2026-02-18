import os
from workpiece_editor.ui.CreateWorkpieceForm import FormFieldConfig, GenericFormConfig


def get_icon_path(icon_name):
    base_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'icons')
    icon_file = f"{icon_name}.png"
    full_path = os.path.join(base_path, icon_file)
    return full_path if os.path.exists(full_path) else ""


def get_contour_icon_path(icon_name):
    base_path = os.path.join(os.path.dirname(__file__), '..', '..', 'contour_editor', 'assets', 'icons')
    icon_file = f"{icon_name}.png"
    full_path = os.path.join(base_path, icon_file)
    return full_path if os.path.exists(full_path) else ""



def create_workpiece_form_config(glue_types=None) -> GenericFormConfig:
    if glue_types is None or (isinstance(glue_types, list) and len(glue_types) == 0):
        glue_types = ["Type A", "Type B", "Type C"]

    fields = [
        FormFieldConfig(
            field_id="workpieceId",
            field_type="text",
            label="Workpiece ID",
            icon_path=get_icon_path("WOPIECE_ID_ICON_2"),
            placeholder="",
            mandatory=True,
            visible=True
        ),
        FormFieldConfig(
            field_id="name",
            field_type="text",
            label="Name",
            icon_path=get_icon_path("WORKPIECE_NAME_ICON"),
            placeholder="",
            mandatory=False,
            visible=True
        ),
        FormFieldConfig(
            field_id="description",
            field_type="text",
            label="Description",
            icon_path=get_icon_path("DESCRIPTION_WORKPIECE_BUTTON_SQUARE"),
            placeholder="",
            mandatory=False,
            visible=True
        ),
        FormFieldConfig(
            field_id="height",
            field_type="text",
            label="Height",
            icon_path=get_contour_icon_path("RULER_ICON"),
            placeholder="",
            mandatory=True,
            visible=True
        ),
        FormFieldConfig(
            field_id="glue_qty",
            field_type="text",
            label="Glue Quantity",
            icon_path=get_icon_path("glue_qty"),
            placeholder="g /m²",
            mandatory=False,
            visible=True
        ),
        FormFieldConfig(
            field_id="gripper_id",
            field_type="dropdown",
            label="Gripper",
            icon_path=get_icon_path("GRIPPER_ID_ICON"),
            options=["Gripper1", "Gripper2", "Gripper3"],
            mandatory=False,
            visible=True
        ),
        FormFieldConfig(
            field_id="glue_type",
            field_type="dropdown",
            label="Glue Type",
            icon_path=get_icon_path("GLUE_TYPE_ICON"),
            options=glue_types,
            mandatory=True,
            visible=True
        ),
    ]

    return GenericFormConfig(
        form_title="Create Workpiece",
        fields=fields,
        accept_button_icon="",
        cancel_button_icon="",
        config_file="settings/workpiece_form_config.json"
    )

