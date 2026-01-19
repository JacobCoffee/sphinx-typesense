"""Tests for SearchBackend abstract base class."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from unittest.mock import MagicMock

from sphinx_typesense.backends.base import SearchBackend


class ConcreteBackend(SearchBackend):
    """Concrete implementation for testing."""

    name = "test"

    def index_all(self) -> int:
        """Return test document count."""
        return 42

    def get_js_files(self) -> list[tuple[str, dict[str, str | int]]]:
        """Return test JS files."""
        return [("test.js", {"priority": 100})]

    def get_css_files(self) -> list[str]:
        """Return test CSS files."""
        return ["test.css"]


class TestSearchBackend:
    """Test SearchBackend abstract base class."""

    def test_cannot_instantiate_abstract_class(self) -> None:
        """SearchBackend cannot be instantiated directly."""
        with pytest.raises(TypeError, match="abstract"):
            SearchBackend(None)  # type: ignore[abstract]

    def test_concrete_implementation(self, mock_sphinx_app: MagicMock) -> None:
        """Concrete implementations can be instantiated."""
        backend = ConcreteBackend(mock_sphinx_app)
        assert backend.name == "test"
        assert backend.app is mock_sphinx_app

    def test_index_all_returns_count(self, mock_sphinx_app: MagicMock) -> None:
        """index_all returns document count."""
        backend = ConcreteBackend(mock_sphinx_app)
        assert backend.index_all() == 42

    def test_get_js_files(self, mock_sphinx_app: MagicMock) -> None:
        """get_js_files returns list of tuples."""
        backend = ConcreteBackend(mock_sphinx_app)
        js_files = backend.get_js_files()
        assert js_files == [("test.js", {"priority": 100})]

    def test_get_css_files(self, mock_sphinx_app: MagicMock) -> None:
        """get_css_files returns list of strings."""
        backend = ConcreteBackend(mock_sphinx_app)
        css_files = backend.get_css_files()
        assert css_files == ["test.css"]

    def test_get_config_script_default(self, mock_sphinx_app: MagicMock) -> None:
        """get_config_script returns empty string by default."""
        backend = ConcreteBackend(mock_sphinx_app)
        assert backend.get_config_script() == ""

    def test_is_available_default(self, mock_sphinx_app: MagicMock) -> None:
        """is_available returns True by default."""
        backend = ConcreteBackend(mock_sphinx_app)
        assert backend.is_available() is True
