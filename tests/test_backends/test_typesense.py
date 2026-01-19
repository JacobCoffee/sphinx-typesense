"""Tests for TypesenseBackend implementation."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

if TYPE_CHECKING:
    from pathlib import Path

from sphinx_typesense.backends.typesense import (
    DOC_TYPE_PRIORITIES,
    DOC_TYPE_WEIGHTS,
    DOCS_SCHEMA,
    TypesenseBackend,
)


class TestTypesenseBackendBasics:
    """Test TypesenseBackend basic properties and interface compliance."""

    def test_backend_name_is_typesense(self, mock_sphinx_app: MagicMock) -> None:
        """TypesenseBackend.name should be 'typesense'."""
        backend = TypesenseBackend(mock_sphinx_app)
        assert backend.name == "typesense"

    def test_backend_has_app_reference(self, mock_sphinx_app: MagicMock) -> None:
        """Backend should store reference to Sphinx app."""
        backend = TypesenseBackend(mock_sphinx_app)
        assert backend.app is mock_sphinx_app

    def test_backend_has_collection_name(self, mock_sphinx_app: MagicMock) -> None:
        """Backend should have collection_name from config."""
        backend = TypesenseBackend(mock_sphinx_app)
        assert backend.collection_name == "test_sphinx_docs"

    def test_backend_inherits_from_search_backend(self, mock_sphinx_app: MagicMock) -> None:
        """TypesenseBackend should inherit from SearchBackend."""
        from sphinx_typesense.backends.base import SearchBackend  # noqa: PLC0415

        backend = TypesenseBackend(mock_sphinx_app)
        assert isinstance(backend, SearchBackend)


class TestTypesenseBackendJSFiles:
    """Test get_js_files() method."""

    def test_get_js_files_returns_list(self, mock_sphinx_app: MagicMock) -> None:
        """get_js_files should return a list."""
        backend = TypesenseBackend(mock_sphinx_app)
        js_files = backend.get_js_files()
        assert isinstance(js_files, list)

    def test_get_js_files_contains_docsearch_js(self, mock_sphinx_app: MagicMock) -> None:
        """get_js_files should include typesense-docsearch.js."""
        backend = TypesenseBackend(mock_sphinx_app)
        js_files = backend.get_js_files()
        filenames = [f[0] for f in js_files]
        assert "typesense-docsearch.js" in filenames

    def test_get_js_files_contains_init_js(self, mock_sphinx_app: MagicMock) -> None:
        """get_js_files should include typesense-init.js."""
        backend = TypesenseBackend(mock_sphinx_app)
        js_files = backend.get_js_files()
        filenames = [f[0] for f in js_files]
        assert "typesense-init.js" in filenames

    def test_get_js_files_has_priority_attributes(self, mock_sphinx_app: MagicMock) -> None:
        """JS files should have priority attributes."""
        backend = TypesenseBackend(mock_sphinx_app)
        js_files = backend.get_js_files()
        for _filename, attrs in js_files:
            assert "priority" in attrs
            assert isinstance(attrs["priority"], int)

    def test_get_js_files_correct_load_order(self, mock_sphinx_app: MagicMock) -> None:
        """init.js should load after docsearch.js (higher priority number)."""
        backend = TypesenseBackend(mock_sphinx_app)
        js_files = backend.get_js_files()
        files_by_name = {f[0]: f[1] for f in js_files}
        assert files_by_name["typesense-init.js"]["priority"] > files_by_name["typesense-docsearch.js"]["priority"]


class TestTypesenseBackendCSSFiles:
    """Test get_css_files() method."""

    def test_get_css_files_returns_list(self, mock_sphinx_app: MagicMock) -> None:
        """get_css_files should return a list."""
        backend = TypesenseBackend(mock_sphinx_app)
        css_files = backend.get_css_files()
        assert isinstance(css_files, list)

    def test_get_css_files_contains_docsearch_css(self, mock_sphinx_app: MagicMock) -> None:
        """get_css_files should include typesense-docsearch.css."""
        backend = TypesenseBackend(mock_sphinx_app)
        css_files = backend.get_css_files()
        assert "typesense-docsearch.css" in css_files


class TestTypesenseBackendConfigScript:
    """Test get_config_script() method."""

    def test_get_config_script_returns_string(self, mock_sphinx_app: MagicMock) -> None:
        """get_config_script should return a string."""
        backend = TypesenseBackend(mock_sphinx_app)
        script = backend.get_config_script()
        assert isinstance(script, str)

    def test_get_config_script_sets_window_variable(self, mock_sphinx_app: MagicMock) -> None:
        """Config script should set window.TYPESENSE_CONFIG."""
        backend = TypesenseBackend(mock_sphinx_app)
        script = backend.get_config_script()
        assert "window.TYPESENSE_CONFIG" in script

    def test_get_config_script_is_valid_js(self, mock_sphinx_app: MagicMock) -> None:
        """Config script should produce valid JSON in the config object."""
        backend = TypesenseBackend(mock_sphinx_app)
        script = backend.get_config_script()
        # Extract JSON part from "window.TYPESENSE_CONFIG = {...};"
        json_str = script.replace("window.TYPESENSE_CONFIG = ", "").rstrip(";")
        config = json.loads(json_str)
        assert isinstance(config, dict)

    def test_get_config_script_contains_collection_name(self, mock_sphinx_app: MagicMock) -> None:
        """Config should include collection name."""
        backend = TypesenseBackend(mock_sphinx_app)
        script = backend.get_config_script()
        json_str = script.replace("window.TYPESENSE_CONFIG = ", "").rstrip(";")
        config = json.loads(json_str)
        assert config["collectionName"] == "test_sphinx_docs"

    def test_get_config_script_contains_host_settings(self, mock_sphinx_app: MagicMock) -> None:
        """Config should include host, port, and protocol."""
        backend = TypesenseBackend(mock_sphinx_app)
        script = backend.get_config_script()
        json_str = script.replace("window.TYPESENSE_CONFIG = ", "").rstrip(";")
        config = json.loads(json_str)
        assert config["host"] == "localhost"
        assert config["port"] == "8108"
        assert config["protocol"] == "http"

    def test_get_config_script_contains_search_api_key(self, mock_sphinx_app: MagicMock) -> None:
        """Config should include search API key (not admin key)."""
        backend = TypesenseBackend(mock_sphinx_app)
        script = backend.get_config_script()
        json_str = script.replace("window.TYPESENSE_CONFIG = ", "").rstrip(";")
        config = json.loads(json_str)
        assert config["apiKey"] == "test_search_key"


class TestTypesenseBackendSchema:
    """Test schema and constants are exported correctly."""

    def test_docs_schema_exists(self) -> None:
        """DOCS_SCHEMA should be defined."""
        assert DOCS_SCHEMA is not None
        assert isinstance(DOCS_SCHEMA, dict)

    def test_doc_type_weights_exists(self) -> None:
        """DOC_TYPE_WEIGHTS should be defined."""
        assert DOC_TYPE_WEIGHTS is not None
        assert isinstance(DOC_TYPE_WEIGHTS, dict)

    def test_doc_type_priorities_exists(self) -> None:
        """DOC_TYPE_PRIORITIES should be defined."""
        assert DOC_TYPE_PRIORITIES is not None
        assert isinstance(DOC_TYPE_PRIORITIES, dict)

    def test_weights_have_expected_types(self) -> None:
        """Weights should exist for lvl0-3 and content."""
        expected_types = ["lvl0", "lvl1", "lvl2", "lvl3", "content"]
        for doc_type in expected_types:
            assert doc_type in DOC_TYPE_WEIGHTS
            assert isinstance(DOC_TYPE_WEIGHTS[doc_type], int)

    def test_priorities_have_expected_types(self) -> None:
        """Priorities should exist for lvl0-3 and content."""
        expected_types = ["lvl0", "lvl1", "lvl2", "lvl3", "content"]
        for doc_type in expected_types:
            assert doc_type in DOC_TYPE_PRIORITIES
            assert isinstance(DOC_TYPE_PRIORITIES[doc_type], int)


class TestTypesenseBackendClient:
    """Test client creation and management."""

    def test_client_property_exists(self, mock_sphinx_app: MagicMock) -> None:
        """Backend should have client property."""
        backend = TypesenseBackend(mock_sphinx_app)
        assert hasattr(backend, "client")
        assert isinstance(type(backend).__dict__.get("client"), property)

    @patch("sphinx_typesense.backends.typesense.TypesenseClient")
    def test_client_creates_typesense_client(self, mock_client_class: MagicMock, mock_sphinx_app: MagicMock) -> None:
        """Client property should create a Typesense client."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        backend = TypesenseBackend(mock_sphinx_app)
        client = backend.client

        mock_client_class.assert_called_once()
        assert client is mock_client

    @patch("sphinx_typesense.backends.typesense.TypesenseClient")
    def test_client_is_cached(self, mock_client_class: MagicMock, mock_sphinx_app: MagicMock) -> None:
        """Client should be created only once (cached)."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        backend = TypesenseBackend(mock_sphinx_app)
        client1 = backend.client
        client2 = backend.client

        # Should only be called once
        mock_client_class.assert_called_once()
        assert client1 is client2


class TestTypesenseBackendIndexAll:
    """Test index_all() method."""

    def test_index_all_method_exists(self, mock_sphinx_app: MagicMock) -> None:
        """Backend should have index_all method."""
        backend = TypesenseBackend(mock_sphinx_app)
        assert hasattr(backend, "index_all")
        assert callable(backend.index_all)

    @patch("sphinx_typesense.backends.typesense.TypesenseClient")
    def test_index_all_returns_zero_when_server_unavailable(
        self, mock_client_class: MagicMock, mock_sphinx_app: MagicMock, tmp_path: Path
    ) -> None:
        """index_all should return 0 when server is unavailable."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        # Simulate connection failure
        mock_client.operations.is_healthy.return_value = False

        mock_sphinx_app.outdir = str(tmp_path)

        backend = TypesenseBackend(mock_sphinx_app)
        count = backend.index_all()

        assert count == 0

    @patch("sphinx_typesense.backends.typesense.TypesenseClient")
    def test_index_all_returns_zero_for_empty_directory(
        self, mock_client_class: MagicMock, mock_sphinx_app: MagicMock, tmp_path: Path
    ) -> None:
        """index_all should return 0 when no HTML files exist."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.operations.is_healthy.return_value = True
        mock_collection = MagicMock()
        mock_client.collections.__getitem__.return_value = mock_collection
        mock_collection.documents.import_.return_value = []

        mock_sphinx_app.outdir = str(tmp_path)

        backend = TypesenseBackend(mock_sphinx_app)
        count = backend.index_all()

        assert count == 0


class TestTypesenseBackendIsAvailable:
    """Test is_available() method."""

    def test_is_available_method_exists(self, mock_sphinx_app: MagicMock) -> None:
        """Backend should have is_available method."""
        backend = TypesenseBackend(mock_sphinx_app)
        assert hasattr(backend, "is_available")
        assert callable(backend.is_available)

    @patch("sphinx_typesense.backends.typesense.TypesenseClient")
    def test_is_available_returns_true_when_healthy(
        self, mock_client_class: MagicMock, mock_sphinx_app: MagicMock
    ) -> None:
        """is_available should return True when server is healthy."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.operations.is_healthy.return_value = True

        backend = TypesenseBackend(mock_sphinx_app)
        result = backend.is_available()

        assert result is True

    @patch("sphinx_typesense.backends.typesense.TypesenseClient")
    def test_is_available_returns_false_when_unhealthy(
        self, mock_client_class: MagicMock, mock_sphinx_app: MagicMock
    ) -> None:
        """is_available should return False when server is unhealthy."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.operations.is_healthy.return_value = False

        backend = TypesenseBackend(mock_sphinx_app)
        result = backend.is_available()

        assert result is False


class TestBackwardCompatibility:
    """Test backward compatibility with TypesenseIndexer alias."""

    def test_typesense_indexer_alias_exists(self) -> None:
        """TypesenseIndexer should be importable from indexer module."""
        from sphinx_typesense.indexer import TypesenseIndexer  # noqa: PLC0415

        assert TypesenseIndexer is not None

    def test_typesense_indexer_is_typesense_backend(self) -> None:
        """TypesenseIndexer should be the same as TypesenseBackend."""
        from sphinx_typesense.indexer import TypesenseIndexer  # noqa: PLC0415

        assert TypesenseIndexer is TypesenseBackend

    def test_docs_schema_importable_from_indexer(self) -> None:
        """DOCS_SCHEMA should be importable from indexer module."""
        from sphinx_typesense.indexer import DOCS_SCHEMA as SCHEMA  # noqa: PLC0415

        assert SCHEMA is DOCS_SCHEMA

    def test_weights_importable_from_indexer(self) -> None:
        """DOC_TYPE_WEIGHTS should be importable from indexer module."""
        from sphinx_typesense.indexer import DOC_TYPE_WEIGHTS as WEIGHTS  # noqa: PLC0415

        assert WEIGHTS is DOC_TYPE_WEIGHTS

    def test_priorities_importable_from_indexer(self) -> None:
        """DOC_TYPE_PRIORITIES should be importable from indexer module."""
        from sphinx_typesense.indexer import DOC_TYPE_PRIORITIES as PRIORITIES  # noqa: PLC0415

        assert PRIORITIES is DOC_TYPE_PRIORITIES

    def test_index_documents_function_exists(self) -> None:
        """index_documents function should be importable from indexer module."""
        from sphinx_typesense.indexer import index_documents  # noqa: PLC0415

        assert index_documents is not None
        assert callable(index_documents)
