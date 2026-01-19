"""Integration tests for sphinx-typesense with a live Typesense server.

This module provides integration tests that require a running Typesense server.
All tests are marked with @pytest.mark.integration and will be skipped if
Typesense is not available at localhost:8108.

Requirements:
    - Typesense server running at localhost:8108
    - API key: xyz (default development key)

Run integration tests::

    pytest -m integration tests/test_integration.py

Skip integration tests::

    pytest -m "not integration"

"""

from __future__ import annotations

import contextlib
from pathlib import Path
from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock

import pytest
from typesense import Client as TypesenseClient
from typesense.exceptions import HTTPStatus0Error, ObjectNotFound, RequestUnauthorized

from sphinx_typesense.indexer import DOCS_SCHEMA, TypesenseIndexer

if TYPE_CHECKING:
    from collections.abc import Generator


# =============================================================================
# Connection Check
# =============================================================================


def _typesense_available() -> bool:
    """Check if Typesense server is available at localhost:8108.

    Returns:
        True if server is reachable and healthy, False otherwise.

    """
    try:
        client = TypesenseClient(
            {
                "nodes": [{"host": "localhost", "port": "8108", "protocol": "http"}],
                "api_key": "xyz",
                "connection_timeout_seconds": 2,
            }
        )
        return client.operations.is_healthy()
    except (OSError, HTTPStatus0Error, TimeoutError):
        return False


# Skip all tests in this module if Typesense is not available
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not _typesense_available(), reason="Typesense server not available at localhost:8108"),
]


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def typesense_client() -> Generator[TypesenseClient, None, None]:
    """Create a Typesense client connected to localhost:8108.

    Yields:
        Configured TypesenseClient instance.

    """
    return TypesenseClient(
        {
            "nodes": [{"host": "localhost", "port": "8108", "protocol": "http"}],
            "api_key": "xyz",
            "connection_timeout_seconds": 10,
        }
    )


@pytest.fixture
def test_collection_name() -> str:
    """Provide a unique collection name for testing.

    Returns:
        Collection name string.

    """
    return "test_sphinx_integration"


@pytest.fixture
def test_collection(
    typesense_client: TypesenseClient,
    test_collection_name: str,
) -> Generator[str, None, None]:
    """Create a test collection and clean up after tests.

    This fixture creates a Typesense collection using the DOCS_SCHEMA
    and deletes it after the test completes.

    Args:
        typesense_client: Typesense client fixture.
        test_collection_name: Name for the test collection.

    Yields:
        The collection name.

    """
    # Clean up any existing collection
    with contextlib.suppress(ObjectNotFound):
        typesense_client.collections[test_collection_name].delete()

    # Create collection with DOCS_SCHEMA
    schema = DOCS_SCHEMA.copy()
    schema["name"] = test_collection_name
    typesense_client.collections.create(schema)  # type: ignore[arg-type]

    yield test_collection_name

    # Cleanup: delete collection after test
    with contextlib.suppress(ObjectNotFound):
        typesense_client.collections[test_collection_name].delete()


@pytest.fixture
def integration_sphinx_app(test_collection_name: str, tmp_path: Path) -> MagicMock:
    """Create a mock Sphinx app configured for integration testing.

    Args:
        test_collection_name: Collection name for the test.
        tmp_path: Temporary directory for output.

    Returns:
        MagicMock configured as a Sphinx application.

    """
    app = MagicMock(spec=["config", "outdir", "srcdir", "builder", "env"])

    app.config = MagicMock()
    app.config.typesense_host = "localhost"
    app.config.typesense_port = "8108"
    app.config.typesense_protocol = "http"
    app.config.typesense_api_key = "xyz"
    app.config.typesense_search_api_key = "xyz"
    app.config.typesense_collection_name = test_collection_name
    app.config.typesense_doc_version = ""
    app.config.typesense_placeholder = "Search documentation..."
    app.config.typesense_num_typos = 2
    app.config.typesense_per_page = 10
    app.config.typesense_container = "#typesense-search"
    app.config.typesense_filter_by = ""
    app.config.typesense_content_selectors = None
    app.config.typesense_enable_indexing = True
    app.config.typesense_drop_existing = False
    app.config.typesense_connection_timeout = 10
    app.config.language = "en"
    app.config.html_theme = "alabaster"
    app.outdir = str(tmp_path)

    return app


@pytest.fixture
def sample_document() -> dict[str, Any]:
    """Provide a sample document matching DOCS_SCHEMA.

    Returns:
        Document dictionary ready for indexing.

    """
    return {
        "id": "test_doc_001",
        "hierarchy.lvl0": "Getting Started",
        "hierarchy.lvl1": "Installation",
        "hierarchy.lvl2": "",
        "hierarchy.lvl3": "",
        "content": "Install sphinx-typesense using pip install sphinx-typesense",
        "url": "getting-started.html#installation",
        "url_without_anchor": "getting-started.html",
        "anchor": "installation",
        "type": "content",
        "version": "1.0",
        "language": "en",
        "weight": 50,
        "item_priority": 50,
    }


@pytest.fixture
def sample_html_file(tmp_path: Path) -> Path:
    """Create a sample HTML file for indexing tests.

    Args:
        tmp_path: Temporary directory fixture.

    Returns:
        Path to the created HTML file.

    """
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Test Documentation</title>
</head>
<body>
    <div class="body">
        <h1 id="getting-started">Getting Started</h1>
        <p>Welcome to the sphinx-typesense documentation.</p>

        <h2 id="installation">Installation</h2>
        <p>Install the package using pip:</p>
        <pre><code>pip install sphinx-typesense</code></pre>

        <h3 id="requirements">Requirements</h3>
        <p>Python 3.9 or higher is required.</p>
        <ul>
            <li>Python 3.9+</li>
            <li>Sphinx 7.0+</li>
            <li>Typesense server</li>
        </ul>

        <h2 id="configuration">Configuration</h2>
        <p>Add sphinx-typesense to your extensions list in conf.py.</p>
    </div>
</body>
</html>"""

    html_file = tmp_path / "index.html"
    html_file.write_text(html_content)
    return html_file


@pytest.fixture
def multiple_html_files(tmp_path: Path) -> Path:
    """Create multiple HTML files for bulk indexing tests.

    Args:
        tmp_path: Temporary directory fixture.

    Returns:
        Path to the directory containing HTML files.

    """
    # Create index.html
    index_html = """<!DOCTYPE html>
<html lang="en">
<head><title>Index</title></head>
<body>
    <div class="body">
        <h1 id="welcome">Welcome</h1>
        <p>Welcome to the documentation.</p>
    </div>
</body>
</html>"""
    (tmp_path / "index.html").write_text(index_html)

    # Create api.html
    api_html = """<!DOCTYPE html>
<html lang="en">
<head><title>API Reference</title></head>
<body>
    <div class="body">
        <h1 id="api-reference">API Reference</h1>
        <p>This section documents the API.</p>
        <h2 id="classes">Classes</h2>
        <p>Available classes and their methods.</p>
    </div>
</body>
</html>"""
    (tmp_path / "api.html").write_text(api_html)

    # Create guide.html
    guide_html = """<!DOCTYPE html>
<html lang="en">
<head><title>User Guide</title></head>
<body>
    <div class="body">
        <h1 id="user-guide">User Guide</h1>
        <p>A comprehensive guide to using the library.</p>
        <h2 id="basics">Basics</h2>
        <p>Start with the basics.</p>
        <h2 id="advanced">Advanced Topics</h2>
        <p>Move on to advanced usage patterns.</p>
    </div>
</body>
</html>"""
    (tmp_path / "guide.html").write_text(guide_html)

    return tmp_path


# =============================================================================
# Connection and Collection Management Tests
# =============================================================================


class TestTypesenseConnection:
    """Tests for Typesense server connection."""

    def test_client_connects_successfully(self, typesense_client: TypesenseClient) -> None:
        """Verify client can connect to Typesense server."""
        assert typesense_client.operations.is_healthy() is True

    def test_client_health_check(self, typesense_client: TypesenseClient) -> None:
        """Verify health check endpoint works."""
        health = typesense_client.operations.is_healthy()
        assert health is True


class TestCollectionManagement:
    """Tests for Typesense collection creation and management."""

    def test_create_collection_with_docs_schema(
        self,
        typesense_client: TypesenseClient,
    ) -> None:
        """Verify collection creation with DOCS_SCHEMA."""
        collection_name = "test_schema_creation"

        # Clean up if exists
        with contextlib.suppress(ObjectNotFound):
            typesense_client.collections[collection_name].delete()

        # Create collection
        schema = DOCS_SCHEMA.copy()
        schema["name"] = collection_name

        result = typesense_client.collections.create(schema)  # type: ignore[arg-type]

        assert result["name"] == collection_name
        assert "fields" in result

        # Verify field names
        field_names = [f["name"] for f in result["fields"]]
        assert "hierarchy.lvl0" in field_names
        assert "hierarchy.lvl1" in field_names
        assert "content" in field_names
        assert "url" in field_names
        assert "weight" in field_names

        # Cleanup
        typesense_client.collections[collection_name].delete()

    def test_drop_and_recreate_collection(
        self,
        typesense_client: TypesenseClient,
    ) -> None:
        """Verify collection can be dropped and recreated."""
        collection_name = "test_drop_recreate"

        # Create initial collection
        schema = DOCS_SCHEMA.copy()
        schema["name"] = collection_name

        with contextlib.suppress(ObjectNotFound):
            typesense_client.collections[collection_name].delete()

        typesense_client.collections.create(schema)  # type: ignore[arg-type]

        # Add a document
        doc = {
            "id": "test_doc",
            "hierarchy.lvl0": "Test",
            "hierarchy.lvl1": "",
            "hierarchy.lvl2": "",
            "hierarchy.lvl3": "",
            "content": "Test content",
            "url": "test.html",
            "url_without_anchor": "test.html",
            "anchor": "",
            "type": "content",
            "version": "",
            "language": "en",
            "weight": 50,
            "item_priority": 50,
        }
        typesense_client.collections[collection_name].documents.create(doc)

        # Drop collection
        typesense_client.collections[collection_name].delete()

        # Verify it's gone
        with pytest.raises(ObjectNotFound):
            typesense_client.collections[collection_name].retrieve()

        # Recreate
        typesense_client.collections.create(schema)  # type: ignore[arg-type]

        # Verify it's empty
        result = typesense_client.collections[collection_name].retrieve()
        assert result["num_documents"] == 0

        # Cleanup
        typesense_client.collections[collection_name].delete()

    def test_retrieve_collection_info(
        self,
        typesense_client: TypesenseClient,
        test_collection: str,
    ) -> None:
        """Verify collection information can be retrieved."""
        result = typesense_client.collections[test_collection].retrieve()

        assert result["name"] == test_collection
        assert "num_documents" in result
        assert "fields" in result


# =============================================================================
# Document Indexing Tests
# =============================================================================


class TestDocumentIndexing:
    """Tests for document indexing operations."""

    def test_index_single_document(
        self,
        typesense_client: TypesenseClient,
        test_collection: str,
        sample_document: dict[str, Any],
    ) -> None:
        """Verify single document can be indexed."""
        result = typesense_client.collections[test_collection].documents.create(sample_document)

        assert result["id"] == sample_document["id"]
        assert result["hierarchy.lvl0"] == sample_document["hierarchy.lvl0"]
        assert result["content"] == sample_document["content"]

    def test_index_single_html_file(
        self,
        integration_sphinx_app: MagicMock,
        sample_html_file: Path,
        typesense_client: TypesenseClient,
        test_collection_name: str,
    ) -> None:
        """Verify single HTML file can be indexed."""
        # Set up app with HTML file directory
        integration_sphinx_app.outdir = str(sample_html_file.parent)
        integration_sphinx_app.config.typesense_collection_name = test_collection_name
        integration_sphinx_app.config.typesense_drop_existing = True

        indexer = TypesenseIndexer(integration_sphinx_app)
        count = indexer.index_all()

        # Should have indexed multiple documents from the HTML
        assert count > 0

        # Verify documents are in collection
        collection_info = typesense_client.collections[test_collection_name].retrieve()
        assert collection_info["num_documents"] > 0

    def test_bulk_index_multiple_html_files(
        self,
        integration_sphinx_app: MagicMock,
        multiple_html_files: Path,
        typesense_client: TypesenseClient,
        test_collection_name: str,
    ) -> None:
        """Verify multiple HTML files can be bulk indexed."""
        integration_sphinx_app.outdir = str(multiple_html_files)
        integration_sphinx_app.config.typesense_collection_name = test_collection_name
        integration_sphinx_app.config.typesense_drop_existing = True

        indexer = TypesenseIndexer(integration_sphinx_app)
        count = indexer.index_all()

        # Should have indexed documents from all 3 HTML files
        assert count > 0

        # Verify collection has documents
        collection_info = typesense_client.collections[test_collection_name].retrieve()
        assert collection_info["num_documents"] == count

    def test_document_upsert_behavior(
        self,
        typesense_client: TypesenseClient,
        test_collection: str,
        sample_document: dict[str, Any],
    ) -> None:
        """Verify document upsert updates existing documents."""
        # Create initial document
        typesense_client.collections[test_collection].documents.create(sample_document)

        # Verify initial content
        doc = typesense_client.collections[test_collection].documents[sample_document["id"]].retrieve()
        assert doc["content"] == sample_document["content"]

        # Update document via upsert
        updated_doc = sample_document.copy()
        updated_doc["content"] = "Updated content for testing upsert"

        typesense_client.collections[test_collection].documents.upsert(updated_doc)

        # Verify update
        doc = typesense_client.collections[test_collection].documents[sample_document["id"]].retrieve()
        assert doc["content"] == "Updated content for testing upsert"

    def test_bulk_import_with_upsert(
        self,
        typesense_client: TypesenseClient,
        test_collection: str,
    ) -> None:
        """Verify bulk import with upsert action."""
        documents = [
            {
                "id": f"bulk_doc_{i}",
                "hierarchy.lvl0": "Bulk Test",
                "hierarchy.lvl1": f"Section {i}",
                "hierarchy.lvl2": "",
                "hierarchy.lvl3": "",
                "content": f"Bulk content item {i}",
                "url": f"bulk.html#section-{i}",
                "url_without_anchor": "bulk.html",
                "anchor": f"section-{i}",
                "type": "content",
                "version": "",
                "language": "en",
                "weight": 50,
                "item_priority": 50,
            }
            for i in range(5)
        ]

        result = typesense_client.collections[test_collection].documents.import_(documents, {"action": "upsert"})

        # All should succeed
        assert len(result) == 5
        for item in result:
            assert item.get("success", True)

        # Verify count
        collection_info = typesense_client.collections[test_collection].retrieve()
        assert collection_info["num_documents"] == 5


# =============================================================================
# Search Functionality Tests
# =============================================================================


class TestSearchFunctionality:
    """Tests for Typesense search operations."""

    @pytest.fixture
    def indexed_collection(
        self,
        typesense_client: TypesenseClient,
        test_collection: str,
    ) -> str:
        """Create a collection with indexed documents for search testing.

        Args:
            typesense_client: Typesense client fixture.
            test_collection: Collection name fixture.

        Returns:
            Collection name with indexed documents.

        """
        documents = [
            {
                "id": "doc_install",
                "hierarchy.lvl0": "Getting Started",
                "hierarchy.lvl1": "Installation",
                "hierarchy.lvl2": "",
                "hierarchy.lvl3": "",
                "content": "Install sphinx-typesense using pip install sphinx-typesense",
                "url": "getting-started.html#installation",
                "url_without_anchor": "getting-started.html",
                "anchor": "installation",
                "type": "lvl1",
                "version": "1.0",
                "language": "en",
                "weight": 90,
                "item_priority": 90,
            },
            {
                "id": "doc_config",
                "hierarchy.lvl0": "Getting Started",
                "hierarchy.lvl1": "Configuration",
                "hierarchy.lvl2": "",
                "hierarchy.lvl3": "",
                "content": "Configure sphinx-typesense in your conf.py file",
                "url": "getting-started.html#configuration",
                "url_without_anchor": "getting-started.html",
                "anchor": "configuration",
                "type": "lvl1",
                "version": "1.0",
                "language": "en",
                "weight": 90,
                "item_priority": 90,
            },
            {
                "id": "doc_api",
                "hierarchy.lvl0": "API Reference",
                "hierarchy.lvl1": "TypesenseIndexer",
                "hierarchy.lvl2": "",
                "hierarchy.lvl3": "",
                "content": "The TypesenseIndexer class handles document extraction and indexing",
                "url": "api.html#typesenseindexer",
                "url_without_anchor": "api.html",
                "anchor": "typesenseindexer",
                "type": "lvl1",
                "version": "1.0",
                "language": "en",
                "weight": 90,
                "item_priority": 90,
            },
            {
                "id": "doc_search",
                "hierarchy.lvl0": "Features",
                "hierarchy.lvl1": "Search",
                "hierarchy.lvl2": "Full-text Search",
                "hierarchy.lvl3": "",
                "content": "Full-text search with typo tolerance and ranking",
                "url": "features.html#full-text-search",
                "url_without_anchor": "features.html",
                "anchor": "full-text-search",
                "type": "lvl2",
                "version": "1.0",
                "language": "en",
                "weight": 80,
                "item_priority": 80,
            },
        ]

        typesense_client.collections[test_collection].documents.import_(documents, {"action": "upsert"})

        return test_collection

    def test_basic_text_search(
        self,
        typesense_client: TypesenseClient,
        indexed_collection: str,
    ) -> None:
        """Verify basic text search works."""
        search_params = {
            "q": "sphinx-typesense",
            "query_by": "content,hierarchy.lvl0,hierarchy.lvl1",
        }

        result = typesense_client.collections[indexed_collection].documents.search(search_params)

        assert result["found"] > 0
        assert len(result["hits"]) > 0

    def test_search_hierarchy_lvl0(
        self,
        typesense_client: TypesenseClient,
        indexed_collection: str,
    ) -> None:
        """Verify searching by lvl0 hierarchy works."""
        search_params = {
            "q": "Getting Started",
            "query_by": "hierarchy.lvl0",
        }

        result = typesense_client.collections[indexed_collection].documents.search(search_params)

        assert result["found"] > 0
        # All results should have "Getting Started" in lvl0
        for hit in result["hits"]:
            assert "Getting Started" in hit["document"]["hierarchy.lvl0"]

    def test_search_hierarchy_lvl1(
        self,
        typesense_client: TypesenseClient,
        indexed_collection: str,
    ) -> None:
        """Verify searching by lvl1 hierarchy works."""
        search_params = {
            "q": "Installation",
            "query_by": "hierarchy.lvl1",
        }

        result = typesense_client.collections[indexed_collection].documents.search(search_params)

        assert result["found"] > 0
        for hit in result["hits"]:
            assert "Installation" in hit["document"]["hierarchy.lvl1"]

    def test_search_hierarchy_lvl2(
        self,
        typesense_client: TypesenseClient,
        indexed_collection: str,
    ) -> None:
        """Verify searching by lvl2 hierarchy works."""
        search_params = {
            "q": "Full-text",
            "query_by": "hierarchy.lvl2",
        }

        result = typesense_client.collections[indexed_collection].documents.search(search_params)

        assert result["found"] > 0
        for hit in result["hits"]:
            doc = hit["document"]
            assert "Full-text" in doc.get("hierarchy.lvl2", "")

    def test_search_with_typo_tolerance(
        self,
        typesense_client: TypesenseClient,
        indexed_collection: str,
    ) -> None:
        """Verify typo tolerance in search."""
        # Search with typo: "instal" instead of "install"
        search_params = {
            "q": "instal",
            "query_by": "content,hierarchy.lvl1",
            "num_typos": 2,
        }

        result = typesense_client.collections[indexed_collection].documents.search(search_params)

        # Should find "Installation" despite typo
        assert result["found"] > 0

    def test_search_no_results(
        self,
        typesense_client: TypesenseClient,
        indexed_collection: str,
    ) -> None:
        """Verify empty search results are handled."""
        search_params = {
            "q": "nonexistent_unique_term_xyz123",
            "query_by": "content",
        }

        result = typesense_client.collections[indexed_collection].documents.search(search_params)

        assert result["found"] == 0
        assert len(result["hits"]) == 0

    def test_search_with_filter(
        self,
        typesense_client: TypesenseClient,
        indexed_collection: str,
    ) -> None:
        """Verify search with filter_by works."""
        search_params = {
            "q": "*",
            "query_by": "content",
            "filter_by": "type:lvl1",
        }

        result = typesense_client.collections[indexed_collection].documents.search(search_params)

        assert result["found"] > 0
        for hit in result["hits"]:
            assert hit["document"]["type"] == "lvl1"


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestErrorHandling:
    """Tests for error scenarios and graceful degradation."""

    def test_invalid_api_key(self) -> None:
        """Verify handling of invalid API key."""
        client = TypesenseClient(
            {
                "nodes": [{"host": "localhost", "port": "8108", "protocol": "http"}],
                "api_key": "invalid_key_12345",
                "connection_timeout_seconds": 2,
            }
        )

        with pytest.raises(RequestUnauthorized):
            client.collections.create({"name": "test", "fields": [{"name": "f", "type": "string"}]})

    def test_collection_not_found(self, typesense_client: TypesenseClient) -> None:
        """Verify handling of non-existent collection."""
        with pytest.raises(ObjectNotFound):
            typesense_client.collections["nonexistent_collection_xyz123"].retrieve()

    def test_document_not_found(
        self,
        typesense_client: TypesenseClient,
        test_collection: str,
    ) -> None:
        """Verify handling of non-existent document."""
        with pytest.raises(ObjectNotFound):
            typesense_client.collections[test_collection].documents["nonexistent_doc_xyz"].retrieve()


class TestServerUnavailable:
    """Tests for server unavailable scenarios.

    Note: These tests use a different port to simulate unavailability.
    They are separate because they don't require the running server.
    """

    def test_connection_timeout_on_unavailable_server(self) -> None:
        """Verify connection timeout when server is unavailable."""
        # Use a port that's unlikely to have a server
        client = TypesenseClient(
            {
                "nodes": [{"host": "localhost", "port": "19999", "protocol": "http"}],
                "api_key": "xyz",
                "connection_timeout_seconds": 1,
            }
        )

        # Should raise an exception when trying to connect
        with pytest.raises((OSError, HTTPStatus0Error, TimeoutError)):
            client.operations.is_healthy()

    def test_indexer_handles_unavailable_server(self, tmp_path: Path) -> None:
        """Verify TypesenseIndexer handles unavailable server gracefully."""
        app = MagicMock(spec=["config", "outdir", "srcdir", "builder", "env"])
        app.config = MagicMock()
        app.config.typesense_host = "localhost"
        app.config.typesense_port = "19999"  # Unavailable port
        app.config.typesense_protocol = "http"
        app.config.typesense_api_key = "xyz"
        app.config.typesense_collection_name = "test_unavailable"
        app.config.typesense_doc_version = ""
        app.config.typesense_content_selectors = None
        app.config.typesense_enable_indexing = True
        app.config.typesense_drop_existing = False
        app.config.typesense_connection_timeout = 1
        app.config.language = "en"
        app.outdir = str(tmp_path)

        # Create HTML file
        html_file = tmp_path / "test.html"
        html_file.write_text("""<!DOCTYPE html>
<html><head><title>Test</title></head>
<body><div class="body"><h1>Test</h1><p>Content</p></div></body>
</html>""")

        indexer = TypesenseIndexer(app)

        # Should return 0 and not raise when server unavailable
        count = indexer.index_all()
        assert count == 0


# =============================================================================
# TypesenseIndexer Integration Tests
# =============================================================================


class TestTypesenseIndexerIntegration:
    """Integration tests for TypesenseIndexer with real Typesense server."""

    def test_indexer_creates_collection_if_not_exists(
        self,
        integration_sphinx_app: MagicMock,
        typesense_client: TypesenseClient,
        test_collection_name: str,
    ) -> None:
        """Verify indexer creates collection if it doesn't exist."""
        # Ensure collection doesn't exist
        with contextlib.suppress(ObjectNotFound):
            typesense_client.collections[test_collection_name].delete()

        # Set drop_existing to trigger creation path
        integration_sphinx_app.config.typesense_drop_existing = True

        indexer = TypesenseIndexer(integration_sphinx_app)

        # Create a test HTML file
        html_dir = Path(integration_sphinx_app.outdir)
        html_file = html_dir / "test.html"
        html_file.write_text("""<!DOCTYPE html>
<html><head><title>Test</title></head>
<body><div class="body"><h1>Test</h1><p>Content</p></div></body>
</html>""")

        # Run indexing - should create collection
        count = indexer.index_all()
        assert count > 0

        # Verify collection exists
        result = typesense_client.collections[test_collection_name].retrieve()
        assert result["name"] == test_collection_name

        # Cleanup
        typesense_client.collections[test_collection_name].delete()

    def test_indexer_respects_drop_existing_flag(
        self,
        integration_sphinx_app: MagicMock,
        typesense_client: TypesenseClient,
        test_collection_name: str,
    ) -> None:
        """Verify indexer drops and recreates collection when flag is True."""
        # Create collection and add a document
        with contextlib.suppress(ObjectNotFound):
            typesense_client.collections[test_collection_name].delete()

        schema = DOCS_SCHEMA.copy()
        schema["name"] = test_collection_name
        typesense_client.collections.create(schema)  # type: ignore[arg-type]

        # Add a document that won't be in our test HTML
        doc = {
            "id": "old_doc",
            "hierarchy.lvl0": "Old Content",
            "hierarchy.lvl1": "",
            "hierarchy.lvl2": "",
            "hierarchy.lvl3": "",
            "content": "This should be deleted",
            "url": "old.html",
            "url_without_anchor": "old.html",
            "anchor": "",
            "type": "content",
            "version": "",
            "language": "en",
            "weight": 50,
            "item_priority": 50,
        }
        typesense_client.collections[test_collection_name].documents.create(doc)

        # Verify document exists
        old_count = typesense_client.collections[test_collection_name].retrieve()["num_documents"]
        assert old_count == 1

        # Enable drop_existing
        integration_sphinx_app.config.typesense_drop_existing = True

        # Create test HTML
        html_dir = Path(integration_sphinx_app.outdir)
        html_file = html_dir / "new.html"
        html_file.write_text("""<!DOCTYPE html>
<html><head><title>New</title></head>
<body><div class="body"><h1>New Content</h1><p>Fresh content</p></div></body>
</html>""")

        indexer = TypesenseIndexer(integration_sphinx_app)
        indexer.index_all()

        # Old document should be gone, new documents should exist
        collection_info = typesense_client.collections[test_collection_name].retrieve()
        assert collection_info["num_documents"] > 0

        # Verify old document is gone
        with pytest.raises(ObjectNotFound):
            typesense_client.collections[test_collection_name].documents["old_doc"].retrieve()

        # Cleanup
        typesense_client.collections[test_collection_name].delete()

    def test_indexer_check_connection(
        self,
        integration_sphinx_app: MagicMock,
    ) -> None:
        """Verify indexer connection check works."""
        indexer = TypesenseIndexer(integration_sphinx_app)

        # Should be able to connect (using public interface via index_all)
        # The _check_connection is private but we test it indirectly
        # by confirming index_all returns > 0 when server is available
        html_dir = Path(integration_sphinx_app.outdir)
        html_file = html_dir / "connection_test.html"
        html_file.write_text("""<!DOCTYPE html>
<html><head><title>Test</title></head>
<body><div class="body"><h1>Test</h1><p>Content</p></div></body>
</html>""")
        integration_sphinx_app.config.typesense_drop_existing = True

        # If connection works, this should return > 0
        count = indexer.index_all()
        assert count > 0

    def test_indexer_extracts_hierarchy_correctly(
        self,
        integration_sphinx_app: MagicMock,
        typesense_client: TypesenseClient,
        test_collection_name: str,
    ) -> None:
        """Verify indexer extracts document hierarchy correctly."""
        integration_sphinx_app.config.typesense_drop_existing = True

        # Create HTML with specific hierarchy
        html_dir = Path(integration_sphinx_app.outdir)
        html_file = html_dir / "hierarchy.html"
        html_file.write_text("""<!DOCTYPE html>
<html lang="en">
<head><title>Hierarchy Test</title></head>
<body>
    <div class="body">
        <h1 id="level-0">Level Zero</h1>
        <p>Content under level 0</p>
        <h2 id="level-1">Level One</h2>
        <p>Content under level 1</p>
        <h3 id="level-2">Level Two</h3>
        <p>Content under level 2</p>
    </div>
</body>
</html>""")

        indexer = TypesenseIndexer(integration_sphinx_app)
        count = indexer.index_all()
        assert count > 0

        # Search for level 0 content
        search_result = typesense_client.collections[test_collection_name].documents.search(
            {"q": "Level Zero", "query_by": "hierarchy.lvl0,hierarchy.lvl1,content"}
        )

        assert search_result["found"] > 0

        # Verify hierarchy structure
        found_lvl0 = False
        for hit in search_result["hits"]:
            doc = hit["document"]
            if doc.get("hierarchy.lvl0") == "Level Zero":
                found_lvl0 = True

        assert found_lvl0, "Should find Level Zero in hierarchy"

        # Search for level 1 content
        search_result = typesense_client.collections[test_collection_name].documents.search(
            {"q": "Level One", "query_by": "hierarchy.lvl1"}
        )
        assert search_result["found"] > 0

        # Cleanup
        typesense_client.collections[test_collection_name].delete()
