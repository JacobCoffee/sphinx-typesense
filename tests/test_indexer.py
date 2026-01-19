"""Tests for sphinx-typesense content extraction and indexing.

This module tests:
    - TypesenseIndexer class initialization
    - HTML content extraction
    - Hierarchical document creation
    - Document schema compliance

TODO (Phase 2):
    - Add tests for _extract_documents() HTML parsing
    - Add tests for _create_document() field population
    - Add tests for _get_content_element() theme selection
    - Add tests for index_all() bulk import
    - Add integration tests with Typesense server
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from sphinx_typesense import indexer
from sphinx_typesense.indexer import DOCS_SCHEMA, TypesenseIndexer


class TestIndexerModule:
    """Tests for the indexer module imports and structure."""

    def test_module_imports(self) -> None:
        """Verify the indexer module can be imported."""
        assert indexer is not None

    def test_docs_schema_exists(self) -> None:
        """Verify DOCS_SCHEMA is defined."""
        assert DOCS_SCHEMA is not None
        assert isinstance(DOCS_SCHEMA, dict)

    def test_typesense_indexer_class_exists(self) -> None:
        """Verify TypesenseIndexer class is defined."""
        assert TypesenseIndexer is not None


class TestDocsSchema:
    """Tests for the Typesense document schema."""

    def test_schema_has_name(self) -> None:
        """Verify schema includes collection name."""
        assert "name" in DOCS_SCHEMA
        assert DOCS_SCHEMA["name"] == "sphinx_docs"

    def test_schema_has_fields(self) -> None:
        """Verify schema includes fields list."""
        assert "fields" in DOCS_SCHEMA
        assert isinstance(DOCS_SCHEMA["fields"], list)
        assert len(DOCS_SCHEMA["fields"]) > 0

    def test_schema_has_hierarchy_fields(self) -> None:
        """Verify schema includes hierarchical level fields."""
        field_names = [f["name"] for f in DOCS_SCHEMA["fields"]]
        assert "hierarchy.lvl0" in field_names
        assert "hierarchy.lvl1" in field_names
        assert "hierarchy.lvl2" in field_names
        assert "hierarchy.lvl3" in field_names

    def test_schema_has_content_field(self) -> None:
        """Verify schema includes content field."""
        field_names = [f["name"] for f in DOCS_SCHEMA["fields"]]
        assert "content" in field_names

    def test_schema_has_url_fields(self) -> None:
        """Verify schema includes URL fields."""
        field_names = [f["name"] for f in DOCS_SCHEMA["fields"]]
        assert "url" in field_names
        assert "url_without_anchor" in field_names
        assert "anchor" in field_names

    def test_schema_has_metadata_fields(self) -> None:
        """Verify schema includes metadata fields."""
        field_names = [f["name"] for f in DOCS_SCHEMA["fields"]]
        assert "type" in field_names
        assert "version" in field_names
        assert "language" in field_names

    def test_schema_has_ranking_fields(self) -> None:
        """Verify schema includes ranking fields."""
        field_names = [f["name"] for f in DOCS_SCHEMA["fields"]]
        assert "weight" in field_names
        assert "item_priority" in field_names

    def test_schema_has_default_sorting_field(self) -> None:
        """Verify schema specifies default sorting."""
        assert "default_sorting_field" in DOCS_SCHEMA
        assert DOCS_SCHEMA["default_sorting_field"] == "item_priority"

    def test_schema_has_token_separators(self) -> None:
        """Verify schema includes token separators for code."""
        assert "token_separators" in DOCS_SCHEMA
        assert "_" in DOCS_SCHEMA["token_separators"]
        assert "-" in DOCS_SCHEMA["token_separators"]
        assert "." in DOCS_SCHEMA["token_separators"]


class TestTypesenseIndexer:
    """Tests for the TypesenseIndexer class."""

    def test_indexer_initialization(self, mock_sphinx_app: MagicMock) -> None:
        """Verify indexer can be initialized with Sphinx app."""
        idx = TypesenseIndexer(mock_sphinx_app)
        assert idx.app is mock_sphinx_app
        # Collection name comes from mock config which sets "test_sphinx_docs"
        assert idx.collection_name == "test_sphinx_docs"

    def test_indexer_has_index_all_method(self, mock_sphinx_app: MagicMock) -> None:
        """Verify indexer has index_all method."""
        idx = TypesenseIndexer(mock_sphinx_app)
        assert hasattr(idx, "index_all")
        assert callable(idx.index_all)

    @patch("sphinx_typesense.backends.typesense.TypesenseClient")
    def test_index_all_with_mocked_client(
        self, mock_client_class: MagicMock, mock_sphinx_app: MagicMock, tmp_path: MagicMock
    ) -> None:
        """Verify index_all works with mocked Typesense client."""
        # Set up mock client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_collection = MagicMock()
        mock_client.collections.__getitem__.return_value = mock_collection
        mock_collection.documents.import_.return_value = []

        # Set outdir to empty temp directory
        mock_sphinx_app.outdir = str(tmp_path)

        idx = TypesenseIndexer(mock_sphinx_app)
        count = idx.index_all()

        # With no HTML files, should return 0
        assert count == 0

    def test_indexer_has_client_property(self, mock_sphinx_app: MagicMock) -> None:
        """Verify indexer has client property defined in class."""
        idx = TypesenseIndexer(mock_sphinx_app)
        # Check property exists via class inspection, not via hasattr which triggers getter
        assert "client" in dir(idx)
        assert isinstance(type(idx).__dict__.get("client"), property)

    @patch("sphinx_typesense.backends.typesense.TypesenseClient")
    def test_client_creates_typesense_client(self, mock_client_class: MagicMock, mock_sphinx_app: MagicMock) -> None:
        """Verify client property creates a Typesense client."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        idx = TypesenseIndexer(mock_sphinx_app)
        client = idx.client

        # Should have called TypesenseClient constructor
        mock_client_class.assert_called_once()
        assert client is mock_client

    def test_indexer_has_extract_documents_method(self, mock_sphinx_app: MagicMock) -> None:
        """Verify indexer has _extract_documents method."""
        idx = TypesenseIndexer(mock_sphinx_app)
        assert hasattr(idx, "_extract_documents")

    def test_indexer_has_create_document_method(self, mock_sphinx_app: MagicMock) -> None:
        """Verify indexer has _create_document method."""
        idx = TypesenseIndexer(mock_sphinx_app)
        assert hasattr(idx, "_create_document")

    def test_indexer_has_get_content_element_method(self, mock_sphinx_app: MagicMock) -> None:
        """Verify indexer has _get_content_element method."""
        idx = TypesenseIndexer(mock_sphinx_app)
        assert hasattr(idx, "_get_content_element")


class TestIndexDocumentsEventHandler:
    """Tests for the index_documents Sphinx event handler."""

    def test_index_documents_exists(self) -> None:
        """Verify index_documents function is defined."""
        assert hasattr(indexer, "index_documents")
        assert callable(indexer.index_documents)

    def test_index_documents_handles_exception(self, mock_sphinx_app: MagicMock) -> None:
        """Verify index_documents handles build exceptions gracefully."""
        # Should not raise when exception is passed
        indexer.index_documents(mock_sphinx_app, Exception("Build failed"))

    @patch("sphinx_typesense.indexer.TypesenseBackend")
    def test_index_documents_handles_none_exception(
        self, mock_backend_class: MagicMock, mock_sphinx_app: MagicMock
    ) -> None:
        """Verify index_documents handles successful build (no exception)."""
        # Set up mock backend
        mock_backend = MagicMock()
        mock_backend.index_all.return_value = 0
        mock_backend_class.return_value = mock_backend

        # Should not raise when no exception
        indexer.index_documents(mock_sphinx_app, None)

        # Should have created backend and called index_all
        mock_backend_class.assert_called_once_with(mock_sphinx_app)
        mock_backend.index_all.assert_called_once()

    @patch("sphinx_typesense.indexer.TypesenseIndexer")
    def test_index_documents_skips_when_disabled(
        self, mock_indexer_class: MagicMock, mock_sphinx_app: MagicMock
    ) -> None:
        """Verify index_documents skips indexing when disabled."""
        mock_sphinx_app.config.typesense_enable_indexing = False

        indexer.index_documents(mock_sphinx_app, None)

        # Should not have created indexer
        mock_indexer_class.assert_not_called()

    @patch("sphinx_typesense.indexer.TypesenseIndexer")
    def test_index_documents_skips_when_no_api_key(
        self, mock_indexer_class: MagicMock, mock_sphinx_app: MagicMock
    ) -> None:
        """Verify index_documents skips indexing when no API key."""
        mock_sphinx_app.config.typesense_api_key = ""

        indexer.index_documents(mock_sphinx_app, None)

        # Should not have created indexer
        mock_indexer_class.assert_not_called()


# =============================================================================
# TODO (Phase 2): Tests to implement
# =============================================================================
#
# class TestContentExtraction:
#     """Tests for HTML content extraction."""
#
#     def test_extract_h1_heading(self, sample_html_content):
#         """Verify H1 headings are extracted as lvl0."""
#         pass
#
#     def test_extract_h2_heading(self, sample_html_content):
#         """Verify H2 headings are extracted as lvl1."""
#         pass
#
#     def test_extract_h3_heading(self, sample_html_content):
#         """Verify H3 headings are extracted as lvl2."""
#         pass
#
#     def test_extract_paragraphs(self, sample_html_content):
#         """Verify paragraphs are extracted as content."""
#         pass
#
#     def test_extract_list_items(self, sample_html_content):
#         """Verify list items are extracted as content."""
#         pass
#
#     def test_hierarchy_inheritance(self, sample_html_content):
#         """Verify content inherits heading hierarchy."""
#         pass
#
#
# class TestDocumentCreation:
#     """Tests for Typesense document creation."""
#
#     def test_document_has_unique_id(self):
#         """Verify documents have unique IDs."""
#         pass
#
#     def test_document_url_with_anchor(self):
#         """Verify URLs include anchor for headings."""
#         pass
#
#     def test_document_weights(self):
#         """Verify correct weights for document types."""
#         pass
#
#
# @pytest.mark.integration
# class TestTypesenseIntegration:
#     """Integration tests requiring Typesense server."""
#
#     def test_create_collection(self, typesense_server):
#         """Verify collection creation with schema."""
#         pass
#
#     def test_bulk_import_documents(self, typesense_server):
#         """Verify bulk document import."""
#         pass
#
#     def test_search_indexed_documents(self, typesense_server):
#         """Verify indexed documents are searchable."""
#         pass
