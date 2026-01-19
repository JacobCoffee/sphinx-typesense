"""Abstract base class for search backends.

This module defines the SearchBackend ABC that all search backend
implementations must inherit from.

"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from sphinx.util import logging

if TYPE_CHECKING:
    from sphinx.application import Sphinx

logger = logging.getLogger(__name__)


class SearchBackend(ABC):
    """Abstract base class for search backends.

    All search backends must implement:
        - index_all(): Index documentation content after build
        - get_js_files(): Return list of JS files to inject
        - get_css_files(): Return list of CSS files to inject
        - get_config_script(): Return inline JS config (or empty string)

    Attributes:
        app: The Sphinx application instance.
        name: Human-readable name of the backend.

    """

    name: str = "base"

    def __init__(self, app: Sphinx) -> None:
        """Initialize the backend with Sphinx app context.

        Args:
            app: The Sphinx application instance.

        """
        logger.debug("sphinx-typesense: Initializing %s backend", self.name)
        self.app = app

    @abstractmethod
    def index_all(self) -> int:
        """Index all documentation content.

        Called by Sphinx's build-finished event handler after
        the HTML build completes.

        Returns:
            Number of documents/pages indexed, or 0 if skipped.

        """
        ...

    @abstractmethod
    def get_js_files(self) -> list[tuple[str, dict[str, str | int]]]:
        """Return JavaScript files to inject.

        Returns:
            List of (filename, attributes) tuples for app.add_js_file().
            Attributes dict may include 'priority', 'defer', etc.

        Example:
            >>> backend.get_js_files()
            [("typesense-docsearch.js", {"priority": 500}),
             ("typesense-init.js", {"priority": 501})]

        """
        ...

    @abstractmethod
    def get_css_files(self) -> list[str]:
        """Return CSS files to inject.

        Returns:
            List of CSS filenames for app.add_css_file().

        Example:
            >>> backend.get_css_files()
            ["typesense-docsearch.css"]

        """
        ...

    def get_config_script(self) -> str:
        """Return inline JavaScript configuration.

        Override this to inject a config script into page context.
        Default implementation returns empty string (no inline script).

        Returns:
            JavaScript code to inject, or empty string.

        """
        return ""

    def is_available(self) -> bool:
        """Check if this backend is available/configured.

        Override this to perform availability checks (e.g., server
        connectivity for Typesense, CLI availability for Pagefind).

        Returns:
            True if backend is ready to use, False otherwise.

        """
        return True
