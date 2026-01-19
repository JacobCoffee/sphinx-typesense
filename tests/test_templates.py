"""Tests for sphinx-typesense template and asset injection.

This module tests:
    - Search container HTML generation
    - JavaScript configuration injection for both backends
    - Backend-specific asset selection
    - CSP-compliant meta tag injection for both backends
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest

from sphinx_typesense import templates
from sphinx_typesense.templates import (
    add_search_meta_tags,
    get_config_script,
    get_pagefind_config_script,
    get_search_container_html,
    get_typesense_config_script,
    inject_search_assets,
)

if TYPE_CHECKING:
    from unittest.mock import MagicMock


class TestTemplatesModule:
    """Tests for the templates module imports and structure."""

    def test_module_imports(self) -> None:
        """Verify the templates module can be imported."""
        assert templates is not None

    def test_inject_search_assets_exists(self) -> None:
        """Verify inject_search_assets function is defined."""
        assert callable(inject_search_assets)

    def test_get_search_container_html_exists(self) -> None:
        """Verify get_search_container_html function is defined."""
        assert callable(get_search_container_html)

    def test_get_config_script_exists(self) -> None:
        """Verify get_config_script function is defined."""
        assert callable(get_config_script)

    def test_get_typesense_config_script_exists(self) -> None:
        """Verify get_typesense_config_script function is defined."""
        assert callable(get_typesense_config_script)

    def test_get_pagefind_config_script_exists(self) -> None:
        """Verify get_pagefind_config_script function is defined."""
        assert callable(get_pagefind_config_script)

    def test_add_search_meta_tags_exists(self) -> None:
        """Verify add_search_meta_tags function is defined."""
        assert callable(add_search_meta_tags)


class TestInjectSearchAssets:
    """Tests for the inject_search_assets function."""

    def test_inject_search_assets_signature(self, mock_sphinx_app: MagicMock) -> None:
        """Verify inject_search_assets has correct signature."""
        context: dict[str, Any] = {}

        # Should not raise with valid parameters
        inject_search_assets(
            app=mock_sphinx_app,
            pagename="index",
            templatename="page.html",
            context=context,
            doctree=None,
        )

    def test_inject_search_assets_accepts_none_doctree(self, mock_sphinx_app: MagicMock) -> None:
        """Verify function handles None doctree (e.g., for genindex)."""
        context: dict[str, Any] = {}
        inject_search_assets(mock_sphinx_app, "genindex", "genindex.html", context, None)

    def test_inject_search_assets_adds_typesense_search_html(self, mock_sphinx_app: MagicMock) -> None:
        """Verify context is modified to include search HTML."""
        context: dict[str, Any] = {}
        inject_search_assets(mock_sphinx_app, "index", "page.html", context, None)
        assert "typesense_search_html" in context
        assert isinstance(context["typesense_search_html"], str)

    def test_inject_search_assets_typesense_backend(self, mock_sphinx_app: MagicMock) -> None:
        """Verify Typesense backend produces TYPESENSE_CONFIG."""
        mock_sphinx_app.config.typesense_backend = "typesense"
        context: dict[str, Any] = {}
        inject_search_assets(mock_sphinx_app, "index", "page.html", context, None)
        assert "TYPESENSE_CONFIG" in context["typesense_search_html"]
        assert "PAGEFIND_CONFIG" not in context["typesense_search_html"]

    def test_inject_search_assets_pagefind_backend(self, mock_sphinx_app: MagicMock) -> None:
        """Verify Pagefind backend produces PAGEFIND_CONFIG."""
        mock_sphinx_app.config.typesense_backend = "pagefind"
        mock_sphinx_app.config.typesense_api_key = ""  # No API key triggers pagefind for auto
        context: dict[str, Any] = {}
        inject_search_assets(mock_sphinx_app, "index", "page.html", context, None)
        assert "PAGEFIND_CONFIG" in context["typesense_search_html"]
        assert "TYPESENSE_CONFIG" not in context["typesense_search_html"]


class TestGetSearchContainerHtml:
    """Tests for the get_search_container_html function."""

    def test_returns_html_string(self, mock_sphinx_app: MagicMock) -> None:
        """Verify function returns an HTML string."""
        result = get_search_container_html(mock_sphinx_app)
        assert isinstance(result, str)

    def test_contains_div_element(self, mock_sphinx_app: MagicMock) -> None:
        """Verify HTML contains a div element."""
        result = get_search_container_html(mock_sphinx_app)
        assert "<div" in result
        assert "</div>" in result

    def test_contains_typesense_search_id(self, mock_sphinx_app: MagicMock) -> None:
        """Verify HTML contains the default search container ID."""
        result = get_search_container_html(mock_sphinx_app)
        assert 'id="typesense-search"' in result

    def test_custom_container_id(self, mock_sphinx_app: MagicMock) -> None:
        """Verify custom container ID is used."""
        mock_sphinx_app.config.typesense_container = "#custom-search"
        result = get_search_container_html(mock_sphinx_app)
        assert 'id="custom-search"' in result

    def test_strips_hash_from_container(self, mock_sphinx_app: MagicMock) -> None:
        """Verify leading hash is stripped from container selector."""
        mock_sphinx_app.config.typesense_container = "#my-search"
        result = get_search_container_html(mock_sphinx_app)
        assert 'id="my-search"' in result
        assert 'id="#my-search"' not in result


class TestGetConfigScript:
    """Tests for the get_config_script function (deprecated)."""

    def test_returns_string(self, mock_sphinx_app: MagicMock) -> None:
        """Verify function returns a string."""
        result = get_config_script(mock_sphinx_app)
        assert isinstance(result, str)

    def test_delegates_to_typesense_config(self, mock_sphinx_app: MagicMock) -> None:
        """Verify get_config_script delegates to get_typesense_config_script."""
        result = get_config_script(mock_sphinx_app)
        expected = get_typesense_config_script(mock_sphinx_app)
        assert result == expected


class TestGetTypesenseConfigScript:
    """Tests for the get_typesense_config_script function."""

    def test_returns_string(self, mock_sphinx_app: MagicMock) -> None:
        """Verify function returns a string."""
        result = get_typesense_config_script(mock_sphinx_app)
        assert isinstance(result, str)

    def test_contains_script_tags(self, mock_sphinx_app: MagicMock) -> None:
        """Verify HTML contains script tags."""
        result = get_typesense_config_script(mock_sphinx_app)
        assert "<script>" in result
        assert "</script>" in result

    def test_contains_typesense_config(self, mock_sphinx_app: MagicMock) -> None:
        """Verify script contains TYPESENSE_CONFIG."""
        result = get_typesense_config_script(mock_sphinx_app)
        assert "TYPESENSE_CONFIG" in result

    def test_contains_collection_name(self, mock_sphinx_app: MagicMock) -> None:
        """Verify config includes collection name."""
        mock_sphinx_app.config.typesense_collection_name = "my_collection"
        result = get_typesense_config_script(mock_sphinx_app)
        assert "my_collection" in result

    def test_contains_host(self, mock_sphinx_app: MagicMock) -> None:
        """Verify config includes host."""
        result = get_typesense_config_script(mock_sphinx_app)
        assert "localhost" in result

    def test_contains_search_api_key_not_admin(self, mock_sphinx_app: MagicMock) -> None:
        """Verify search API key is used, not admin key."""
        mock_sphinx_app.config.typesense_api_key = "admin_secret_key"
        mock_sphinx_app.config.typesense_search_api_key = "search_public_key"
        result = get_typesense_config_script(mock_sphinx_app)
        assert "search_public_key" in result
        assert "admin_secret_key" not in result


class TestGetPagefindConfigScript:
    """Tests for the get_pagefind_config_script function."""

    def test_returns_string(self, mock_sphinx_app: MagicMock) -> None:
        """Verify function returns a string."""
        result = get_pagefind_config_script(mock_sphinx_app)
        assert isinstance(result, str)

    def test_contains_script_tags(self, mock_sphinx_app: MagicMock) -> None:
        """Verify HTML contains script tags."""
        result = get_pagefind_config_script(mock_sphinx_app)
        assert "<script>" in result
        assert "</script>" in result

    def test_contains_pagefind_config(self, mock_sphinx_app: MagicMock) -> None:
        """Verify script contains PAGEFIND_CONFIG."""
        result = get_pagefind_config_script(mock_sphinx_app)
        assert "PAGEFIND_CONFIG" in result

    def test_contains_container(self, mock_sphinx_app: MagicMock) -> None:
        """Verify config includes container."""
        result = get_pagefind_config_script(mock_sphinx_app)
        assert "typesense-search" in result

    def test_contains_placeholder(self, mock_sphinx_app: MagicMock) -> None:
        """Verify config includes placeholder."""
        result = get_pagefind_config_script(mock_sphinx_app)
        assert "Search documentation..." in result

    def test_contains_base_path(self, mock_sphinx_app: MagicMock) -> None:
        """Verify config includes basePath."""
        result = get_pagefind_config_script(mock_sphinx_app)
        assert "/_pagefind/" in result


class TestAddSearchMetaTags:
    """Tests for the add_search_meta_tags function."""

    def test_accepts_app_and_context(self, mock_sphinx_app: MagicMock) -> None:
        """Verify function accepts app and context parameters."""
        context: dict[str, Any] = {}
        # Should not raise
        add_search_meta_tags(mock_sphinx_app, context)

    def test_initializes_metatags_list(self, mock_sphinx_app: MagicMock) -> None:
        """Verify metatags list is initialized if not present."""
        context: dict[str, Any] = {}
        add_search_meta_tags(mock_sphinx_app, context)
        assert "metatags" in context
        assert isinstance(context["metatags"], list)

    def test_adds_backend_meta_tag_typesense(self, mock_sphinx_app: MagicMock) -> None:
        """Verify typesense backend meta tag is added."""
        mock_sphinx_app.config.typesense_backend = "typesense"
        context: dict[str, Any] = {}
        add_search_meta_tags(mock_sphinx_app, context, "typesense")

        backend_tag = next(
            (tag for tag in context["metatags"] if tag["name"] == "typesense-backend"),
            None,
        )
        assert backend_tag is not None
        assert backend_tag["content"] == "typesense"

    def test_adds_backend_meta_tag_pagefind(self, mock_sphinx_app: MagicMock) -> None:
        """Verify pagefind backend meta tag is added."""
        context: dict[str, Any] = {}
        add_search_meta_tags(mock_sphinx_app, context, "pagefind")

        backend_tag = next(
            (tag for tag in context["metatags"] if tag["name"] == "typesense-backend"),
            None,
        )
        assert backend_tag is not None
        assert backend_tag["content"] == "pagefind"

    def test_typesense_specific_meta_tags(self, mock_sphinx_app: MagicMock) -> None:
        """Verify Typesense-specific meta tags are added."""
        mock_sphinx_app.config.typesense_backend = "typesense"
        context: dict[str, Any] = {}
        add_search_meta_tags(mock_sphinx_app, context, "typesense")

        tag_names = [tag["name"] for tag in context["metatags"]]
        assert "typesense-collection" in tag_names
        assert "typesense-host" in tag_names
        assert "typesense-port" in tag_names
        assert "typesense-protocol" in tag_names
        assert "typesense-api-key" in tag_names

    def test_pagefind_specific_meta_tags(self, mock_sphinx_app: MagicMock) -> None:
        """Verify Pagefind-specific meta tags are added."""
        context: dict[str, Any] = {}
        add_search_meta_tags(mock_sphinx_app, context, "pagefind")

        tag_names = [tag["name"] for tag in context["metatags"]]
        assert "pagefind-base-path" in tag_names
        # Should not have Typesense-specific tags
        assert "typesense-host" not in tag_names
        assert "typesense-collection" not in tag_names

    def test_common_meta_tags_both_backends(self, mock_sphinx_app: MagicMock) -> None:
        """Verify common meta tags are present for both backends."""
        for backend in ["typesense", "pagefind"]:
            context: dict[str, Any] = {}
            add_search_meta_tags(mock_sphinx_app, context, backend)

            tag_names = [tag["name"] for tag in context["metatags"]]
            assert "typesense-backend" in tag_names
            assert "typesense-container" in tag_names
            assert "typesense-placeholder" in tag_names

    def test_preserves_existing_metatags(self, mock_sphinx_app: MagicMock) -> None:
        """Verify existing metatags are preserved."""
        existing_tag = {"name": "existing", "content": "value"}
        context: dict[str, Any] = {"metatags": [existing_tag]}
        add_search_meta_tags(mock_sphinx_app, context, "typesense")

        assert existing_tag in context["metatags"]
        assert len(context["metatags"]) > 1


class TestBackendConfigScriptSelection:
    """Tests for correct config script selection based on backend."""

    @pytest.fixture
    def typesense_app(self, mock_sphinx_app: MagicMock) -> MagicMock:
        """Create app configured for Typesense backend."""
        mock_sphinx_app.config.typesense_backend = "typesense"
        mock_sphinx_app.config.typesense_api_key = "admin_key"
        return mock_sphinx_app

    @pytest.fixture
    def pagefind_app(self, mock_sphinx_app: MagicMock) -> MagicMock:
        """Create app configured for Pagefind backend."""
        mock_sphinx_app.config.typesense_backend = "pagefind"
        mock_sphinx_app.config.typesense_api_key = ""
        return mock_sphinx_app

    def test_typesense_backend_config_script(self, typesense_app: MagicMock) -> None:
        """Verify Typesense config script is generated for Typesense backend."""
        context: dict[str, Any] = {}
        inject_search_assets(typesense_app, "index", "page.html", context, None)

        search_html = context["typesense_search_html"]
        assert "TYPESENSE_CONFIG" in search_html
        assert "collectionName" in search_html
        assert "host" in search_html

    def test_pagefind_backend_config_script(self, pagefind_app: MagicMock) -> None:
        """Verify Pagefind config script is generated for Pagefind backend."""
        context: dict[str, Any] = {}
        inject_search_assets(pagefind_app, "index", "page.html", context, None)

        search_html = context["typesense_search_html"]
        assert "PAGEFIND_CONFIG" in search_html
        assert "basePath" in search_html
