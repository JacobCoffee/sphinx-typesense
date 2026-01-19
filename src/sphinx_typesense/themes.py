"""Theme-specific selectors and configuration for sphinx-typesense.

This module provides content selectors and search bar placement logic
for various Sphinx themes, enabling automatic detection and proper
integration without manual configuration.

Supported Themes:
    - sphinx_rtd_theme (ReadTheDocs)
    - furo
    - alabaster
    - pydata_sphinx_theme
    - sphinx_book_theme
    - shibuya

Usage:
    Theme detection is automatic based on the configured html_theme.
    Custom selectors can override defaults via typesense_content_selectors.

Example:
    Override selectors in conf.py::

        typesense_content_selectors = [
            ".my-custom-content",
            "article.main",
        ]

"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from sphinx.util import logging

if TYPE_CHECKING:
    from collections.abc import Sequence

    from sphinx.application import Sphinx

logger = logging.getLogger(__name__)


# =============================================================================
# Theme Content Selectors Registry
# =============================================================================
# CSS selectors for extracting main content area from each theme.
# Listed in priority order - first match wins.

THEME_SELECTORS: dict[str, list[str]] = {
    "sphinx_rtd_theme": [".wy-nav-content-wrap", ".wy-nav-content", "[role=main]"],
    "furo": ["article[role=main]", ".content"],
    "alabaster": [".body", ".document"],
    "pydata_sphinx_theme": ["article.bd-article", "main.bd-main", "main.bd-content"],
    "sphinx_book_theme": ["main#main-content", "article", "article.bd-article"],
    "shibuya": ["article.yue[role=main]", "article[role=main]", "main.sy-main"],
}

# =============================================================================
# Search Bar Placement Selectors
# =============================================================================
# CSS selectors for where to inject the Typesense search bar in each theme.

SEARCH_PLACEMENT_SELECTORS: dict[str, str] = {
    "sphinx_rtd_theme": ".wy-side-nav-search",
    "furo": ".sidebar-search-container",
    "alabaster": ".searchbox",
    "pydata_sphinx_theme": "nav.bd-search",
    "sphinx_book_theme": ".search-button-field",
    "shibuya": ".searchbox",
}

# =============================================================================
# Default Fallback Selectors
# =============================================================================
# Used when theme is not recognized or custom selectors are not provided.

DEFAULT_CONTENT_SELECTORS: list[str] = [
    "article[role=main]",
    "main",
    ".body",
    ".document",
    "[role=main]",
]

DEFAULT_SEARCH_PLACEMENT: str = "#typesense-search"

DEFAULT_SEARCH_CONTAINER_SELECTORS: tuple[str, ...] = (
    "#typesense-search",
    ".search",
    ".searchbox",
)


# =============================================================================
# Theme Configuration Dataclass
# =============================================================================


@dataclass(frozen=True)
class ThemeConfig:
    """Configuration for a specific Sphinx theme.

    Attributes:
        name: Theme package name (e.g., "sphinx_rtd_theme").
        content_selectors: CSS selectors for main content area.
        search_container_selectors: CSS selectors for search bar placement.
        search_input_selector: CSS selector for existing search input.

    """

    name: str
    content_selectors: tuple[str, ...]
    search_container_selectors: tuple[str, ...]
    search_input_selector: str | None = None


# Full theme configurations with all details
THEME_CONFIGS: dict[str, ThemeConfig] = {
    "sphinx_rtd_theme": ThemeConfig(
        name="sphinx_rtd_theme",
        content_selectors=(".wy-nav-content-wrap", ".wy-nav-content", "[role=main]"),
        search_container_selectors=(".wy-side-nav-search",),
        search_input_selector='input[name="q"]',
    ),
    "furo": ThemeConfig(
        name="furo",
        content_selectors=("article[role=main]", ".content"),
        search_container_selectors=(".sidebar-search-container",),
        search_input_selector=".search-input",
    ),
    "alabaster": ThemeConfig(
        name="alabaster",
        content_selectors=(".body", ".document"),
        search_container_selectors=(".searchbox",),
        search_input_selector='input[name="q"]',
    ),
    "pydata_sphinx_theme": ThemeConfig(
        name="pydata_sphinx_theme",
        content_selectors=("article.bd-article", "main.bd-content"),
        search_container_selectors=("nav.bd-search", ".bd-search"),
        search_input_selector='input[name="q"]',
    ),
    "sphinx_book_theme": ThemeConfig(
        name="sphinx_book_theme",
        content_selectors=("main#main-content", "article.bd-article"),
        search_container_selectors=(".search-button-field",),
        search_input_selector='input[name="q"]',
    ),
    "shibuya": ThemeConfig(
        name="shibuya",
        content_selectors=("article.yue[role=main]", "article[role=main]", "main.sy-main"),
        search_container_selectors=(".searchbox",),
        search_input_selector='input[name="q"]',
    ),
}


# =============================================================================
# Helper Functions
# =============================================================================


def get_content_selectors(
    theme_name: str | None = None,
    custom_selectors: Sequence[str] | None = None,
) -> list[str]:
    """Get content selectors for a theme with optional custom overrides.

    Returns custom selectors if provided, otherwise theme-specific selectors
    if the theme is recognized, otherwise the default fallback selectors.

    Args:
        theme_name: The Sphinx theme name (e.g., "furo", "sphinx_rtd_theme").
        custom_selectors: User-provided custom CSS selectors to use instead
            of theme defaults.

    Returns:
        List of CSS selectors in priority order for extracting main content.

    Example:
        >>> get_content_selectors("furo")
        ['article[role=main]', '.content']
        >>> get_content_selectors("furo", [".my-content"])
        ['.my-content']
        >>> get_content_selectors("unknown_theme")
        ['article[role=main]', 'main', '.body', '.document', '[role=main]']

    """
    logger.debug("sphinx-typesense: Getting content selectors for theme=%s", theme_name)

    # Custom selectors take highest priority
    if custom_selectors is not None:
        logger.debug("sphinx-typesense: Using custom selectors: %s", custom_selectors)
        return list(custom_selectors)

    # Theme-specific selectors
    if theme_name and theme_name in THEME_SELECTORS:
        selectors = THEME_SELECTORS[theme_name]
        logger.debug("sphinx-typesense: Using theme-specific selectors for %s: %s", theme_name, selectors)
        return list(selectors)

    # Default fallback
    logger.debug("sphinx-typesense: Using default fallback selectors: %s", DEFAULT_CONTENT_SELECTORS)
    return list(DEFAULT_CONTENT_SELECTORS)


def get_search_placement(theme_name: str | None = None) -> str:
    """Get the CSS selector for search bar placement.

    Returns the appropriate CSS selector for where to place the Typesense
    search bar based on the detected theme.

    Args:
        theme_name: The Sphinx theme name (e.g., "furo", "sphinx_rtd_theme").

    Returns:
        CSS selector string for search bar container placement.

    Example:
        >>> get_search_placement("sphinx_rtd_theme")
        '.wy-side-nav-search'
        >>> get_search_placement("unknown_theme")
        '#typesense-search'

    """
    logger.debug("sphinx-typesense: Getting search placement for theme=%s", theme_name)
    if theme_name and theme_name in SEARCH_PLACEMENT_SELECTORS:
        placement = SEARCH_PLACEMENT_SELECTORS[theme_name]
        logger.debug("sphinx-typesense: Using theme-specific search placement: %s", placement)
        return placement
    logger.debug("sphinx-typesense: Using default search placement: %s", DEFAULT_SEARCH_PLACEMENT)
    return DEFAULT_SEARCH_PLACEMENT


# =============================================================================
# Sphinx Integration Functions
# =============================================================================


def get_theme_config(app: Sphinx) -> ThemeConfig:
    """Get theme configuration for the current Sphinx build.

    Detects the configured HTML theme and returns the appropriate
    ThemeConfig with all selectors and settings.

    Args:
        app: The Sphinx application instance.

    Returns:
        ThemeConfig for the detected theme, or a default config.

    """
    theme_name = getattr(app.config, "html_theme", None)
    logger.debug("sphinx-typesense: Detected html_theme=%s", theme_name)

    if theme_name and theme_name in THEME_CONFIGS:
        logger.debug("sphinx-typesense: Using theme configuration for: %s", theme_name)
        return THEME_CONFIGS[theme_name]

    if theme_name:
        logger.warning(
            "sphinx-typesense: Theme '%s' not in supported themes, using default selectors. Supported themes: %s",
            theme_name,
            ", ".join(sorted(THEME_CONFIGS.keys())),
        )
    else:
        logger.debug("sphinx-typesense: No html_theme configured, using default configuration")

    return _get_default_config()


def _get_default_config() -> ThemeConfig:
    """Create a default theme configuration.

    Returns:
        ThemeConfig with generic selectors suitable for unknown themes.

    """
    logger.debug("sphinx-typesense: Creating default theme configuration")
    return ThemeConfig(
        name="default",
        content_selectors=tuple(DEFAULT_CONTENT_SELECTORS),
        search_container_selectors=DEFAULT_SEARCH_CONTAINER_SELECTORS,
        search_input_selector=None,
    )


def get_content_selectors_for_app(app: Sphinx) -> list[str]:
    """Get content selectors for the current Sphinx application.

    Returns user-configured selectors if set, otherwise
    theme-specific or default selectors.

    Args:
        app: The Sphinx application instance.

    Returns:
        List of CSS selectors in priority order.

    """
    logger.debug("sphinx-typesense: Getting content selectors for application")

    # Check for user-configured custom selectors
    custom_selectors = getattr(app.config, "typesense_content_selectors", None)
    if custom_selectors:
        logger.debug("sphinx-typesense: Using user-configured custom selectors: %s", custom_selectors)
        return list(custom_selectors)

    # Use theme-based detection
    theme_name = getattr(app.config, "html_theme", None)
    logger.debug("sphinx-typesense: Falling back to theme-based selectors for theme=%s", theme_name)
    return get_content_selectors(theme_name)


def get_search_container_selector(app: Sphinx) -> str:
    """Get the best selector for search container placement.

    Args:
        app: The Sphinx application instance.

    Returns:
        CSS selector for search container placement.

    """
    theme_name = getattr(app.config, "html_theme", None)
    logger.debug("sphinx-typesense: Getting search container selector for theme=%s", theme_name)
    selector = get_search_placement(theme_name)
    logger.debug("sphinx-typesense: Search container selector: %s", selector)
    return selector


def should_replace_search(app: Sphinx) -> bool:
    """Determine if the default search should be replaced.

    Some themes may benefit from replacing their search input
    entirely, while others work better with an additional search.

    Args:
        app: The Sphinx application instance.

    Returns:
        True if default search should be replaced.

    """
    logger.debug("sphinx-typesense: Determining if default search should be replaced")

    # Check for explicit configuration
    replace_config = getattr(app.config, "typesense_replace_search", None)
    if replace_config is not None:
        logger.debug("sphinx-typesense: Using explicit typesense_replace_search=%s", replace_config)
        return bool(replace_config)

    # Default: replace search for all supported themes
    theme_name = getattr(app.config, "html_theme", None)
    should_replace = theme_name in THEME_CONFIGS or theme_name is None
    logger.debug(
        "sphinx-typesense: should_replace_search=%s (theme=%s, in_supported=%s)",
        should_replace,
        theme_name,
        theme_name in THEME_CONFIGS if theme_name else "N/A",
    )
    return should_replace
