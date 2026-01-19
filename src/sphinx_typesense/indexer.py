"""Backward compatibility module for TypesenseIndexer.

This module maintains backward compatibility by re-exporting TypesenseBackend
as TypesenseIndexer and exposing the schema and weight constants.

.. deprecated::
    Use sphinx_typesense.backends.typesense.TypesenseBackend instead.

Example:
    New code should use::

        from sphinx_typesense.backends.typesense import TypesenseBackend

        backend = TypesenseBackend(app)
        count = backend.index_all()

    Legacy code using TypesenseIndexer continues to work::

        from sphinx_typesense.indexer import TypesenseIndexer

        indexer = TypesenseIndexer(app)
        count = indexer.index_all()

"""

from __future__ import annotations

from typing import TYPE_CHECKING

import typesense
import typesense.exceptions
from sphinx.util import logging
from typesense.exceptions import (
    HTTPStatus0Error,
    RequestUnauthorized,
    ServiceUnavailable,
    Timeout,
)

from sphinx_typesense.backends.typesense import (
    DOC_TYPE_PRIORITIES,
    DOC_TYPE_WEIGHTS,
    DOCS_SCHEMA,
    TypesenseBackend,
)

if TYPE_CHECKING:
    from sphinx.application import Sphinx

logger = logging.getLogger(__name__)

# Backward compatibility alias
TypesenseIndexer = TypesenseBackend

__all__ = [
    "DOCS_SCHEMA",
    "DOC_TYPE_PRIORITIES",
    "DOC_TYPE_WEIGHTS",
    "TypesenseBackend",
    "TypesenseIndexer",
    "index_documents",
]


def _log_indexing_error(exc: Exception) -> None:
    """Log an indexing error with appropriate context.

    Handles different exception types with specific, actionable messages
    to help users diagnose connection and configuration issues.

    Args:
        exc: The exception that occurred during indexing.

    """
    if isinstance(exc, RequestUnauthorized):
        logger.warning("sphinx-typesense: Authentication failed. Check typesense_api_key in conf.py")
    elif isinstance(exc, ServiceUnavailable):
        logger.warning("sphinx-typesense: Server unavailable. Documentation build completed without search indexing.")
    elif isinstance(exc, (Timeout, HTTPStatus0Error)):
        logger.warning("sphinx-typesense: Connection timed out. Check server availability and network configuration.")
    elif isinstance(exc, (ConnectionError, TimeoutError)):
        logger.warning(
            "sphinx-typesense: Network error (%s). Ensure Typesense server is running and accessible.",
            type(exc).__name__,
        )
    elif isinstance(exc, typesense.exceptions.TypesenseClientError):
        logger.warning("sphinx-typesense: Client error: %s", exc)
    elif isinstance(exc, OSError):
        logger.warning("sphinx-typesense: System error: %s", exc)
    else:
        logger.warning("sphinx-typesense: Unexpected error: %s", exc)


def index_documents(app: Sphinx, exception: Exception | None) -> None:
    """Sphinx event handler to index documents after build.

    This function is called by Sphinx after the build completes. It creates
    a TypesenseBackend and indexes all HTML files if no exception occurred.

    Implements graceful degradation: if Typesense is unavailable, the build
    completes successfully with a warning. Search will not be available until
    the server is restored and docs are rebuilt.

    Args:
        app: The Sphinx application instance.
        exception: Exception raised during build, if any.

    """
    logger.debug("sphinx-typesense: index_documents event handler invoked")

    # Don't index if build failed
    if exception:
        logger.debug("sphinx-typesense: Skipping indexing due to build exception: %s", exception)
        return

    # Check if indexing is enabled
    if not app.config.typesense_enable_indexing:
        logger.debug("sphinx-typesense: Indexing is disabled via configuration")
        return

    # Check if API key is configured
    if not app.config.typesense_api_key:
        logger.warning("sphinx-typesense: Skipping indexing - no API key configured")
        return

    logger.debug("sphinx-typesense: Starting indexing process")
    try:
        backend = TypesenseBackend(app)
        count = backend.index_all()
        if count > 0:
            logger.info("sphinx-typesense: Successfully indexed %d documents", count)
        else:
            logger.debug("sphinx-typesense: No documents indexed")
    except (
        RequestUnauthorized,
        ServiceUnavailable,
        Timeout,
        HTTPStatus0Error,
        ConnectionError,
        TimeoutError,
        typesense.exceptions.TypesenseClientError,
        OSError,
    ) as e:
        _log_indexing_error(e)
    # Note: We intentionally don't re-raise - indexing failure shouldn't fail the build
