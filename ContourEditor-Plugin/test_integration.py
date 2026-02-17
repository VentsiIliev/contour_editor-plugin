#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, 'src')

print("=" * 60)
print("Testing Generic Form Integration")
print("=" * 60)

try:
    print("\n1. Testing CreateWorkpieceForm imports...")
    from workpiece_editor.ui.CreateWorkpieceForm import (
        CreateWorkpieceForm, FormFieldConfig, GenericFormConfig
    )
    print("   ✅ CreateWorkpieceForm imported successfully")

    print("\n2. Testing model imports...")
    from workpiece_editor.models import (
        BaseWorkpiece, GenericWorkpiece, WorkpieceFactory, WorkpieceField
    )
    print("   ✅ Models imported successfully")

    print("\n3. Testing form configuration...")
    from enum import Enum

    class TestPriority(Enum):
        LOW = "low"
        HIGH = "high"

    fields = [
        FormFieldConfig(
            field_id='name',
            field_type='text',
            label='Name',
            icon_path='',
            placeholder='Enter name',
            mandatory=True
        ),
        FormFieldConfig(
            field_id='priority',
            field_type='dropdown',
            label='Priority',
            icon_path='',
            options=list(TestPriority),
            default_value=TestPriority.LOW.name
        )
    ]

    config = GenericFormConfig(
        form_title='Test Form',
        fields=fields,
        config_file='test_config.json'
    )
    print(f"   ✅ Created config with {len(config.fields)} fields")
    print(f"   ✅ Form title: {config.form_title}")

    print("\n4. Testing run_workpiece_editor imports...")
    exec(open('run_workpiece_editor.py').read(), {'__name__': '__test__'})
    print("   ✅ run_workpiece_editor.py syntax is valid")

    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED")
    print("=" * 60)

except Exception as e:
    print(f"\n❌ TEST FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

