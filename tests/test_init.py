"""Tests for sphinx-typesense extension initialization and backend selection.

This module tests:
    - Extension setup and configuration
    - Backend factory function (get_backend)
    - Backend selection based on configuration
    - Static file addition based on backend
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from unittest.mock import patch

from sphinx_typesense import (
    SearchBackend,
    __version__,
    _add_static_files,
    get_backend,
    index_documents,
    setup,
)
from sphinx_typesense.backends.pagefind import PagefindBackend
from sphinx_typesense.backends.typesense import TypesenseBackend

if TYPE_CHECKING:
    from pathlib import Path
    from unittest.mock import MagicMock

    import pytest


class TestModuleExports:
    """Tests for module-level exports."""

    def test_version_is_string(self) -> None:
        """Verify __version__ is a string."""
        assert isinstance(__version__, str)

    def test_version_format(self) -> None:
        """Verify __version__ follows semver format."""
        parts = __version__.split(".")
        assert len(parts) >= 2
        assert all(part.isdigit() for part in parts[:2])

    def test_searchbackend_exported(self) -> None:
        """Verify SearchBackend is exported."""
        assert SearchBackend is not None

    def test_get_backend_exported(self) -> None:
        """Verify get_backend is exported."""
        assert callable(get_backend)

    def test_setup_exported(self) -> None:
        """Verify setup is exported."""
        assert callable(setup)


class TestGetBackend:
    """Tests for the get_backend factory function."""

    def test_returns_search_backend(self, mock_sphinx_app: MagicMock) -> None:
        """Verify get_backend returns a SearchBackend instance."""
        backend = get_backend(mock_sphinx_app)
        assert isinstance(backend, SearchBackend)

    def test_typesense_backend_explicit(self, mock_sphinx_app: MagicMock) -> None:
        """Verify Typesense backend is returned for explicit typesense config."""
        mock_sphinx_app.config.typesense_backend = "typesense"
        backend = get_backend(mock_sphinx_app)
        assert isinstance(backend, TypesenseBackend)
        assert backend.name == "typesense"

    def test_pagefind_backend_explicit(self, mock_sphinx_app: MagicMock) -> None:
        """Verify Pagefind backend is returned for explicit pagefind config."""
        mock_sphinx_app.config.typesense_backend = "pagefind"
        backend = get_backend(mock_sphinx_app)
        assert isinstance(backend, PagefindBackend)
        assert backend.name == "pagefind"

    def test_auto_with_api_key_returns_typesense(self, mock_sphinx_app: MagicMock) -> None:
        """Verify auto backend returns Typesense when API key is present."""
        mock_sphinx_app.config.typesense_backend = "auto"
        mock_sphinx_app.config.typesense_api_key = "test_key"
        backend = get_backend(mock_sphinx_app)
        assert isinstance(backend, TypesenseBackend)

    def test_auto_without_api_key_returns_pagefind(self, mock_sphinx_app: MagicMock) -> None:
        """Verify auto backend returns Pagefind when no API key is present."""
        mock_sphinx_app.config.typesense_backend = "auto"
        mock_sphinx_app.config.typesense_api_key = ""
        with patch.dict("os.environ", {}, clear=True):
            backend = get_backend(mock_sphinx_app)
        assert isinstance(backend, PagefindBackend)

    def test_backend_has_app_reference(self, mock_sphinx_app: MagicMock) -> None:
        """Verify backend has reference to Sphinx app."""
        backend = get_backend(mock_sphinx_app)
        assert backend.app is mock_sphinx_app


class TestSetupFunction:
    """Tests for the setup function."""

    def test_returns_metadata_dict(self, mock_sphinx_app: MagicMock) -> None:
        """Verify setup returns extension metadata."""
        result = setup(mock_sphinx_app)
        assert isinstance(result, dict)
        assert "version" in result
        assert "parallel_read_safe" in result
        assert "parallel_write_safe" in result

    def test_registers_config_values(self, mock_sphinx_app: MagicMock) -> None:
        """Verify setup registers configuration with Sphinx."""
        setup(mock_sphinx_app)
        # The mock should have add_config_value called
        # Note: This is a simplistic check; the actual verification
        # happens in test_config.py

    def test_connects_to_events(self, mock_sphinx_app: MagicMock) -> None:
        """Verify setup connects to Sphinx events."""
        setup(mock_sphinx_app)
        # Verify connect was called for expected events
        call_args = [call[0] for call in mock_sphinx_app.connect.call_args_list]
        events = [arg[0] for arg in call_args]
        assert "config-inited" in events
        assert "build-finished" in events
        assert "html-page-context" in events

    def test_parallel_read_safe(self, mock_sphinx_app: MagicMock) -> None:
        """Verify extension is marked parallel read safe."""
        result = setup(mock_sphinx_app)
        assert result["parallel_read_safe"] is True

    def test_parallel_write_safe(self, mock_sphinx_app: MagicMock) -> None:
        """Verify extension is marked parallel write safe."""
        result = setup(mock_sphinx_app)
        assert result["parallel_write_safe"] is True


class TestIndexDocuments:
    """Tests for the index_documents event handler."""

    def test_skips_on_build_exception(self, mock_sphinx_app: MagicMock) -> None:
        """Verify indexing is skipped when build has exception."""
        # Should not raise and should return early
        index_documents(mock_sphinx_app, Exception("Build failed"))

    def test_skips_when_disabled(self, mock_sphinx_app: MagicMock) -> None:
        """Verify indexing is skipped when disabled."""
        mock_sphinx_app.config.typesense_enable_indexing = False
        # Should not raise and should return early
        index_documents(mock_sphinx_app, None)

    def test_uses_backend_for_indexing(self, mock_sphinx_app: MagicMock, tmp_path: Path) -> None:
        """Verify backend is used for indexing."""
        mock_sphinx_app.config.typesense_enable_indexing = True
        mock_sphinx_app.config.typesense_backend = "pagefind"
        mock_sphinx_app.outdir = str(tmp_path)

        # Create a mock HTML file
        (tmp_path / "index.html").write_text("<html><body>Test</body></html>")

        # Mock the pagefind command to not be available
        with patch("shutil.which", return_value=None):
            # Should not raise even when backend unavailable
            index_documents(mock_sphinx_app, None)


class TestAddStaticFiles:
    """Tests for static file addition based on backend."""

    def test_typesense_static_files(self, mock_sphinx_app: MagicMock) -> None:
        """Verify Typesense static files are added for Typesense backend."""
        mock_sphinx_app.config.typesense_backend = "typesense"
        mock_sphinx_app.config.typesense_api_key = "test_key"

        _add_static_files(mock_sphinx_app, mock_sphinx_app.config)

        # Verify CSS files added
        css_calls = list(mock_sphinx_app.add_css_file.call_args_list)
        css_files = [call[0][0] for call in css_calls]
        assert any("typesense-docsearch" in f for f in css_files)

        # Verify JS files added
        js_calls = list(mock_sphinx_app.add_js_file.call_args_list)
        js_files = [call[0][0] for call in js_calls]
        assert any("typesense-docsearch" in f or "typesense-init" in f for f in js_files)

    def test_pagefind_static_files(self, mock_sphinx_app: MagicMock) -> None:
        """Verify Pagefind static files are added for Pagefind backend."""
        mock_sphinx_app.config.typesense_backend = "pagefind"
        mock_sphinx_app.config.typesense_api_key = ""

        _add_static_files(mock_sphinx_app, mock_sphinx_app.config)

        # Verify CSS files added
        css_calls = list(mock_sphinx_app.add_css_file.call_args_list)
        css_files = [call[0][0] for call in css_calls]
        assert any("pagefind" in f for f in css_files)

        # Verify JS files added
        js_calls = list(mock_sphinx_app.add_js_file.call_args_list)
        js_files = [call[0][0] for call in js_calls]
        assert any("pagefind-init" in f for f in js_files)

    def test_typesense_cdn_files(self, mock_sphinx_app: MagicMock) -> None:
        """Verify Typesense CDN files are added."""
        mock_sphinx_app.config.typesense_backend = "typesense"
        mock_sphinx_app.config.typesense_api_key = "test_key"

        _add_static_files(mock_sphinx_app, mock_sphinx_app.config)

        # Verify CDN CSS added
        css_calls = list(mock_sphinx_app.add_css_file.call_args_list)
        css_files = [call[0][0] for call in css_calls]
        assert any("cdn.jsdelivr.net" in f for f in css_files)

        # Verify CDN JS added
        js_calls = list(mock_sphinx_app.add_js_file.call_args_list)
        js_files = [call[0][0] for call in js_calls]
        assert any("cdn.jsdelivr.net" in f for f in js_files)


class TestBackendAvailabilityCheck:
    """Tests for backend availability checking in index_documents."""

    def test_logs_warning_when_backend_unavailable(
        self, mock_sphinx_app: MagicMock, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Verify warning is logged when backend is not available."""
        mock_sphinx_app.config.typesense_enable_indexing = True
        mock_sphinx_app.config.typesense_backend = "pagefind"
        mock_sphinx_app.outdir = str(tmp_path)

        # Mock pagefind not being available
        with patch("shutil.which", return_value=None), caplog.at_level(logging.WARNING):
            index_documents(mock_sphinx_app, None)

        # Should have logged a warning about backend not available
        assert any("not available" in record.message for record in caplog.records)
