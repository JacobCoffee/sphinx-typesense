"""sphinx-typesense: A Sphinx extension for Typesense search integration.

This extension replaces Sphinx's default search with Typesense or Pagefind,
providing typo-tolerant, fast search functionality for documentation sites.

Features:
    - Build-time indexing of documentation content
    - Support for multiple search backends (Typesense, Pagefind)
    - DocSearch-compatible frontend search UI
    - Support for multiple Sphinx themes (RTD, Furo, Alabaster, PyData)
    - Both self-hosted Typesense Server and Typesense Cloud support
    - Zero-config Pagefind for static site search

Example:
    Add to your Sphinx conf.py::

        extensions = ["sphinx_typesense"]

        # For Typesense backend:
        typesense_host = "localhost"
        typesense_port = "8108"
        typesense_protocol = "http"
        typesense_api_key = "your_admin_key"
        typesense_search_api_key = "your_search_key"

        # Or for Pagefind backend (no server required):
        typesense_backend = "pagefind"

"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from sphinx.util import logging

from sphinx_typesense.backends.base import SearchBackend
from sphinx_typesense.config import get_effective_backend, setup_config, validate_config
from sphinx_typesense.templates import inject_search_assets

if TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.config import Config

# Path to static files bundled with the extension
STATIC_PATH = Path(__file__).parent / "static"

__version__ = "0.1.0"
__all__ = ["SearchBackend", "__version__", "get_backend", "setup"]

logger = logging.getLogger(__name__)


def get_backend(app: Sphinx) -> SearchBackend:
    """Get the appropriate backend instance based on configuration.

    This factory function returns the correct backend implementation
    based on the typesense_backend configuration value.

    Args:
        app: The Sphinx application instance.

    Returns:
        SearchBackend instance (TypesenseBackend or PagefindBackend).

    Example:
        Get and use the backend for indexing::

            backend = get_backend(app)
            if backend.is_available():
                count = backend.index_all()
                print(f"Indexed {count} documents")

    """
    # Lazy imports to avoid circular dependencies and improve startup time
    from sphinx_typesense.backends.pagefind import PagefindBackend  # noqa: PLC0415
    from sphinx_typesense.backends.typesense import TypesenseBackend  # noqa: PLC0415

    backend_name = get_effective_backend(app.config)
    logger.debug("sphinx-typesense: Creating backend instance for '%s'", backend_name)

    if backend_name == "typesense":
        return TypesenseBackend(app)
    # pagefind
    return PagefindBackend(app)


def _write_config_js(app: Sphinx) -> None:
    """Write the Typesense configuration to a JS file.

    This function writes the TYPESENSE_CONFIG object to a JavaScript file
    that gets loaded before the init script.

    Args:
        app: The Sphinx application instance.

    """
    backend_name = get_effective_backend(app.config)
    if backend_name != "typesense":
        return

    # Build the config object
    # Note: port must be an integer for the Typesense JS client
    config = {
        "collectionName": app.config.typesense_collection_name,
        "host": app.config.typesense_host,
        "port": int(app.config.typesense_port),
        "protocol": app.config.typesense_protocol,
        "apiKey": app.config.typesense_search_api_key,
        "placeholder": app.config.typesense_placeholder,
        "numTypos": app.config.typesense_num_typos,
        "perPage": app.config.typesense_per_page,
        "filterBy": app.config.typesense_filter_by,
        "container": app.config.typesense_container,
    }

    config_js = f"window.TYPESENSE_CONFIG = {json.dumps(config, indent=2)};"

    # Write to the output static directory
    outdir = Path(app.outdir) / "_static"
    outdir.mkdir(parents=True, exist_ok=True)
    config_path = outdir / "typesense-config.js"
    config_path.write_text(config_js)
    logger.debug("sphinx-typesense: Wrote config to %s", config_path)


def index_documents(app: Sphinx, exception: Exception | None) -> None:
    """Sphinx event handler to index documents after build completes.

    This function is connected to Sphinx's ``build-finished`` event and
    triggers the indexing of all HTML documents using the selected backend.

    Args:
        app: The Sphinx application instance.
        exception: Exception raised during build, if any. When not None,
            indexing is skipped to avoid indexing partial or broken content.

    Note:
        Indexing is controlled by the ``typesense_enable_indexing`` config
        option. Set to False to disable automatic indexing (useful for
        development builds or when indexing is handled separately).

    Example:
        This function is called automatically by Sphinx after the build
        completes. It can also be invoked manually for testing::

            index_documents(app, None)

    """
    logger.debug("sphinx-typesense: index_documents handler invoked")

    # Skip if build failed
    if exception is not None:
        logger.warning("sphinx-typesense: Build failed with exception, skipping: %s", exception)
        return

    # Write the config JS file (for frontend search)
    _write_config_js(app)

    # Skip if indexing is disabled
    if not app.config.typesense_enable_indexing:
        logger.info("sphinx-typesense: Indexing disabled via typesense_enable_indexing=False")
        return

    # Get and use the appropriate backend
    backend = get_backend(app)

    # Check if backend is available (server up for Typesense, CLI available for Pagefind)
    if not backend.is_available():
        logger.warning("sphinx-typesense: Backend '%s' not available, skipping indexing", backend.name)
        return

    # Perform indexing
    logger.info("sphinx-typesense: Starting document indexing with %s backend", backend.name)
    count = backend.index_all()
    logger.info("sphinx-typesense: Indexing complete - %d documents indexed", count)


def _add_static_files(app: Sphinx, config: Config) -> None:
    """Add static files based on selected backend.

    This function is connected to the config-inited event to add
    the appropriate CSS and JavaScript files for the selected backend.

    Args:
        app: The Sphinx application instance.
        config: The Sphinx configuration object.

    Note:
        Static files are added after configuration is initialized so
        that the backend selection is properly resolved.

    """
    backend_name = get_effective_backend(config)
    logger.debug("sphinx-typesense: Adding static files for %s backend", backend_name)

    if backend_name == "typesense":
        # Add CSS for DocSearch (CDN base styles + local customizations)
        app.add_css_file(
            "https://cdn.jsdelivr.net/npm/typesense-docsearch-css@0.4.1/dist/style.min.css",
            priority=400,
        )
        app.add_css_file("typesense-docsearch.css", priority=401)

        # Add DocSearch JS from CDN, then our init script
        app.add_js_file(
            "https://cdn.jsdelivr.net/npm/typesense-docsearch.js@3.4.0/dist/umd/index.min.js",
            priority=500,
        )
        app.add_js_file("typesense-config.js", priority=500)  # Generated during build
        app.add_js_file("typesense-init.js", priority=501)
    else:  # pagefind
        # Pagefind assets are loaded dynamically from the _pagefind directory
        # We only need our init script and optional CSS customizations
        app.add_css_file("pagefind-ui.css", priority=400)
        app.add_js_file("pagefind-init.js", priority=500)


def setup(app: Sphinx) -> dict[str, str | bool]:
    """Sphinx extension entry point.

    Registers configuration values, connects to Sphinx build events,
    and adds static assets for the search UI.

    Args:
        app: The Sphinx application instance.

    Returns:
        Extension metadata dictionary containing:
            - version: The extension version string
            - parallel_read_safe: Whether parallel reading is supported
            - parallel_write_safe: Whether parallel writing is supported

    Example:
        This function is called automatically by Sphinx when the extension
        is loaded. Users enable it by adding to conf.py::

            extensions = ["sphinx_typesense"]

    """
    logger.info("sphinx-typesense: Initializing extension v%s", __version__)
    logger.debug("sphinx-typesense: setup() entry point invoked")

    # Register configuration values
    logger.debug("sphinx-typesense: Registering configuration values")
    setup_config(app)

    # Connect to Sphinx events
    logger.debug("sphinx-typesense: Connecting to Sphinx events")
    app.connect("config-inited", validate_config)
    app.connect("build-finished", index_documents)
    app.connect("html-page-context", inject_search_assets)

    # Register static files directory
    logger.debug("sphinx-typesense: Registering static files directory")
    app.config.html_static_path.append(str(STATIC_PATH))

    # Defer adding static files until config is initialized
    # This allows the backend selection to be properly resolved
    app.connect("config-inited", _add_static_files)

    logger.debug("sphinx-typesense: Extension setup complete")
    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
