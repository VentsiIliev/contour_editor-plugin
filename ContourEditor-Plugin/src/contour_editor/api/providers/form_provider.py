from typing import Optional, Protocol, Callable
from PyQt6.QtWidgets import QWidget


class IWorkpieceFormFactory(Protocol):
    """Protocol for creating workpiece forms"""

    def create_form(self, parent: Optional[QWidget] = None) -> QWidget:
        """
        Create a workpiece form instance.

        Args:
            parent: Parent widget

        Returns:
            Widget instance that implements the workpiece form interface
        """
        ...


class WorkpieceFormProvider:
    """
    Singleton provider for workpiece form factory.

    Allows applications to inject custom workpiece form implementations
    into the contour editor.

    Usage in plugin:
        from frontend.contour_editor import WorkpieceFormProvider
        from frontend.forms.CreateWorkpieceForm import CreateWorkpieceForm

        class GlueWorkpieceFormFactory:
            def create_form(self, parent=None):
                form = CreateWorkpieceForm(parent=parent)
                form.setFixedWidth(400)
                return form

        WorkpieceFormProvider.get().set_factory(GlueWorkpieceFormFactory())

    Usage in ContourEditor:
        form = WorkpieceFormProvider.get().create_form(self)
    """

    _instance = None
    _factory: Optional[IWorkpieceFormFactory] = None

    @classmethod
    def get(cls) -> 'WorkpieceFormProvider':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def set_factory(self, factory: IWorkpieceFormFactory):
        """
        Set the workpiece form factory to use.

        Args:
            factory: Factory implementing IWorkpieceFormFactory interface
        """
        self._factory = factory
        print(f"[WorkpieceFormProvider] Using factory: {factory.__class__.__name__}")

    def create_form(self, parent: Optional[QWidget] = None) -> Optional[QWidget]:
        """
        Create a workpiece form instance.

        Args:
            parent: Parent widget

        Returns:
            Form widget instance, or None if no factory is configured
        """
        if self._factory:
            return self._factory.create_form(parent)
        return None

    def has_factory(self) -> bool:
        """Check if a factory is registered"""
        return self._factory is not None

    def reset(self):
        """Reset to no factory (useful for testing)"""
        self._factory = None

