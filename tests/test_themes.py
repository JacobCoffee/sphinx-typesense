"""Tests for sphinx-typesense theme support.

This module tests:
    - Theme selector registries (THEME_SELECTORS, SEARCH_PLACEMENT_SELECTORS)
    - Theme configuration dataclass and registry (ThemeConfig, THEME_CONFIGS)
    - Theme detection and selector resolution functions
    - Sphinx application integration functions

Supported Themes Tested:
    - sphinx_rtd_theme (ReadTheDocs)
    - furo
    - alabaster
    - pydata_sphinx_theme
    - sphinx_book_theme
    - shibuya (if supported)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from sphinx_typesense import themes
from sphinx_typesense.themes import (
    DEFAULT_CONTENT_SELECTORS,
    DEFAULT_SEARCH_PLACEMENT,
    SEARCH_PLACEMENT_SELECTORS,
    THEME_CONFIGS,
    THEME_SELECTORS,
    ThemeConfig,
    get_content_selectors,
    get_content_selectors_for_app,
    get_search_placement,
    get_theme_config,
    should_replace_search,
)

if TYPE_CHECKING:
    from unittest.mock import MagicMock


# =============================================================================
# Theme Selector Registry Tests
# =============================================================================


class TestThemeSelectorsRegistry:
    """Tests for the THEME_SELECTORS dictionary."""

    def test_theme_selectors_is_dict(self) -> None:
        """Verify THEME_SELECTORS is a dictionary."""
        assert isinstance(THEME_SELECTORS, dict)

    def test_theme_selectors_not_empty(self) -> None:
        """Verify THEME_SELECTORS has entries."""
        assert len(THEME_SELECTORS) > 0

    def test_has_sphinx_rtd_theme(self) -> None:
        """Verify sphinx_rtd_theme is in THEME_SELECTORS."""
        assert "sphinx_rtd_theme" in THEME_SELECTORS

    def test_has_furo_theme(self) -> None:
        """Verify furo theme is in THEME_SELECTORS."""
        assert "furo" in THEME_SELECTORS

    def test_has_alabaster_theme(self) -> None:
        """Verify alabaster theme is in THEME_SELECTORS."""
        assert "alabaster" in THEME_SELECTORS

    def test_has_pydata_sphinx_theme(self) -> None:
        """Verify pydata_sphinx_theme is in THEME_SELECTORS."""
        assert "pydata_sphinx_theme" in THEME_SELECTORS

    def test_has_sphinx_book_theme(self) -> None:
        """Verify sphinx_book_theme is in THEME_SELECTORS."""
        assert "sphinx_book_theme" in THEME_SELECTORS

    def test_has_shibuya_theme(self) -> None:
        """Verify shibuya theme is in THEME_SELECTORS."""
        assert "shibuya" in THEME_SELECTORS

    def test_rtd_theme_selectors_are_list(self) -> None:
        """Verify RTD theme selectors is a list."""
        assert isinstance(THEME_SELECTORS["sphinx_rtd_theme"], list)

    def test_rtd_theme_selectors_not_empty(self) -> None:
        """Verify RTD theme has selectors defined."""
        assert len(THEME_SELECTORS["sphinx_rtd_theme"]) > 0

    def test_rtd_theme_includes_wy_nav_content(self) -> None:
        """Verify RTD theme includes expected selectors."""
        assert ".wy-nav-content-wrap" in THEME_SELECTORS["sphinx_rtd_theme"]

    def test_furo_theme_includes_article_main(self) -> None:
        """Verify Furo theme includes expected selectors."""
        assert "article[role=main]" in THEME_SELECTORS["furo"]

    def test_alabaster_theme_includes_body(self) -> None:
        """Verify Alabaster theme includes expected selectors."""
        assert ".body" in THEME_SELECTORS["alabaster"]

    def test_pydata_theme_includes_bd_article(self) -> None:
        """Verify PyData theme includes expected selectors."""
        assert "article.bd-article" in THEME_SELECTORS["pydata_sphinx_theme"]

    def test_shibuya_theme_includes_yue_main(self) -> None:
        """Verify Shibuya theme includes expected selectors."""
        assert "article.yue[role=main]" in THEME_SELECTORS["shibuya"]

    def test_all_theme_selectors_are_strings(self) -> None:
        """Verify all theme selectors are strings."""
        for theme_name, selectors in THEME_SELECTORS.items():
            for selector in selectors:
                assert isinstance(selector, str), f"Selector in {theme_name} is not a string: {selector}"


# =============================================================================
# Search Placement Selectors Tests
# =============================================================================


class TestSearchPlacementSelectorsRegistry:
    """Tests for the SEARCH_PLACEMENT_SELECTORS dictionary."""

    def test_search_placement_selectors_is_dict(self) -> None:
        """Verify SEARCH_PLACEMENT_SELECTORS is a dictionary."""
        assert isinstance(SEARCH_PLACEMENT_SELECTORS, dict)

    def test_search_placement_selectors_not_empty(self) -> None:
        """Verify SEARCH_PLACEMENT_SELECTORS has entries."""
        assert len(SEARCH_PLACEMENT_SELECTORS) > 0

    def test_has_sphinx_rtd_theme_search(self) -> None:
        """Verify sphinx_rtd_theme search placement is defined."""
        assert "sphinx_rtd_theme" in SEARCH_PLACEMENT_SELECTORS

    def test_has_furo_theme_search(self) -> None:
        """Verify furo theme search placement is defined."""
        assert "furo" in SEARCH_PLACEMENT_SELECTORS

    def test_has_alabaster_theme_search(self) -> None:
        """Verify alabaster theme search placement is defined."""
        assert "alabaster" in SEARCH_PLACEMENT_SELECTORS

    def test_has_pydata_sphinx_theme_search(self) -> None:
        """Verify pydata_sphinx_theme search placement is defined."""
        assert "pydata_sphinx_theme" in SEARCH_PLACEMENT_SELECTORS

    def test_has_sphinx_book_theme_search(self) -> None:
        """Verify sphinx_book_theme search placement is defined."""
        assert "sphinx_book_theme" in SEARCH_PLACEMENT_SELECTORS

    def test_has_shibuya_theme_search(self) -> None:
        """Verify shibuya theme search placement is defined."""
        assert "shibuya" in SEARCH_PLACEMENT_SELECTORS

    def test_rtd_theme_search_selector(self) -> None:
        """Verify RTD theme search placement selector."""
        assert SEARCH_PLACEMENT_SELECTORS["sphinx_rtd_theme"] == ".wy-side-nav-search"

    def test_furo_theme_search_selector(self) -> None:
        """Verify Furo theme search placement selector."""
        assert SEARCH_PLACEMENT_SELECTORS["furo"] == ".sidebar-search-container"

    def test_shibuya_theme_search_selector(self) -> None:
        """Verify Shibuya theme search placement selector."""
        assert SEARCH_PLACEMENT_SELECTORS["shibuya"] == ".searchbox"

    def test_all_search_selectors_are_strings(self) -> None:
        """Verify all search placement selectors are strings."""
        for theme_name, selector in SEARCH_PLACEMENT_SELECTORS.items():
            assert isinstance(selector, str), f"Search selector for {theme_name} is not a string"


# =============================================================================
# Theme Configuration Tests
# =============================================================================


class TestThemeConfigDataclass:
    """Tests for the ThemeConfig dataclass."""

    def test_theme_config_creation(self) -> None:
        """Verify ThemeConfig can be instantiated."""
        config = ThemeConfig(
            name="test_theme",
            content_selectors=(".content", ".main"),
            search_container_selectors=(".search",),
        )
        assert config.name == "test_theme"
        assert config.content_selectors == (".content", ".main")
        assert config.search_container_selectors == (".search",)

    def test_theme_config_default_search_input_selector(self) -> None:
        """Verify ThemeConfig search_input_selector defaults to None."""
        config = ThemeConfig(
            name="test_theme",
            content_selectors=(".content",),
            search_container_selectors=(".search",),
        )
        assert config.search_input_selector is None

    def test_theme_config_custom_search_input_selector(self) -> None:
        """Verify ThemeConfig accepts custom search_input_selector."""
        config = ThemeConfig(
            name="test_theme",
            content_selectors=(".content",),
            search_container_selectors=(".search",),
            search_input_selector='input[name="q"]',
        )
        assert config.search_input_selector == 'input[name="q"]'

    def test_theme_config_is_frozen(self) -> None:
        """Verify ThemeConfig is immutable (frozen dataclass)."""
        config = ThemeConfig(
            name="test_theme",
            content_selectors=(".content",),
            search_container_selectors=(".search",),
        )
        with pytest.raises(AttributeError):
            config.name = "modified"  # type: ignore[misc]


class TestThemeConfigsRegistry:
    """Tests for the THEME_CONFIGS dictionary."""

    def test_theme_configs_is_dict(self) -> None:
        """Verify THEME_CONFIGS is a dictionary."""
        assert isinstance(THEME_CONFIGS, dict)

    def test_theme_configs_not_empty(self) -> None:
        """Verify THEME_CONFIGS has entries."""
        assert len(THEME_CONFIGS) > 0

    def test_has_sphinx_rtd_theme_config(self) -> None:
        """Verify sphinx_rtd_theme has a ThemeConfig entry."""
        assert "sphinx_rtd_theme" in THEME_CONFIGS
        assert isinstance(THEME_CONFIGS["sphinx_rtd_theme"], ThemeConfig)

    def test_has_furo_theme_config(self) -> None:
        """Verify furo theme has a ThemeConfig entry."""
        assert "furo" in THEME_CONFIGS
        assert isinstance(THEME_CONFIGS["furo"], ThemeConfig)

    def test_has_alabaster_theme_config(self) -> None:
        """Verify alabaster theme has a ThemeConfig entry."""
        assert "alabaster" in THEME_CONFIGS
        assert isinstance(THEME_CONFIGS["alabaster"], ThemeConfig)

    def test_has_pydata_sphinx_theme_config(self) -> None:
        """Verify pydata_sphinx_theme has a ThemeConfig entry."""
        assert "pydata_sphinx_theme" in THEME_CONFIGS
        assert isinstance(THEME_CONFIGS["pydata_sphinx_theme"], ThemeConfig)

    def test_has_sphinx_book_theme_config(self) -> None:
        """Verify sphinx_book_theme has a ThemeConfig entry."""
        assert "sphinx_book_theme" in THEME_CONFIGS
        assert isinstance(THEME_CONFIGS["sphinx_book_theme"], ThemeConfig)

    def test_has_shibuya_theme_config(self) -> None:
        """Verify shibuya theme has a ThemeConfig entry."""
        assert "shibuya" in THEME_CONFIGS
        assert isinstance(THEME_CONFIGS["shibuya"], ThemeConfig)

    def test_rtd_theme_config_name(self) -> None:
        """Verify RTD theme config has correct name."""
        assert THEME_CONFIGS["sphinx_rtd_theme"].name == "sphinx_rtd_theme"

    def test_rtd_theme_config_has_content_selectors(self) -> None:
        """Verify RTD theme config has content selectors."""
        assert len(THEME_CONFIGS["sphinx_rtd_theme"].content_selectors) > 0

    def test_rtd_theme_config_has_search_container_selectors(self) -> None:
        """Verify RTD theme config has search container selectors."""
        assert len(THEME_CONFIGS["sphinx_rtd_theme"].search_container_selectors) > 0

    def test_rtd_theme_config_has_search_input_selector(self) -> None:
        """Verify RTD theme config has search input selector."""
        assert THEME_CONFIGS["sphinx_rtd_theme"].search_input_selector is not None

    def test_all_theme_configs_are_valid(self) -> None:
        """Verify all theme configs have required attributes."""
        for theme_name, config in THEME_CONFIGS.items():
            assert isinstance(config, ThemeConfig), f"Config for {theme_name} is not ThemeConfig"
            assert config.name == theme_name, f"Config name mismatch for {theme_name}"
            assert len(config.content_selectors) > 0, f"No content selectors for {theme_name}"
            assert len(config.search_container_selectors) > 0, f"No search container selectors for {theme_name}"


# =============================================================================
# get_content_selectors Function Tests
# =============================================================================


class TestGetContentSelectors:
    """Tests for the get_content_selectors() function."""

    def test_returns_list(self) -> None:
        """Verify get_content_selectors returns a list."""
        result = get_content_selectors()
        assert isinstance(result, list)

    def test_returns_theme_specific_selectors_for_known_theme(self) -> None:
        """Verify theme-specific selectors are returned for known themes."""
        result = get_content_selectors("sphinx_rtd_theme")
        assert result == THEME_SELECTORS["sphinx_rtd_theme"]

    def test_returns_furo_selectors(self) -> None:
        """Verify Furo theme selectors are returned."""
        result = get_content_selectors("furo")
        assert "article[role=main]" in result

    def test_returns_alabaster_selectors(self) -> None:
        """Verify Alabaster theme selectors are returned."""
        result = get_content_selectors("alabaster")
        assert ".body" in result

    def test_returns_pydata_selectors(self) -> None:
        """Verify PyData theme selectors are returned."""
        result = get_content_selectors("pydata_sphinx_theme")
        assert "article.bd-article" in result

    def test_returns_book_theme_selectors(self) -> None:
        """Verify Book theme selectors are returned."""
        result = get_content_selectors("sphinx_book_theme")
        assert "main#main-content" in result

    def test_returns_shibuya_selectors(self) -> None:
        """Verify Shibuya theme selectors are returned."""
        result = get_content_selectors("shibuya")
        assert "article.yue[role=main]" in result

    def test_returns_custom_selectors_when_provided(self) -> None:
        """Verify custom selectors override theme defaults."""
        custom = [".my-custom-content", "article.main"]
        result = get_content_selectors("furo", custom_selectors=custom)
        assert result == custom

    def test_custom_selectors_override_known_theme(self) -> None:
        """Verify custom selectors take precedence over known theme."""
        custom = [".custom"]
        result = get_content_selectors("sphinx_rtd_theme", custom_selectors=custom)
        assert result == custom
        assert ".wy-nav-content-wrap" not in result

    def test_returns_default_selectors_for_unknown_theme(self) -> None:
        """Verify default selectors are returned for unknown themes."""
        result = get_content_selectors("unknown_theme_xyz")
        assert result == DEFAULT_CONTENT_SELECTORS

    def test_returns_default_selectors_for_none_theme(self) -> None:
        """Verify default selectors are returned when theme is None."""
        result = get_content_selectors(None)
        assert result == DEFAULT_CONTENT_SELECTORS

    def test_returns_default_selectors_for_empty_string_theme(self) -> None:
        """Verify default selectors are returned for empty string theme."""
        result = get_content_selectors("")
        assert result == DEFAULT_CONTENT_SELECTORS

    def test_returns_copy_not_original(self) -> None:
        """Verify a copy is returned, not the original list."""
        result = get_content_selectors("furo")
        original = THEME_SELECTORS["furo"]
        assert result is not original
        # Modify result should not affect original
        result.append(".modified")
        assert ".modified" not in THEME_SELECTORS["furo"]


# =============================================================================
# get_search_placement Function Tests
# =============================================================================


class TestGetSearchPlacement:
    """Tests for the get_search_placement() function."""

    def test_returns_string(self) -> None:
        """Verify get_search_placement returns a string."""
        result = get_search_placement()
        assert isinstance(result, str)

    def test_returns_theme_specific_placement_for_known_theme(self) -> None:
        """Verify theme-specific placement is returned for known themes."""
        result = get_search_placement("sphinx_rtd_theme")
        assert result == ".wy-side-nav-search"

    def test_returns_furo_placement(self) -> None:
        """Verify Furo theme placement is returned."""
        result = get_search_placement("furo")
        assert result == ".sidebar-search-container"

    def test_returns_alabaster_placement(self) -> None:
        """Verify Alabaster theme placement is returned."""
        result = get_search_placement("alabaster")
        assert result == ".searchbox"

    def test_returns_pydata_placement(self) -> None:
        """Verify PyData theme placement is returned."""
        result = get_search_placement("pydata_sphinx_theme")
        assert result == "nav.bd-search"

    def test_returns_book_theme_placement(self) -> None:
        """Verify Book theme placement is returned."""
        result = get_search_placement("sphinx_book_theme")
        assert result == ".search-button-field"

    def test_returns_shibuya_placement(self) -> None:
        """Verify Shibuya theme placement is returned."""
        result = get_search_placement("shibuya")
        assert result == ".searchbox"

    def test_returns_default_placement_for_unknown_theme(self) -> None:
        """Verify default placement is returned for unknown themes."""
        result = get_search_placement("unknown_theme_xyz")
        assert result == DEFAULT_SEARCH_PLACEMENT

    def test_returns_default_placement_for_none_theme(self) -> None:
        """Verify default placement is returned when theme is None."""
        result = get_search_placement(None)
        assert result == DEFAULT_SEARCH_PLACEMENT

    def test_returns_default_placement_for_empty_string_theme(self) -> None:
        """Verify default placement is returned for empty string theme."""
        result = get_search_placement("")
        assert result == DEFAULT_SEARCH_PLACEMENT


# =============================================================================
# get_theme_config Function Tests
# =============================================================================


class TestGetThemeConfig:
    """Tests for the get_theme_config() function with mock Sphinx app."""

    def test_returns_theme_config(self, mock_sphinx_app: MagicMock) -> None:
        """Verify get_theme_config returns a ThemeConfig instance."""
        result = get_theme_config(mock_sphinx_app)
        assert isinstance(result, ThemeConfig)

    def test_returns_config_for_known_theme(self, mock_sphinx_app: MagicMock) -> None:
        """Verify correct config is returned for known themes."""
        mock_sphinx_app.config.html_theme = "sphinx_rtd_theme"
        result = get_theme_config(mock_sphinx_app)
        assert result.name == "sphinx_rtd_theme"

    def test_returns_furo_config(self, mock_sphinx_app: MagicMock) -> None:
        """Verify Furo theme config is returned."""
        mock_sphinx_app.config.html_theme = "furo"
        result = get_theme_config(mock_sphinx_app)
        assert result.name == "furo"

    def test_returns_alabaster_config(self, mock_sphinx_app: MagicMock) -> None:
        """Verify Alabaster theme config is returned."""
        mock_sphinx_app.config.html_theme = "alabaster"
        result = get_theme_config(mock_sphinx_app)
        assert result.name == "alabaster"

    def test_returns_pydata_config(self, mock_sphinx_app: MagicMock) -> None:
        """Verify PyData theme config is returned."""
        mock_sphinx_app.config.html_theme = "pydata_sphinx_theme"
        result = get_theme_config(mock_sphinx_app)
        assert result.name == "pydata_sphinx_theme"

    def test_returns_book_theme_config(self, mock_sphinx_app: MagicMock) -> None:
        """Verify Book theme config is returned."""
        mock_sphinx_app.config.html_theme = "sphinx_book_theme"
        result = get_theme_config(mock_sphinx_app)
        assert result.name == "sphinx_book_theme"

    def test_returns_shibuya_config(self, mock_sphinx_app: MagicMock) -> None:
        """Verify Shibuya theme config is returned."""
        mock_sphinx_app.config.html_theme = "shibuya"
        result = get_theme_config(mock_sphinx_app)
        assert result.name == "shibuya"

    def test_returns_default_config_for_unknown_theme(self, mock_sphinx_app: MagicMock) -> None:
        """Verify default config is returned for unknown themes."""
        mock_sphinx_app.config.html_theme = "unknown_theme_xyz"
        result = get_theme_config(mock_sphinx_app)
        assert result.name == "default"

    def test_returns_default_config_when_html_theme_is_none(self, mock_sphinx_app: MagicMock) -> None:
        """Verify default config is returned when html_theme is None."""
        mock_sphinx_app.config.html_theme = None
        result = get_theme_config(mock_sphinx_app)
        assert result.name == "default"

    def test_default_config_has_content_selectors(self, mock_sphinx_app: MagicMock) -> None:
        """Verify default config has content selectors."""
        mock_sphinx_app.config.html_theme = "unknown_theme"
        result = get_theme_config(mock_sphinx_app)
        assert len(result.content_selectors) > 0

    def test_default_config_has_search_container_selectors(self, mock_sphinx_app: MagicMock) -> None:
        """Verify default config has search container selectors."""
        mock_sphinx_app.config.html_theme = "unknown_theme"
        result = get_theme_config(mock_sphinx_app)
        assert len(result.search_container_selectors) > 0


# =============================================================================
# get_content_selectors_for_app Function Tests
# =============================================================================


class TestGetContentSelectorsForApp:
    """Tests for the get_content_selectors_for_app() function with mock Sphinx app."""

    def test_returns_list(self, mock_sphinx_app: MagicMock) -> None:
        """Verify get_content_selectors_for_app returns a list."""
        result = get_content_selectors_for_app(mock_sphinx_app)
        assert isinstance(result, list)

    def test_returns_custom_selectors_when_configured(self, mock_sphinx_app: MagicMock) -> None:
        """Verify user-configured selectors are returned when set."""
        mock_sphinx_app.config.typesense_content_selectors = [".custom-content", ".my-docs"]
        result = get_content_selectors_for_app(mock_sphinx_app)
        assert result == [".custom-content", ".my-docs"]

    def test_returns_theme_selectors_when_no_custom(self, mock_sphinx_app: MagicMock) -> None:
        """Verify theme selectors are returned when no custom selectors set."""
        mock_sphinx_app.config.typesense_content_selectors = None
        mock_sphinx_app.config.html_theme = "furo"
        result = get_content_selectors_for_app(mock_sphinx_app)
        assert "article[role=main]" in result

    def test_custom_selectors_override_theme(self, mock_sphinx_app: MagicMock) -> None:
        """Verify custom selectors take precedence over theme selectors."""
        mock_sphinx_app.config.typesense_content_selectors = [".override"]
        mock_sphinx_app.config.html_theme = "sphinx_rtd_theme"
        result = get_content_selectors_for_app(mock_sphinx_app)
        assert result == [".override"]
        assert ".wy-nav-content-wrap" not in result

    def test_returns_default_selectors_for_unknown_theme(self, mock_sphinx_app: MagicMock) -> None:
        """Verify default selectors are returned for unknown themes."""
        mock_sphinx_app.config.typesense_content_selectors = None
        mock_sphinx_app.config.html_theme = "unknown_theme_xyz"
        result = get_content_selectors_for_app(mock_sphinx_app)
        assert result == DEFAULT_CONTENT_SELECTORS

    def test_handles_empty_custom_selectors_list(self, mock_sphinx_app: MagicMock) -> None:
        """Verify empty custom selectors list falls back to theme defaults."""
        mock_sphinx_app.config.typesense_content_selectors = []
        mock_sphinx_app.config.html_theme = "furo"
        result = get_content_selectors_for_app(mock_sphinx_app)
        # Empty list is falsy, so should use theme-based detection
        assert "article[role=main]" in result


# =============================================================================
# should_replace_search Function Tests
# =============================================================================


class TestShouldReplaceSearch:
    """Tests for the should_replace_search() function."""

    def test_returns_bool(self, mock_sphinx_app: MagicMock) -> None:
        """Verify should_replace_search returns a boolean."""
        result = should_replace_search(mock_sphinx_app)
        assert isinstance(result, bool)

    def test_respects_explicit_true_configuration(self, mock_sphinx_app: MagicMock) -> None:
        """Verify explicit True configuration is respected."""
        mock_sphinx_app.config.typesense_replace_search = True
        mock_sphinx_app.config.html_theme = "unknown_theme"
        result = should_replace_search(mock_sphinx_app)
        assert result is True

    def test_respects_explicit_false_configuration(self, mock_sphinx_app: MagicMock) -> None:
        """Verify explicit False configuration is respected."""
        mock_sphinx_app.config.typesense_replace_search = False
        mock_sphinx_app.config.html_theme = "sphinx_rtd_theme"
        result = should_replace_search(mock_sphinx_app)
        assert result is False

    def test_returns_true_for_supported_themes_without_config(self, mock_sphinx_app: MagicMock) -> None:
        """Verify True is returned for supported themes when not explicitly configured."""
        mock_sphinx_app.config.typesense_replace_search = None
        for theme_name in THEME_CONFIGS:
            mock_sphinx_app.config.html_theme = theme_name
            result = should_replace_search(mock_sphinx_app)
            assert result is True, f"Expected True for {theme_name}"

    def test_returns_false_for_unknown_themes_without_config(self, mock_sphinx_app: MagicMock) -> None:
        """Verify False is returned for unknown themes when not explicitly configured."""
        mock_sphinx_app.config.typesense_replace_search = None
        mock_sphinx_app.config.html_theme = "unknown_theme_xyz"
        result = should_replace_search(mock_sphinx_app)
        assert result is False

    def test_returns_true_for_none_theme_without_config(self, mock_sphinx_app: MagicMock) -> None:
        """Verify True is returned when theme is None (per implementation)."""
        mock_sphinx_app.config.typesense_replace_search = None
        mock_sphinx_app.config.html_theme = None
        result = should_replace_search(mock_sphinx_app)
        assert result is True


# =============================================================================
# Default Constants Tests
# =============================================================================


class TestDefaultConstants:
    """Tests for default constant values."""

    def test_default_content_selectors_is_list(self) -> None:
        """Verify DEFAULT_CONTENT_SELECTORS is a list."""
        assert isinstance(DEFAULT_CONTENT_SELECTORS, list)

    def test_default_content_selectors_not_empty(self) -> None:
        """Verify DEFAULT_CONTENT_SELECTORS has entries."""
        assert len(DEFAULT_CONTENT_SELECTORS) > 0

    def test_default_content_selectors_includes_common_selectors(self) -> None:
        """Verify DEFAULT_CONTENT_SELECTORS includes commonly used selectors."""
        assert "article[role=main]" in DEFAULT_CONTENT_SELECTORS
        assert "main" in DEFAULT_CONTENT_SELECTORS
        assert ".body" in DEFAULT_CONTENT_SELECTORS

    def test_default_search_placement_is_string(self) -> None:
        """Verify DEFAULT_SEARCH_PLACEMENT is a string."""
        assert isinstance(DEFAULT_SEARCH_PLACEMENT, str)

    def test_default_search_placement_value(self) -> None:
        """Verify DEFAULT_SEARCH_PLACEMENT has expected value."""
        assert DEFAULT_SEARCH_PLACEMENT == "#typesense-search"


# =============================================================================
# Module Import Tests
# =============================================================================


class TestModuleImports:
    """Tests for the themes module imports and structure."""

    def test_module_imports(self) -> None:
        """Verify the themes module can be imported."""
        assert themes is not None

    def test_theme_selectors_exported(self) -> None:
        """Verify THEME_SELECTORS is exported from module."""
        assert hasattr(themes, "THEME_SELECTORS")

    def test_search_placement_selectors_exported(self) -> None:
        """Verify SEARCH_PLACEMENT_SELECTORS is exported from module."""
        assert hasattr(themes, "SEARCH_PLACEMENT_SELECTORS")

    def test_theme_configs_exported(self) -> None:
        """Verify THEME_CONFIGS is exported from module."""
        assert hasattr(themes, "THEME_CONFIGS")

    def test_theme_config_class_exported(self) -> None:
        """Verify ThemeConfig class is exported from module."""
        assert hasattr(themes, "ThemeConfig")

    def test_get_content_selectors_exported(self) -> None:
        """Verify get_content_selectors function is exported."""
        assert hasattr(themes, "get_content_selectors")
        assert callable(themes.get_content_selectors)

    def test_get_search_placement_exported(self) -> None:
        """Verify get_search_placement function is exported."""
        assert hasattr(themes, "get_search_placement")
        assert callable(themes.get_search_placement)

    def test_get_theme_config_exported(self) -> None:
        """Verify get_theme_config function is exported."""
        assert hasattr(themes, "get_theme_config")
        assert callable(themes.get_theme_config)

    def test_get_content_selectors_for_app_exported(self) -> None:
        """Verify get_content_selectors_for_app function is exported."""
        assert hasattr(themes, "get_content_selectors_for_app")
        assert callable(themes.get_content_selectors_for_app)

    def test_should_replace_search_exported(self) -> None:
        """Verify should_replace_search function is exported."""
        assert hasattr(themes, "should_replace_search")
        assert callable(themes.should_replace_search)
