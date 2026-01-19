"""Tests for sphinx-typesense configuration handling.

This module tests:
    - Configuration registration with Sphinx
    - Default value handling
    - Configuration validation
    - Environment variable support
    - Backend selection and validation

TODO (Phase 2):
    - Add tests for setup_config() registering all config values
    - Add tests for validate_config() error handling
    - Add tests for environment variable fallbacks
    - Add tests for invalid configuration detection
    - Add tests for API key security warnings
"""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest
from sphinx.errors import ConfigError

from sphinx_typesense import config


class TestConfigModule:
    """Tests for the config module imports and structure."""

    def test_module_imports(self) -> None:
        """Verify the config module can be imported."""
        assert config is not None

    def test_default_constants_exist(self) -> None:
        """Verify default configuration constants are defined."""
        assert hasattr(config, "DEFAULT_HOST")
        assert hasattr(config, "DEFAULT_PORT")
        assert hasattr(config, "DEFAULT_PROTOCOL")
        assert hasattr(config, "DEFAULT_COLLECTION_NAME")
        assert hasattr(config, "DEFAULT_PLACEHOLDER")
        assert hasattr(config, "DEFAULT_NUM_TYPOS")
        assert hasattr(config, "DEFAULT_PER_PAGE")
        assert hasattr(config, "DEFAULT_CONTAINER")
        assert hasattr(config, "DEFAULT_CONTENT_SELECTORS")

    def test_default_host_value(self) -> None:
        """Verify default host is localhost."""
        assert config.DEFAULT_HOST == "localhost"

    def test_default_port_value(self) -> None:
        """Verify default port is 8108 (Typesense default)."""
        assert config.DEFAULT_PORT == "8108"

    def test_default_protocol_value(self) -> None:
        """Verify default protocol is http."""
        assert config.DEFAULT_PROTOCOL == "http"

    def test_default_collection_name(self) -> None:
        """Verify default collection name is sphinx_docs."""
        assert config.DEFAULT_COLLECTION_NAME == "sphinx_docs"

    def test_default_num_typos(self) -> None:
        """Verify default typo tolerance is 2."""
        assert config.DEFAULT_NUM_TYPOS == 2

    def test_default_content_selectors_is_list(self) -> None:
        """Verify default content selectors is a list."""
        assert isinstance(config.DEFAULT_CONTENT_SELECTORS, list)
        assert len(config.DEFAULT_CONTENT_SELECTORS) > 0

    def test_default_content_selectors_includes_rtd(self) -> None:
        """Verify RTD theme selector is included in defaults."""
        assert ".wy-nav-content-wrap" in config.DEFAULT_CONTENT_SELECTORS


class TestSetupConfig:
    """Tests for the setup_config function."""

    def test_setup_config_exists(self) -> None:
        """Verify setup_config function is defined."""
        assert callable(config.setup_config)

    def test_setup_config_accepts_app(self, mock_sphinx_app: MagicMock) -> None:
        """Verify setup_config accepts a Sphinx app without error."""
        # TODO (Phase 2): Test that config values are registered
        # Currently a no-op, should not raise
        config.setup_config(mock_sphinx_app)


class TestValidateConfig:
    """Tests for the validate_config function."""

    def test_validate_config_exists(self) -> None:
        """Verify validate_config function is defined."""
        assert callable(config.validate_config)

    def test_validate_config_accepts_app_and_config(
        self, mock_sphinx_app: MagicMock, mock_sphinx_config: MagicMock
    ) -> None:
        """Verify validate_config accepts app and config without error."""
        # TODO (Phase 2): Test validation logic
        # Currently a no-op, should not raise
        config.validate_config(mock_sphinx_app, mock_sphinx_config)


class TestValidBackends:
    """Tests for backend configuration validation."""

    def test_valid_backends_constant_exists(self) -> None:
        """Verify VALID_BACKENDS constant is defined."""
        assert hasattr(config, "VALID_BACKENDS")
        assert isinstance(config.VALID_BACKENDS, set)

    def test_auto_is_valid_backend(self) -> None:
        """Verify 'auto' is a valid backend option."""
        assert "auto" in config.VALID_BACKENDS

    def test_typesense_is_valid_backend(self) -> None:
        """Verify 'typesense' is a valid backend option."""
        assert "typesense" in config.VALID_BACKENDS

    def test_pagefind_is_valid_backend(self) -> None:
        """Verify 'pagefind' is a valid backend option."""
        assert "pagefind" in config.VALID_BACKENDS

    def test_invalid_backend_raises_error(self, mock_sphinx_app: MagicMock, mock_sphinx_config: MagicMock) -> None:
        """Verify invalid backend raises ConfigError."""
        mock_sphinx_config.typesense_backend = "invalid_backend"
        with pytest.raises(ConfigError) as exc_info:
            config.validate_config(mock_sphinx_app, mock_sphinx_config)
        assert "invalid_backend" in str(exc_info.value)
        assert "typesense_backend" in str(exc_info.value)


class TestGetEffectiveBackend:
    """Tests for the get_effective_backend function."""

    def test_function_exists(self) -> None:
        """Verify get_effective_backend function is defined."""
        assert callable(config.get_effective_backend)

    def test_auto_with_api_key_returns_typesense(self, mock_sphinx_config: MagicMock) -> None:
        """Verify 'auto' backend returns 'typesense' when API key is present."""
        mock_sphinx_config.typesense_backend = "auto"
        mock_sphinx_config.typesense_api_key = "test_key"
        result = config.get_effective_backend(mock_sphinx_config)
        assert result == "typesense"

    def test_auto_without_api_key_returns_pagefind(self, mock_sphinx_config: MagicMock) -> None:
        """Verify 'auto' backend returns 'pagefind' when no API key is present."""
        mock_sphinx_config.typesense_backend = "auto"
        mock_sphinx_config.typesense_api_key = ""
        # Also ensure environment variable is not set
        with patch.dict(os.environ, {}, clear=True):
            result = config.get_effective_backend(mock_sphinx_config)
        assert result == "pagefind"

    def test_auto_with_env_api_key_returns_typesense(self, mock_sphinx_config: MagicMock) -> None:
        """Verify 'auto' backend returns 'typesense' when API key is in environment."""
        mock_sphinx_config.typesense_backend = "auto"
        mock_sphinx_config.typesense_api_key = ""
        with patch.dict(os.environ, {"TYPESENSE_API_KEY": "env_key"}):
            result = config.get_effective_backend(mock_sphinx_config)
        assert result == "typesense"

    def test_explicit_typesense_returns_typesense(self, mock_sphinx_config: MagicMock) -> None:
        """Verify explicit 'typesense' backend returns 'typesense'."""
        mock_sphinx_config.typesense_backend = "typesense"
        mock_sphinx_config.typesense_api_key = ""
        result = config.get_effective_backend(mock_sphinx_config)
        assert result == "typesense"

    def test_explicit_pagefind_returns_pagefind(self, mock_sphinx_config: MagicMock) -> None:
        """Verify explicit 'pagefind' backend returns 'pagefind'."""
        mock_sphinx_config.typesense_backend = "pagefind"
        mock_sphinx_config.typesense_api_key = "test_key"  # Even with API key
        result = config.get_effective_backend(mock_sphinx_config)
        assert result == "pagefind"


class TestBackendValidation:
    """Tests for backend-specific validation behavior."""

    def test_pagefind_backend_skips_api_key_validation(
        self, mock_sphinx_app: MagicMock, mock_sphinx_config: MagicMock
    ) -> None:
        """Verify pagefind backend doesn't require Typesense API keys."""
        mock_sphinx_config.typesense_backend = "pagefind"
        mock_sphinx_config.typesense_api_key = ""
        mock_sphinx_config.typesense_search_api_key = ""
        mock_sphinx_config.typesense_enable_indexing = True

        # Clear environment variables
        with patch.dict(os.environ, {}, clear=True):
            # Should not raise ConfigError
            config.validate_config(mock_sphinx_app, mock_sphinx_config)

    def test_auto_without_api_key_skips_validation(
        self, mock_sphinx_app: MagicMock, mock_sphinx_config: MagicMock
    ) -> None:
        """Verify 'auto' backend without API key doesn't error (uses pagefind)."""
        mock_sphinx_config.typesense_backend = "auto"
        mock_sphinx_config.typesense_api_key = ""
        mock_sphinx_config.typesense_search_api_key = ""
        mock_sphinx_config.typesense_enable_indexing = True

        # Clear environment variables
        with patch.dict(os.environ, {}, clear=True):
            # Should not raise ConfigError
            config.validate_config(mock_sphinx_app, mock_sphinx_config)

    def test_typesense_backend_requires_api_keys(
        self, mock_sphinx_app: MagicMock, mock_sphinx_config: MagicMock
    ) -> None:
        """Verify explicit 'typesense' backend requires API keys."""
        mock_sphinx_config.typesense_backend = "typesense"
        mock_sphinx_config.typesense_api_key = ""
        mock_sphinx_config.typesense_search_api_key = ""
        mock_sphinx_config.typesense_enable_indexing = True

        # Clear environment variables
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ConfigError) as exc_info:
                config.validate_config(mock_sphinx_app, mock_sphinx_config)
            assert "typesense_api_key" in str(exc_info.value)

    def test_auto_with_api_key_requires_search_key(
        self, mock_sphinx_app: MagicMock, mock_sphinx_config: MagicMock
    ) -> None:
        """Verify 'auto' backend with API key requires search key too."""
        mock_sphinx_config.typesense_backend = "auto"
        mock_sphinx_config.typesense_api_key = "admin_key"
        mock_sphinx_config.typesense_search_api_key = ""
        mock_sphinx_config.typesense_enable_indexing = True

        # Clear environment variables
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ConfigError) as exc_info:
                config.validate_config(mock_sphinx_app, mock_sphinx_config)
            assert "typesense_search_api_key" in str(exc_info.value)


# =============================================================================
# TODO (Phase 2): Tests to implement
# =============================================================================
#
# class TestConfigRegistration:
#     """Tests for Sphinx config value registration."""
#
#     def test_registers_required_config_values(self):
#         """Verify all required config values are registered."""
#         pass
#
#     def test_registers_optional_config_values(self):
#         """Verify all optional config values are registered."""
#         pass
#
#
# class TestConfigValidation:
#     """Tests for configuration validation."""
#
#     def test_missing_api_key_raises_error(self):
#         """Verify missing API key raises ConfigError."""
#         pass
#
#     def test_missing_search_api_key_raises_error(self):
#         """Verify missing search API key raises ConfigError."""
#         pass
#
#     def test_invalid_protocol_raises_error(self):
#         """Verify invalid protocol raises ConfigError."""
#         pass
#
#     def test_same_admin_and_search_key_warns(self):
#         """Verify warning when admin and search keys are the same."""
#         pass
#
#
# class TestEnvironmentVariables:
#     """Tests for environment variable support."""
#
#     def test_api_key_from_environment(self):
#         """Verify API key can be loaded from environment."""
#         pass
#
#     def test_search_api_key_from_environment(self):
#         """Verify search API key can be loaded from environment."""
#         pass
