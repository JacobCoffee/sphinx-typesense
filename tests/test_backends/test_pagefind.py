"""Tests for PagefindBackend."""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

from sphinx_typesense.backends.pagefind import PagefindBackend

if TYPE_CHECKING:
    from pathlib import Path


class TestPagefindBackend:
    """Tests for PagefindBackend class."""

    def test_name(self, mock_sphinx_app: MagicMock) -> None:
        """Backend name is 'pagefind'."""
        backend = PagefindBackend(mock_sphinx_app)
        assert backend.name == "pagefind"

    def test_output_dir_default(self, mock_sphinx_app: MagicMock) -> None:
        """Output directory defaults to '_pagefind'."""
        backend = PagefindBackend(mock_sphinx_app)
        assert backend.output_dir == "_pagefind"

    def test_get_js_files(self, mock_sphinx_app: MagicMock) -> None:
        """get_js_files returns pagefind init script."""
        backend = PagefindBackend(mock_sphinx_app)
        js_files = backend.get_js_files()
        assert len(js_files) == 1
        assert js_files[0][0] == "pagefind-init.js"
        assert js_files[0][1]["priority"] == 500
        assert js_files[0][1]["defer"] == "defer"

    def test_get_css_files(self, mock_sphinx_app: MagicMock) -> None:
        """get_css_files returns pagefind UI CSS."""
        backend = PagefindBackend(mock_sphinx_app)
        css_files = backend.get_css_files()
        assert css_files == ["pagefind-ui.css"]

    def test_get_config_script(self, mock_sphinx_app: MagicMock) -> None:
        """get_config_script returns valid JS config."""
        mock_sphinx_app.config.typesense_container = "#search"
        mock_sphinx_app.config.typesense_placeholder = "Search..."

        backend = PagefindBackend(mock_sphinx_app)
        script = backend.get_config_script()

        assert "PAGEFIND_CONFIG" in script
        assert '"container": "#search"' in script
        assert '"placeholder": "Search..."' in script
        assert '"basePath": "/_pagefind/"' in script

    def test_get_config_script_default_container(self, mock_sphinx_app: MagicMock) -> None:
        """get_config_script uses default container from config."""
        # Uses default from mock_sphinx_app fixture
        backend = PagefindBackend(mock_sphinx_app)
        script = backend.get_config_script()

        assert "PAGEFIND_CONFIG" in script
        assert "#typesense-search" in script

    def test_is_available_with_python_package(self, mock_sphinx_app: MagicMock) -> None:
        """is_available returns True when Python pagefind package is installed."""
        backend = PagefindBackend(mock_sphinx_app)
        with patch.object(backend, "_check_python_pagefind", return_value=True):
            assert backend.is_available() is True

    def test_is_available_with_pagefind(self, mock_sphinx_app: MagicMock) -> None:
        """is_available returns True when pagefind is in PATH."""
        backend = PagefindBackend(mock_sphinx_app)
        with (
            patch.object(backend, "_check_python_pagefind", return_value=False),
            patch("shutil.which", return_value="/usr/bin/pagefind"),
        ):
            assert backend.is_available() is True

    def test_is_available_with_npx(self, mock_sphinx_app: MagicMock) -> None:
        """is_available returns True when npx is available."""
        backend = PagefindBackend(mock_sphinx_app)

        def mock_which(cmd: str) -> str | None:
            return "/usr/bin/npx" if cmd == "npx" else None

        with (
            patch.object(backend, "_check_python_pagefind", return_value=False),
            patch("shutil.which", side_effect=mock_which),
        ):
            assert backend.is_available() is True

    def test_is_available_without_cli(self, mock_sphinx_app: MagicMock) -> None:
        """is_available returns False when nothing found."""
        backend = PagefindBackend(mock_sphinx_app)
        with (
            patch.object(backend, "_check_python_pagefind", return_value=False),
            patch("shutil.which", return_value=None),
        ):
            assert backend.is_available() is False


class TestPagefindBackendPrivateMethods:
    """Tests for private methods of PagefindBackend.

    Note: These tests access private methods (_find_pagefind_command, _parse_page_count,
    _check_python_pagefind) for thorough unit testing coverage. In production code,
    only public methods should be used.
    """

    def test_find_pagefind_command_python_package(self, mock_sphinx_app: MagicMock) -> None:
        """_find_pagefind_command prefers Python pagefind package."""
        backend = PagefindBackend(mock_sphinx_app)
        with (
            patch.object(backend, "_check_python_pagefind", return_value=True),
            patch("shutil.which", return_value="/usr/bin/pagefind"),  # Also available
        ):
            cmd = backend._find_pagefind_command()  # noqa: SLF001
            # Should use Python package even if CLI is available
            assert cmd is not None
            assert "-m" in cmd
            assert "pagefind" in cmd

    def test_find_pagefind_command_direct(self, mock_sphinx_app: MagicMock) -> None:
        """_find_pagefind_command falls back to CLI when no Python package."""
        backend = PagefindBackend(mock_sphinx_app)
        with (
            patch.object(backend, "_check_python_pagefind", return_value=False),
            patch("shutil.which", return_value="/usr/bin/pagefind"),
        ):
            cmd = backend._find_pagefind_command()  # noqa: SLF001
            assert cmd == ["pagefind"]

    def test_find_pagefind_command_npx(self, mock_sphinx_app: MagicMock) -> None:
        """_find_pagefind_command returns npx pagefind when no Python package or CLI."""
        backend = PagefindBackend(mock_sphinx_app)

        def mock_which(cmd: str) -> str | None:
            return "/usr/bin/npx" if cmd == "npx" else None

        with (
            patch.object(backend, "_check_python_pagefind", return_value=False),
            patch("shutil.which", side_effect=mock_which),
        ):
            cmd = backend._find_pagefind_command()  # noqa: SLF001
            assert cmd == ["/usr/bin/npx", "pagefind"]

    def test_find_pagefind_command_none(self, mock_sphinx_app: MagicMock) -> None:
        """_find_pagefind_command returns None when nothing found."""
        backend = PagefindBackend(mock_sphinx_app)
        with (
            patch.object(backend, "_check_python_pagefind", return_value=False),
            patch("shutil.which", return_value=None),
        ):
            cmd = backend._find_pagefind_command()  # noqa: SLF001
            assert cmd is None

    def test_check_python_pagefind_installed(self, mock_sphinx_app: MagicMock) -> None:
        """_check_python_pagefind returns True when package is installed."""
        backend = PagefindBackend(mock_sphinx_app)
        mock_spec = MagicMock()
        with patch("importlib.util.find_spec", return_value=mock_spec):
            assert backend._check_python_pagefind() is True  # noqa: SLF001

    def test_check_python_pagefind_not_installed(self, mock_sphinx_app: MagicMock) -> None:
        """_check_python_pagefind returns False when package is not installed."""
        backend = PagefindBackend(mock_sphinx_app)
        with patch("importlib.util.find_spec", return_value=None):
            assert backend._check_python_pagefind() is False  # noqa: SLF001


class TestPagefindBackendParsePageCount:
    """Tests for _parse_page_count method."""

    def test_parse_indexed_pages(self, mock_sphinx_app: MagicMock) -> None:
        """Parse 'Indexed N pages' pattern."""
        backend = PagefindBackend(mock_sphinx_app)
        assert backend._parse_page_count("Indexed 42 pages") == 42  # noqa: SLF001
        assert backend._parse_page_count("Indexed 1 page") == 1  # noqa: SLF001
        assert backend._parse_page_count("Successfully Indexed 100 pages in 2s") == 100  # noqa: SLF001

    def test_parse_on_pages(self, mock_sphinx_app: MagicMock) -> None:
        """Parse 'on N pages' pattern."""
        backend = PagefindBackend(mock_sphinx_app)
        assert backend._parse_page_count("Running Pagefind on 100 pages") == 100  # noqa: SLF001
        assert backend._parse_page_count("Working on 50 pages...") == 50  # noqa: SLF001

    def test_parse_generic_pages(self, mock_sphinx_app: MagicMock) -> None:
        """Parse generic 'N pages' pattern."""
        backend = PagefindBackend(mock_sphinx_app)
        assert backend._parse_page_count("Found 5 pages to index") == 5  # noqa: SLF001
        assert backend._parse_page_count("Processing 25 pages") == 25  # noqa: SLF001

    def test_parse_no_match(self, mock_sphinx_app: MagicMock) -> None:
        """Return 0 when no pattern matches."""
        backend = PagefindBackend(mock_sphinx_app)
        assert backend._parse_page_count("No match here") == 0  # noqa: SLF001
        assert backend._parse_page_count("") == 0  # noqa: SLF001
        assert backend._parse_page_count("Some random output") == 0  # noqa: SLF001

    def test_parse_case_insensitive(self, mock_sphinx_app: MagicMock) -> None:
        """Parsing is case insensitive."""
        backend = PagefindBackend(mock_sphinx_app)
        assert backend._parse_page_count("INDEXED 10 PAGES") == 10  # noqa: SLF001
        assert backend._parse_page_count("indexed 20 Pages") == 20  # noqa: SLF001


class TestPagefindBackendIndexAll:
    """Tests for index_all method."""

    def test_index_all_success(self, mock_sphinx_app: MagicMock, tmp_path: Path) -> None:
        """index_all runs pagefind and returns page count."""
        mock_sphinx_app.outdir = str(tmp_path)

        backend = PagefindBackend(mock_sphinx_app)

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Indexed 25 pages successfully"
        mock_result.stderr = ""

        with (
            patch("shutil.which", return_value="/usr/bin/pagefind"),
            patch("subprocess.run", return_value=mock_result) as mock_run,
        ):
            count = backend.index_all()
            assert count == 25
            mock_run.assert_called_once()

            # Verify command arguments
            call_args = mock_run.call_args
            cmd = call_args[0][0]
            assert cmd[0] == "pagefind"
            assert "--site" in cmd
            assert "--output-path" in cmd

    def test_index_all_cli_not_found(self, mock_sphinx_app: MagicMock, tmp_path: Path) -> None:
        """index_all returns 0 when CLI not found."""
        mock_sphinx_app.outdir = str(tmp_path)

        backend = PagefindBackend(mock_sphinx_app)

        with patch("shutil.which", return_value=None):
            count = backend.index_all()
            assert count == 0

    def test_index_all_build_dir_missing(self, mock_sphinx_app: MagicMock, tmp_path: Path) -> None:
        """index_all returns 0 when build directory does not exist."""
        mock_sphinx_app.outdir = str(tmp_path / "nonexistent")

        backend = PagefindBackend(mock_sphinx_app)

        count = backend.index_all()
        assert count == 0

    def test_index_all_command_fails(self, mock_sphinx_app: MagicMock, tmp_path: Path) -> None:
        """index_all returns 0 when command fails."""
        mock_sphinx_app.outdir = str(tmp_path)

        backend = PagefindBackend(mock_sphinx_app)

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Error: something went wrong"

        with (
            patch("shutil.which", return_value="/usr/bin/pagefind"),
            patch("subprocess.run", return_value=mock_result),
        ):
            count = backend.index_all()
            assert count == 0

    def test_index_all_timeout(self, mock_sphinx_app: MagicMock, tmp_path: Path) -> None:
        """index_all returns 0 when command times out."""
        mock_sphinx_app.outdir = str(tmp_path)

        backend = PagefindBackend(mock_sphinx_app)

        with (
            patch("shutil.which", return_value="/usr/bin/pagefind"),
            patch("subprocess.run", side_effect=subprocess.TimeoutExpired("pagefind", 300)),
        ):
            count = backend.index_all()
            assert count == 0

    def test_index_all_file_not_found_error(self, mock_sphinx_app: MagicMock, tmp_path: Path) -> None:
        """index_all returns 0 when FileNotFoundError raised."""
        mock_sphinx_app.outdir = str(tmp_path)

        backend = PagefindBackend(mock_sphinx_app)

        with (
            patch("shutil.which", return_value="/usr/bin/pagefind"),
            patch("subprocess.run", side_effect=FileNotFoundError("pagefind not found")),
        ):
            count = backend.index_all()
            assert count == 0

    def test_index_all_os_error(self, mock_sphinx_app: MagicMock, tmp_path: Path) -> None:
        """index_all returns 0 when OSError raised."""
        mock_sphinx_app.outdir = str(tmp_path)

        backend = PagefindBackend(mock_sphinx_app)

        with (
            patch("shutil.which", return_value="/usr/bin/pagefind"),
            patch("subprocess.run", side_effect=OSError("Permission denied")),
        ):
            count = backend.index_all()
            assert count == 0

    def test_index_all_uses_npx_when_pagefind_not_found(self, mock_sphinx_app: MagicMock, tmp_path: Path) -> None:
        """index_all uses npx when direct pagefind not available."""
        mock_sphinx_app.outdir = str(tmp_path)

        backend = PagefindBackend(mock_sphinx_app)

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Indexed 10 pages"
        mock_result.stderr = ""

        def mock_which(cmd: str) -> str | None:
            return "/usr/bin/npx" if cmd == "npx" else None

        with (
            patch("shutil.which", side_effect=mock_which),
            patch("subprocess.run", return_value=mock_result) as mock_run,
        ):
            count = backend.index_all()
            assert count == 10

            # Verify npx was used
            call_args = mock_run.call_args
            cmd = call_args[0][0]
            assert cmd[0] == "/usr/bin/npx"
            assert cmd[1] == "pagefind"
