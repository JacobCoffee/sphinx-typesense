"""Pagefind static search backend implementation.

This module provides the PagefindBackend class for client-side static
search using Pagefind. No server is required - the search index is
generated at build time and served as static files.

Pagefind Documentation: https://pagefind.app/

Installation:
    The recommended way to install Pagefind is via the Python package::

        pip install sphinx-typesense[pagefind]

    This bundles the Pagefind binary and requires no Node.js installation.
    Alternatively, pagefind can be installed via npm or run via npx.
"""

from __future__ import annotations

import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from sphinx.util import logging

from sphinx_typesense.backends.base import SearchBackend

if TYPE_CHECKING:
    from sphinx.application import Sphinx

logger = logging.getLogger(__name__)

# Pagefind CLI command name
PAGEFIND_CLI = "pagefind"

# Default output directory name (relative to build output)
DEFAULT_OUTPUT_DIR = "_pagefind"


class PagefindBackend(SearchBackend):
    """Pagefind static search backend implementation.

    Provides client-side search using Pagefind. The search index is
    generated at build time by running the pagefind CLI, requiring
    no server infrastructure.

    Attributes:
        name: Backend identifier ("pagefind").
        output_dir: Directory where Pagefind outputs its index.

    Configuration:
        The following conf.py options affect Pagefind behavior:
        - typesense_container: CSS selector for search container
        - typesense_placeholder: Search input placeholder text

    Requirements (any ONE of):
        - pip install sphinx-typesense[pagefind] (recommended, bundles binary)
        - pagefind CLI installed via npm (npm install -g pagefind)
        - npx available (auto-downloads pagefind on first run)

    """

    name = "pagefind"

    def __init__(self, app: Sphinx) -> None:
        """Initialize the Pagefind backend.

        Args:
            app: The Sphinx application instance.

        """
        super().__init__(app)
        self.output_dir = DEFAULT_OUTPUT_DIR
        logger.debug("sphinx-typesense: PagefindBackend initialized")

    def index_all(self) -> int:
        """Run Pagefind CLI to index the HTML output.

        Returns:
            Number of pages indexed, or 0 if indexing failed/skipped.

        """
        logger.info("sphinx-typesense: Running Pagefind indexer")

        build_dir = Path(self.app.outdir)
        if not build_dir.exists():
            logger.warning("sphinx-typesense: Build directory does not exist: %s", build_dir)
            return 0

        # Try to find pagefind CLI
        pagefind_cmd = self._find_pagefind_command()
        if not pagefind_cmd:
            logger.warning(
                "sphinx-typesense: Pagefind not found. Install with 'pip install sphinx-typesense[pagefind]' "
                "(recommended) or 'npm install -g pagefind'."
            )
            return 0

        return self._run_pagefind(pagefind_cmd, build_dir)

    def _run_pagefind(self, pagefind_cmd: list[str], build_dir: Path) -> int:
        """Execute the pagefind CLI command.

        Args:
            pagefind_cmd: Command to run pagefind (e.g., ['pagefind'] or ['npx', 'pagefind']).
            build_dir: Directory containing the built HTML.

        Returns:
            Number of pages indexed, or 0 if indexing failed.

        """
        # Build the command
        cmd = [
            *pagefind_cmd,
            "--site",
            str(build_dir),
            "--output-path",
            str(build_dir / self.output_dir),
        ]

        logger.debug("sphinx-typesense: Running command: %s", " ".join(cmd))

        try:
            result = subprocess.run(  # noqa: S603
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                check=False,
            )
        except subprocess.TimeoutExpired:
            logger.warning("sphinx-typesense: Pagefind indexing timed out after 5 minutes")
            return 0
        except FileNotFoundError:
            logger.warning("sphinx-typesense: Pagefind CLI not found at: %s", pagefind_cmd)
            return 0
        except OSError as e:
            logger.warning("sphinx-typesense: Error running Pagefind: %s", e)
            return 0

        if result.returncode != 0:
            logger.warning(
                "sphinx-typesense: Pagefind indexing failed (exit code %d): %s",
                result.returncode,
                result.stderr or result.stdout,
            )
            return 0

        # Parse page count from output
        # Pagefind outputs something like "Indexed 123 pages"
        page_count = self._parse_page_count(result.stdout)
        logger.info("sphinx-typesense: Pagefind indexed %d pages", page_count)
        return page_count

    def _find_pagefind_command(self) -> list[str] | None:
        """Find the pagefind CLI command.

        Tries to find pagefind in this order:
        1. Python pagefind package (pip install sphinx-typesense[pagefind])
        2. Direct 'pagefind' command (if installed via npm globally)
        3. 'npx pagefind' (downloads on demand, requires Node.js)

        Returns:
            Command as list of strings, or None if not found.

        """
        # Try Python pagefind package first (recommended)
        if self._check_python_pagefind():
            logger.debug("sphinx-typesense: Using Python pagefind package")
            return [sys.executable, "-m", "pagefind"]

        # Try direct pagefind command (npm global install)
        if shutil.which(PAGEFIND_CLI):
            logger.debug("sphinx-typesense: Found pagefind in PATH")
            return [PAGEFIND_CLI]

        # Try npx (requires Node.js)
        npx = shutil.which("npx")
        if npx:
            logger.debug("sphinx-typesense: Using npx to run pagefind")
            return [npx, "pagefind"]

        return None

    def _check_python_pagefind(self) -> bool:
        """Check if the Python pagefind package is installed.

        Returns:
            True if pagefind Python package is available.

        """
        return importlib.util.find_spec("pagefind") is not None

    def _parse_page_count(self, output: str) -> int:
        """Parse the number of indexed pages from Pagefind output.

        Args:
            output: Pagefind CLI stdout.

        Returns:
            Number of pages indexed, or 0 if not parseable.

        """
        # Look for patterns like:
        # "Indexed 123 pages"
        # "Running Pagefind v1.x on 123 pages"

        # Try "Indexed N pages" pattern
        match = re.search(r"Indexed\s+(\d+)\s+page", output, re.IGNORECASE)
        if match:
            return int(match.group(1))

        # Try "on N pages" pattern
        match = re.search(r"on\s+(\d+)\s+page", output, re.IGNORECASE)
        if match:
            return int(match.group(1))

        # Try any number followed by "pages"
        match = re.search(r"(\d+)\s+pages?", output, re.IGNORECASE)
        if match:
            return int(match.group(1))

        logger.debug("sphinx-typesense: Could not parse page count from: %s", output[:200])
        return 0

    def get_js_files(self) -> list[tuple[str, dict[str, str | int]]]:
        """Return Pagefind JavaScript files.

        Note: Pagefind JS is loaded from the generated _pagefind/ directory,
        not from Sphinx static files. The init script handles loading.

        """
        return [
            ("pagefind-init.js", {"priority": 500, "defer": "defer"}),
        ]

    def get_css_files(self) -> list[str]:
        """Return Pagefind CSS files.

        Note: Pagefind CSS is loaded dynamically by the init script
        from the _pagefind/ directory.

        """
        return ["pagefind-ui.css"]

    def get_config_script(self) -> str:
        """Return inline JavaScript configuration for Pagefind UI."""
        config = {
            "container": self.app.config.typesense_container,
            "placeholder": self.app.config.typesense_placeholder,
            "basePath": f"/{self.output_dir}/",
        }
        config_json = json.dumps(config, indent=2)
        return f"window.PAGEFIND_CONFIG = {config_json};"

    def is_available(self) -> bool:
        """Check if Pagefind CLI is available.

        Returns:
            True if pagefind or npx is available.

        """
        return self._find_pagefind_command() is not None
