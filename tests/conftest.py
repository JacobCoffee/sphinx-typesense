"""Pytest configuration and shared fixtures for sphinx-typesense tests.

This module provides:
    - pytest configuration and markers
    - Shared fixtures for testing Sphinx applications
    - HTML content fixtures for extraction testing
    - Mock fixtures for external services

Markers:
    slow: Tests that take more than 1 second
    integration: Tests requiring a Typesense server

Example:
    Run only unit tests (exclude slow and integration)::

        pytest -m "not slow and not integration"

    Run integration tests::

        pytest -m integration

"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock

import pytest

if TYPE_CHECKING:
    from pathlib import Path

# =============================================================================
# Pytest Configuration
# =============================================================================


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers for test categorization."""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "integration: marks tests as integration tests requiring Typesense")


# =============================================================================
# Sphinx Application Fixtures
# =============================================================================


@pytest.fixture
def mock_sphinx_app() -> MagicMock:
    """Create a mock Sphinx application for testing.

    Returns:
        MagicMock configured as a Sphinx application with default config values.

    Example:
        def test_something(mock_sphinx_app):
            mock_sphinx_app.config.typesense_host = "custom.host"
            # use mock_sphinx_app in tests

    """
    app = MagicMock(
        spec=[
            "config",
            "outdir",
            "srcdir",
            "builder",
            "env",
            "add_config_value",
            "connect",
            "add_css_file",
            "add_js_file",
        ]
    )

    # Set up config with default values
    app.config = MagicMock()
    app.config.typesense_backend = "auto"
    app.config.typesense_host = "localhost"
    app.config.typesense_port = "8108"
    app.config.typesense_protocol = "http"
    app.config.typesense_api_key = "test_admin_key"
    app.config.typesense_search_api_key = "test_search_key"
    app.config.typesense_collection_name = "test_sphinx_docs"
    app.config.typesense_doc_version = ""
    app.config.typesense_placeholder = "Search documentation..."
    app.config.typesense_num_typos = 2
    app.config.typesense_per_page = 10
    app.config.typesense_container = "#typesense-search"
    app.config.typesense_filter_by = ""
    app.config.typesense_content_selectors = None
    app.config.typesense_enable_indexing = True
    app.config.typesense_drop_existing = False
    app.config.language = "en"
    app.config.html_theme = "alabaster"
    app.config.html_static_path = []

    return app


@pytest.fixture
def mock_sphinx_config() -> MagicMock:
    """Create a mock Sphinx config object.

    Returns:
        MagicMock configured with Typesense configuration values.

    """
    config = MagicMock()
    # Backend selection
    config.typesense_backend = "auto"
    # Required settings
    config.typesense_host = "localhost"
    config.typesense_port = "8108"
    config.typesense_protocol = "http"
    config.typesense_api_key = "xyz_admin_key"
    config.typesense_search_api_key = "abc_search_key"
    # Optional settings
    config.typesense_collection_name = "sphinx_docs"
    config.typesense_doc_version = ""
    config.typesense_placeholder = "Search documentation..."
    config.typesense_num_typos = 2
    config.typesense_per_page = 10
    config.typesense_container = "#typesense-search"
    config.typesense_filter_by = ""
    config.typesense_content_selectors = None
    config.typesense_enable_indexing = True
    config.typesense_drop_existing = False
    return config


# =============================================================================
# HTML Content Fixtures
# =============================================================================


@pytest.fixture
def sample_html_content() -> str:
    """Provide sample HTML content for extraction testing.

    Returns:
        HTML string with typical documentation structure including
        headings, paragraphs, and list items.

    Example:
        def test_extraction(sample_html_content):
            soup = BeautifulSoup(sample_html_content, "html.parser")
            # test extraction logic

    """
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Installation Guide</title>
</head>
<body>
    <div class="body">
        <h1 id="installation">Installation</h1>
        <p>This guide covers installing sphinx-typesense.</p>

        <h2 id="prerequisites">Prerequisites</h2>
        <p>Before installing, ensure you have:</p>
        <ul>
            <li>Python 3.9 or higher</li>
            <li>pip or uv package manager</li>
            <li>Typesense server (local or cloud)</li>
        </ul>

        <h3 id="python-version">Python Version</h3>
        <p>We recommend using the latest Python version for best performance.</p>

        <h2 id="installation-methods">Installation Methods</h2>

        <h3 id="pip-install">Using pip</h3>
        <p>Install using pip:</p>
        <pre><code>pip install sphinx-typesense</code></pre>

        <h3 id="uv-install">Using uv</h3>
        <p>Install using uv for faster installation:</p>
        <pre><code>uv add sphinx-typesense</code></pre>
    </div>
</body>
</html>"""


@pytest.fixture
def minimal_html_content() -> str:
    """Provide minimal HTML for edge case testing.

    Returns:
        Simple HTML with just a heading and paragraph.

    """
    return """<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
    <div class="body">
        <h1>Test Page</h1>
        <p>Test content.</p>
    </div>
</body>
</html>"""


@pytest.fixture
def rtd_theme_html() -> str:
    """Provide HTML mimicking ReadTheDocs theme structure.

    Returns:
        HTML with RTD theme-specific selectors.

    """
    return """<!DOCTYPE html>
<html>
<head><title>RTD Theme Test</title></head>
<body>
    <div class="wy-nav-content-wrap">
        <div class="wy-nav-content">
            <div class="rst-content" role="main">
                <h1>Documentation</h1>
                <p>Welcome to the documentation.</p>
                <h2>Getting Started</h2>
                <p>Get started quickly with these steps.</p>
            </div>
        </div>
    </div>
</body>
</html>"""


@pytest.fixture
def furo_theme_html() -> str:
    """Provide HTML mimicking Furo theme structure.

    Returns:
        HTML with Furo theme-specific selectors.

    """
    return """<!DOCTYPE html>
<html>
<head><title>Furo Theme Test</title></head>
<body>
    <article role="main">
        <h1>API Reference</h1>
        <p>This is the API reference documentation.</p>
        <h2>Classes</h2>
        <p>Available classes in the module.</p>
    </article>
</body>
</html>"""


# =============================================================================
# Temporary File Fixtures
# =============================================================================


@pytest.fixture
def tmp_html(tmp_path: Path, sample_html_content: str) -> Path:
    """Create a temporary HTML file for testing.

    Args:
        tmp_path: pytest's temporary directory fixture.
        sample_html_content: HTML content to write.

    Returns:
        Path to the temporary HTML file.

    Example:
        def test_file_reading(tmp_html):
            content = tmp_html.read_text()
            assert "Installation" in content

    """
    html_file = tmp_path / "test_page.html"
    html_file.write_text(sample_html_content)
    return html_file


@pytest.fixture
def tmp_html_dir(tmp_path: Path, sample_html_content: str, minimal_html_content: str) -> Path:
    """Create a temporary directory with multiple HTML files.

    Args:
        tmp_path: pytest's temporary directory fixture.
        sample_html_content: Content for main documentation page.
        minimal_html_content: Content for secondary page.

    Returns:
        Path to the temporary directory containing HTML files.

    """
    html_dir = tmp_path / "html"
    html_dir.mkdir()

    (html_dir / "index.html").write_text(sample_html_content)
    (html_dir / "about.html").write_text(minimal_html_content)

    # Create subdirectory with additional files
    subdir = html_dir / "api"
    subdir.mkdir()
    (subdir / "reference.html").write_text(minimal_html_content)

    return html_dir


# =============================================================================
# Mock Service Fixtures
# =============================================================================


@pytest.fixture
def mock_typesense_client() -> MagicMock:
    """Create a mock Typesense client for testing without a server.

    Returns:
        MagicMock configured to behave like typesense.Client.

    Example:
        def test_indexing(mock_typesense_client):
            mock_typesense_client.collections["docs"].documents.import_.return_value = []
            # test indexing logic

    """
    client = MagicMock()

    # Set up collections mock
    collection = MagicMock()
    collection.documents.import_ = MagicMock(return_value=[])
    collection.documents.search = MagicMock(return_value={"hits": [], "found": 0})
    collection.retrieve = MagicMock(return_value={"name": "test_sphinx_docs", "num_documents": 0})

    client.collections = MagicMock()
    client.collections.__getitem__ = MagicMock(return_value=collection)
    client.collections.create = MagicMock(return_value={"name": "test_sphinx_docs"})

    return client


@pytest.fixture
def mock_beautifulsoup() -> MagicMock:
    """Create a mock BeautifulSoup object for HTML parsing tests.

    Returns:
        MagicMock configured as a BeautifulSoup parsed document.

    """
    soup = MagicMock()
    soup.select_one = MagicMock(return_value=MagicMock())
    soup.find_all = MagicMock(return_value=[])
    return soup


# =============================================================================
# Fixture Data
# =============================================================================


@pytest.fixture
def expected_hierarchy() -> dict[str, str]:
    """Provide expected hierarchy structure for extraction tests.

    Returns:
        Dictionary with expected heading hierarchy.

    """
    return {
        "lvl0": "Installation",
        "lvl1": "Prerequisites",
        "lvl2": "Python Version",
        "lvl3": "",
    }


@pytest.fixture
def sample_typesense_document() -> dict[str, Any]:
    """Provide a sample Typesense document for comparison.

    Returns:
        Document dictionary matching the expected schema.

    """
    return {
        "id": "abc123",
        "hierarchy.lvl0": "Installation",
        "hierarchy.lvl1": "Prerequisites",
        "hierarchy.lvl2": "",
        "hierarchy.lvl3": "",
        "content": "Before installing, ensure you have:",
        "url": "installation.html#prerequisites",
        "url_without_anchor": "installation.html",
        "anchor": "prerequisites",
        "type": "content",
        "version": "",
        "language": "en",
        "weight": 50,
        "item_priority": 50,
    }
