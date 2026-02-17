"""
Tests for API Providers.

This module tests:
- DialogProvider (singleton pattern, default provider, custom provider)
- WidgetProvider (singleton pattern, widget factory methods)
- IconProvider (singleton pattern, icon loading)
- AdditionalFormProvider (singleton pattern, form factory)
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from PyQt6.QtWidgets import QWidget, QDoubleSpinBox, QSpinBox, QLineEdit
from PyQt6.QtGui import QIcon, QPixmap


class TestDialogProvider:
    """Tests for DialogProvider singleton"""

    def setup_method(self):
        """Reset DialogProvider before each test"""
        from contour_editor.persistence.providers import DialogProvider
        DialogProvider._instance = None
        DialogProvider._provider = None

    def test_dialog_provider_singleton(self):
        """Test that DialogProvider follows singleton pattern"""
        from contour_editor.persistence.providers import DialogProvider

        provider1 = DialogProvider.get()
        provider2 = DialogProvider.get()

        assert provider1 is provider2

    def test_dialog_provider_has_default_provider(self):
        """Test that DialogProvider has a default provider on initialization"""
        from contour_editor.persistence.providers import DialogProvider

        provider = DialogProvider.get()
        assert provider._provider is not None

    @patch('contour_editor.persistence.providers.dialog_provider.QMessageBox')
    def test_show_warning_with_default_provider(self, mock_qmessagebox):
        """Test show_warning with default provider"""
        from contour_editor.persistence.providers import DialogProvider

        mock_qmessagebox.warning.return_value = Mock()
        provider = DialogProvider.get()
        result = provider.show_warning(None, "Title", "Message")
        # Should call QMessageBox.warning
        mock_qmessagebox.warning.assert_called_once()

    @patch('contour_editor.persistence.providers.dialog_provider.QMessageBox')
    def test_show_info_with_default_provider(self, mock_qmessagebox):
        """Test show_info with default provider"""
        from contour_editor.persistence.providers import DialogProvider

        provider = DialogProvider.get()
        provider.show_info(None, "Title", "Message")
        # Should call QMessageBox.information
        mock_qmessagebox.information.assert_called()

    @patch('contour_editor.persistence.providers.dialog_provider.QMessageBox')
    def test_show_error_with_default_provider(self, mock_qmessagebox):
        """Test show_error with default provider"""
        from contour_editor.persistence.providers import DialogProvider

        provider = DialogProvider.get()
        provider.show_error(None, "Title", "Message")
        # Should call QMessageBox.critical
        mock_qmessagebox.critical.assert_called()

    @patch('contour_editor.persistence.providers.dialog_provider.QMessageBox')
    def test_show_success_with_default_provider(self, mock_qmessagebox):
        """Test show_success with default provider"""
        from contour_editor.persistence.providers import DialogProvider

        provider = DialogProvider.get()
        provider.show_success(None, "Title", "Message")
        # Should call QMessageBox.information
        mock_qmessagebox.information.assert_called()

    def test_set_custom_provider(self):
        """Test setting a custom provider"""
        from contour_editor.persistence.providers import DialogProvider

        provider = DialogProvider.get()
        mock_custom_provider = Mock()
        mock_custom_provider.show_warning = Mock(return_value=True)
        mock_custom_provider.show_info = Mock()
        mock_custom_provider.show_error = Mock()
        mock_custom_provider.show_success = Mock()

        provider.set_custom_provider(mock_custom_provider)

        assert provider._provider is mock_custom_provider
        assert provider.show_warning(None, "T", "M") is True
        mock_custom_provider.show_warning.assert_called_once()

    def test_reset_to_default_provider(self):
        """Test resetting to default provider"""
        from contour_editor.persistence.providers import DialogProvider, DefaultDialogProvider

        provider = DialogProvider.get()
        original_provider = provider._provider

        # Set custom provider
        mock_custom = Mock()
        provider.set_custom_provider(mock_custom)
        assert provider._provider is not original_provider

        # Reset
        provider.reset()
        assert isinstance(provider._provider, DefaultDialogProvider)

    @patch('contour_editor.persistence.providers.dialog_provider.QMessageBox')
    def test_dialog_provider_with_info_text(self, mock_qmessagebox):
        """Test dialog methods with additional info_text parameter"""
        from contour_editor.persistence.providers import DialogProvider

        provider = DialogProvider.get()
        # These should not raise even with info_text
        provider.show_warning(None, "Title", "Message", "Info")
        provider.show_info(None, "Title", "Message", "Info")
        provider.show_error(None, "Title", "Message", "Info")
        provider.show_success(None, "Title", "Message", "Info")


class TestWidgetProvider:
    """Tests for WidgetProvider singleton"""

    def setup_method(self):
        """Reset WidgetProvider before each test"""
        from contour_editor.persistence.providers import WidgetProvider
        WidgetProvider._instance = None
        WidgetProvider._factory = None

    def test_widget_provider_singleton(self):
        """Test that WidgetProvider follows singleton pattern"""
        from contour_editor.persistence.providers import WidgetProvider

        provider1 = WidgetProvider.get()
        provider2 = WidgetProvider.get()

        assert provider1 is provider2

    def test_create_double_spinbox(self):
        """Test creating a double spinbox"""
        from contour_editor.persistence.providers import WidgetProvider

        provider = WidgetProvider.get()
        # Mock the factory to avoid creating actual widgets
        mock_factory = Mock()
        mock_spinbox = Mock(spec=QDoubleSpinBox)
        mock_factory.create_double_spinbox = Mock(return_value=mock_spinbox)
        provider.set_custom_factory(mock_factory)

        spinbox = provider.create_double_spinbox()
        assert spinbox is mock_spinbox

    def test_create_spinbox(self):
        """Test creating a spinbox"""
        from contour_editor.persistence.providers import WidgetProvider

        provider = WidgetProvider.get()
        # Mock the factory to avoid creating actual widgets
        mock_factory = Mock()
        mock_spinbox = Mock(spec=QSpinBox)
        mock_factory.create_spinbox = Mock(return_value=mock_spinbox)
        provider.set_custom_factory(mock_factory)

        spinbox = provider.create_spinbox()
        assert spinbox is mock_spinbox

    def test_create_lineedit(self):
        """Test creating a line edit"""
        from contour_editor.persistence.providers import WidgetProvider

        provider = WidgetProvider.get()
        # Mock the factory to avoid creating actual widgets
        mock_factory = Mock()
        mock_lineedit = Mock(spec=QLineEdit)
        mock_factory.create_lineedit = Mock(return_value=mock_lineedit)
        provider.set_custom_factory(mock_factory)

        lineedit = provider.create_lineedit()
        assert lineedit is mock_lineedit

    def test_create_widgets_with_parent(self):
        """Test creating widgets with parent"""
        from contour_editor.persistence.providers import WidgetProvider

        provider = WidgetProvider.get()
        parent = Mock(spec=QWidget)

        # Mock the factory
        mock_factory = Mock()
        mock_spinbox = Mock(spec=QDoubleSpinBox)
        mock_factory.create_double_spinbox = Mock(return_value=mock_spinbox)
        mock_factory.create_spinbox = Mock(return_value=Mock(spec=QSpinBox))
        mock_factory.create_lineedit = Mock(return_value=Mock(spec=QLineEdit))

        provider.set_custom_factory(mock_factory)

        provider.create_double_spinbox(parent)
        mock_factory.create_double_spinbox.assert_called_with(parent)

    def test_set_custom_factory(self):
        """Test setting a custom widget factory"""
        from contour_editor.persistence.providers import WidgetProvider

        provider = WidgetProvider.get()

        mock_factory = Mock()
        mock_spinbox = Mock(spec=QDoubleSpinBox)
        mock_factory.create_double_spinbox = Mock(return_value=mock_spinbox)

        provider.set_custom_factory(mock_factory)

        assert provider._factory is mock_factory
        result = provider.create_double_spinbox()
        assert result is mock_spinbox
        mock_factory.create_double_spinbox.assert_called_once()

    def test_reset_to_default_factory(self):
        """Test resetting to default factory"""
        from contour_editor.persistence.providers import WidgetProvider, DefaultWidgetFactory

        provider = WidgetProvider.get()

        # Set custom factory
        mock_factory = Mock()
        provider.set_custom_factory(mock_factory)

        # Reset
        provider.reset()
        assert isinstance(provider._factory, DefaultWidgetFactory)


class TestIconProvider:
    """Tests for IconProvider singleton"""

    def setup_method(self):
        """Reset IconProvider before each test"""
        from contour_editor.persistence.providers import IconProvider
        IconProvider._instance = None
        IconProvider._provider = None

    def test_icon_provider_singleton(self):
        """Test that IconProvider follows singleton pattern"""
        from contour_editor.persistence.providers import IconProvider

        provider1 = IconProvider.get()
        provider2 = IconProvider.get()

        assert provider1 is provider2

    def test_get_icon_returns_qicon(self):
        """Test that get_icon returns QIcon"""
        from contour_editor.persistence.providers import IconProvider

        provider = IconProvider.get()
        icon = provider.get_icon("test_icon")

        assert isinstance(icon, QIcon)

    def test_set_custom_provider(self):
        """Test setting a custom icon provider"""
        from contour_editor.persistence.providers import IconProvider

        provider = IconProvider.get()

        mock_icon = Mock(spec=QIcon)
        mock_custom_provider = Mock()
        mock_custom_provider.get_icon = Mock(return_value=mock_icon)

        provider.set_custom_provider(mock_custom_provider)

        assert provider._provider is mock_custom_provider
        result = provider.get_icon("test")
        assert result is mock_icon
        mock_custom_provider.get_icon.assert_called_once_with("test")

    def test_reset_to_default_provider(self):
        """Test resetting to default provider"""
        from contour_editor.persistence.providers import IconProvider, DefaultIconProvider

        provider = IconProvider.get()

        # Set custom provider
        mock_provider = Mock()
        provider.set_custom_provider(mock_provider)

        # Reset
        provider.reset()
        assert isinstance(provider._provider, DefaultIconProvider)

    def test_default_icon_provider_creates_valid_path(self):
        """Test that default provider creates valid icon path"""
        from contour_editor.persistence.providers import DefaultIconProvider

        provider = DefaultIconProvider()
        # Should construct path to assets/icons
        assert "icons" in provider.icons_dir


class TestAdditionalFormProvider:
    """Tests for AdditionalFormProvider singleton"""

    def setup_method(self):
        """Reset AdditionalFormProvider before each test"""
        from contour_editor.persistence.providers import AdditionalFormProvider
        AdditionalFormProvider._instance = None
        AdditionalFormProvider._factory = None

    def test_form_provider_singleton(self):
        """Test that AdditionalFormProvider follows singleton pattern"""
        from contour_editor.persistence.providers import AdditionalFormProvider

        provider1 = AdditionalFormProvider.get()
        provider2 = AdditionalFormProvider.get()

        assert provider1 is provider2

    def test_has_factory_returns_false_initially(self):
        """Test that has_factory returns False when no factory is set"""
        from contour_editor.persistence.providers import AdditionalFormProvider

        provider = AdditionalFormProvider.get()
        assert provider.has_factory() is False

    def test_create_form_returns_none_when_no_factory(self):
        """Test that create_form returns None when no factory is configured"""
        from contour_editor.persistence.providers import AdditionalFormProvider

        provider = AdditionalFormProvider.get()
        result = provider.create_form()

        assert result is None

    def test_set_factory(self):
        """Test setting a workpiece form factory"""
        from contour_editor.persistence.providers import AdditionalFormProvider

        provider = AdditionalFormProvider.get()

        mock_form = Mock()
        mock_factory = Mock()
        mock_factory.create_form = Mock(return_value=mock_form)

        provider.set_factory(mock_factory)

        assert provider._factory is mock_factory
        assert provider.has_factory() is True

    def test_create_form_with_factory(self):
        """Test creating form with factory"""
        from contour_editor.persistence.providers import AdditionalFormProvider

        provider = AdditionalFormProvider.get()

        mock_form = Mock()
        mock_factory = Mock()
        mock_factory.create_form = Mock(return_value=mock_form)

        provider.set_factory(mock_factory)
        result = provider.create_form()

        assert result is mock_form
        mock_factory.create_form.assert_called_once_with(None)

    def test_create_form_with_parent(self):
        """Test creating form with parent widget"""
        from contour_editor.persistence.providers import AdditionalFormProvider

        provider = AdditionalFormProvider.get()

        mock_form = Mock()
        mock_factory = Mock()
        mock_factory.create_form = Mock(return_value=mock_form)

        provider.set_factory(mock_factory)
        parent = Mock()
        result = provider.create_form(parent)

        assert result is mock_form
        mock_factory.create_form.assert_called_once_with(parent)

    def test_reset(self):
        """Test resetting the provider"""
        from contour_editor.persistence.providers import AdditionalFormProvider

        provider = AdditionalFormProvider.get()

        mock_factory = Mock()
        provider.set_factory(mock_factory)
        assert provider.has_factory() is True

        provider.reset()
        assert provider.has_factory() is False
        assert provider.create_form() is None


@pytest.mark.unit
class TestProviderIntegration:
    """Integration tests for multiple providers"""

    def setup_method(self):
        """Reset all providers before each test"""
        from contour_editor.persistence.providers import (
            DialogProvider, WidgetProvider, IconProvider, AdditionalFormProvider
        )
        DialogProvider._instance = None
        DialogProvider._provider = None
        WidgetProvider._instance = None
        WidgetProvider._factory = None
        IconProvider._instance = None
        IconProvider._provider = None
        AdditionalFormProvider._instance = None
        AdditionalFormProvider._factory = None

    def test_multiple_providers_are_independent_singletons(self):
        """Test that different providers are independent singletons"""
        from contour_editor.persistence.providers import (
            DialogProvider, WidgetProvider, IconProvider, AdditionalFormProvider
        )

        dialog_provider = DialogProvider.get()
        widget_provider = WidgetProvider.get()
        icon_provider = IconProvider.get()
        form_provider = AdditionalFormProvider.get()

        # Each should be singleton
        assert dialog_provider is DialogProvider.get()
        assert widget_provider is WidgetProvider.get()
        assert icon_provider is IconProvider.get()
        assert form_provider is AdditionalFormProvider.get()

        # But they should all be different objects
        assert dialog_provider is not widget_provider
        assert widget_provider is not icon_provider
        assert icon_provider is not form_provider

