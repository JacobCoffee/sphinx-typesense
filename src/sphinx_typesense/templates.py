"""HTML and JavaScript injection for sphinx-typesense search UI.

This module handles injecting the search configuration and container
into Sphinx HTML pages, with support for multiple backends (Typesense
and Pagefind).

The injection process:
    1. Determines the effective backend from configuration
    2. Adds search container div to page context
    3. Injects backend-specific JavaScript configuration
    4. Handles theme-specific search bar placement

Assets:
    Typesense backend:
        - typesense-docsearch.css: DocSearch styling
        - typesense-docsearch.js: DocSearch library (from CDN)
        - typesense-init.js: Initialization script with config

    Pagefind backend:
        - pagefind-ui.css: Pagefind UI styling
        - pagefind-init.js: Initialization script with config

Example:
    The module is used automatically via Sphinx event::

        app.connect("html-page-context", inject_search_assets)

"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from sphinx.util import logging

from sphinx_typesense.config import get_effective_backend

if TYPE_CHECKING:
    from sphinx.application import Sphinx

logger = logging.getLogger(__name__)


def inject_search_assets(
    app: Sphinx,
    pagename: str,
    templatename: str,  # noqa: ARG001
    context: dict[str, Any],
    doctree: Any,  # noqa: ARG001
) -> None:
    """Inject search configuration into page context based on selected backend.

    This function is connected to Sphinx's html-page-context event
    and adds the search UI HTML and JavaScript configuration to
    each page. The configuration varies based on the selected backend
    (Typesense or Pagefind).

    Args:
        app: The Sphinx application instance.
        pagename: Name of the current page being rendered.
        templatename: Name of the template being used.
        context: Template context dictionary to modify.
        doctree: The document tree (may be None for some pages).

    Note:
        The search container and configuration are added to the
        context as 'typesense_search_html' which can be included
        in templates or injected via theme-specific methods.

    """
    logger.debug("sphinx-typesense: Injecting search assets for page: %s", pagename)

    # Get the effective backend
    backend_name = get_effective_backend(app.config)
    logger.debug("sphinx-typesense: Using backend: %s", backend_name)

    # Generate the search container HTML
    container_html = get_search_container_html(app)
    logger.debug("sphinx-typesense: Generated search container HTML")

    # Generate the config script based on backend
    config_script = get_typesense_config_script(app) if backend_name == "typesense" else get_pagefind_config_script(app)
    logger.debug("sphinx-typesense: Generated config script for %s backend", backend_name)

    # Combine into a single HTML block
    search_html = f"{container_html}\n{config_script}"

    # Add to template context
    context["typesense_search_html"] = search_html
    logger.debug("sphinx-typesense: Added typesense_search_html to context")
    logger.debug("sphinx-typesense: Search assets injection complete for page: %s", pagename)


def get_search_container_html(app: Sphinx) -> str:
    """Generate the search container HTML.

    Args:
        app: The Sphinx application instance.

    Returns:
        HTML string for the search container div.

    """
    container = app.config.typesense_container
    # Strip leading # if present to get the ID
    container_id = container.lstrip("#") if container.startswith("#") else container
    logger.debug("sphinx-typesense: Using container ID: %s", container_id)

    return f'<div id="{container_id}"></div>'


def get_config_script(app: Sphinx) -> str:
    """Generate the JavaScript configuration script (deprecated).

    This function is kept for backward compatibility. New code should
    use get_typesense_config_script() or get_pagefind_config_script()
    based on the selected backend.

    Args:
        app: The Sphinx application instance.

    Returns:
        JavaScript script tag with TYPESENSE_CONFIG object.

    """
    return get_typesense_config_script(app)


def get_typesense_config_script(app: Sphinx) -> str:
    """Generate JavaScript configuration for Typesense DocSearch.

    Creates a script tag containing the TYPESENSE_CONFIG object with
    all necessary configuration for the DocSearch frontend to connect
    to the Typesense server.

    Args:
        app: The Sphinx application instance.

    Returns:
        JavaScript script tag with window.TYPESENSE_CONFIG object.

    Note:
        Only the search API key is exposed in the frontend configuration,
        never the admin API key.

    """
    logger.debug("sphinx-typesense: Building Typesense JavaScript configuration")

    # Build configuration object
    config = {
        "collectionName": app.config.typesense_collection_name,
        "host": app.config.typesense_host,
        "port": str(app.config.typesense_port),
        "protocol": app.config.typesense_protocol,
        "apiKey": app.config.typesense_search_api_key,  # Use search-only key, NOT admin key
        "placeholder": app.config.typesense_placeholder,
        "numTypos": app.config.typesense_num_typos,
        "perPage": app.config.typesense_per_page,
        "filterBy": app.config.typesense_filter_by,
        "container": app.config.typesense_container,
    }

    logger.debug(
        "sphinx-typesense: Config script - collection=%s, host=%s, port=%s",
        config["collectionName"],
        config["host"],
        config["port"],
    )

    # Warn if search API key is missing
    if not config["apiKey"]:
        logger.warning("sphinx-typesense: Search API key is not configured - search may not work")

    # Use json.dumps for proper escaping and formatting
    config_json = json.dumps(config, indent=2)

    return f"""<script>
  window.TYPESENSE_CONFIG = {config_json};
</script>"""


def get_pagefind_config_script(app: Sphinx) -> str:
    """Generate JavaScript configuration for Pagefind UI.

    Creates a script tag containing the PAGEFIND_CONFIG object with
    configuration for the Pagefind UI frontend.

    Args:
        app: The Sphinx application instance.

    Returns:
        JavaScript script tag with window.PAGEFIND_CONFIG object.

    """
    logger.debug("sphinx-typesense: Building Pagefind JavaScript configuration")

    config = {
        "container": app.config.typesense_container,
        "placeholder": app.config.typesense_placeholder,
        "basePath": "/_pagefind/",
    }

    logger.debug(
        "sphinx-typesense: Pagefind config - container=%s, basePath=%s",
        config["container"],
        config["basePath"],
    )

    config_json = json.dumps(config, indent=2)

    return f"""<script>
  window.PAGEFIND_CONFIG = {config_json};
</script>"""


def add_search_meta_tags(app: Sphinx, context: dict[str, Any], backend_name: str | None = None) -> None:
    """Add meta tags for search configuration.

    Adds meta tags that can be used by the JavaScript to get
    configuration without inline scripts (for CSP compliance).

    Args:
        app: The Sphinx application instance.
        context: Template context dictionary to modify.
        backend_name: The backend name ('typesense' or 'pagefind').
            If None, determined from config.

    Note:
        Meta tags are added to context['metatags'] if it exists,
        allowing the configuration to be read via JavaScript
        document.querySelector for CSP-compliant implementations.

    """
    logger.debug("sphinx-typesense: Adding meta tags for CSP-compliant configuration")

    # Determine backend if not provided
    if backend_name is None:
        backend_name = get_effective_backend(app.config)

    # Common meta entries for both backends
    meta_entries = [
        ("typesense-backend", backend_name),
        ("typesense-container", app.config.typesense_container),
        ("typesense-placeholder", app.config.typesense_placeholder),
    ]

    # Add backend-specific meta entries
    if backend_name == "typesense":
        meta_entries.extend(
            [
                ("typesense-collection", app.config.typesense_collection_name),
                ("typesense-host", app.config.typesense_host),
                ("typesense-port", str(app.config.typesense_port)),
                ("typesense-protocol", app.config.typesense_protocol),
                ("typesense-api-key", app.config.typesense_search_api_key),
                ("typesense-num-typos", str(app.config.typesense_num_typos)),
                ("typesense-per-page", str(app.config.typesense_per_page)),
                ("typesense-filter-by", app.config.typesense_filter_by),
            ]
        )
    else:  # pagefind
        meta_entries.extend(
            [
                ("pagefind-base-path", "/_pagefind/"),
            ]
        )

    # Initialize metatags if not present or not a list
    # Some themes use strings or other formats for metatags
    if "metatags" not in context or not isinstance(context["metatags"], list):
        logger.debug("sphinx-typesense: Initializing metatags list in context")
        context["metatags"] = []

    # Add each config value as a meta tag
    for name, content in meta_entries:
        context["metatags"].append({"name": name, "content": str(content)})

    logger.debug("sphinx-typesense: Added %d meta tags to context", len(meta_entries))
