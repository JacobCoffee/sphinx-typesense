"""Sphinx configuration for PyData theme example.

This configuration demonstrates sphinx-typesense integration with the
pydata_sphinx_theme, commonly used by scientific Python projects.

Build with:
    sphinx-build -b html -c docs-pydata source docs-pydata/_build/html
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# -- Path setup --------------------------------------------------------------
# Add the examples directory to the Python path for autodoc (contains litestar_app package)
_examples_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_examples_dir))

# Also add the sphinx-typesense source for the extension
_src_dir = Path(__file__).parent.parent.parent.parent / "src"
sys.path.insert(0, str(_src_dir))

# -- Project information -----------------------------------------------------
project = "Litestar Example API"
copyright = "2025, sphinx-typesense"
author = "sphinx-typesense"
release = "1.0.0"
version = "1.0.0"

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_typesense",
]

templates_path = []
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
html_theme = "pydata_sphinx_theme"
html_static_path = []

html_theme_options = {
    "show_nav_level": 2,
    "navigation_depth": 4,
    "show_toc_level": 2,
    "navbar_align": "left",
    "navbar_end": ["theme-switcher", "navbar-icon-links"],
    "secondary_sidebar_items": ["page-toc", "edit-this-page"],
    "footer_start": ["copyright"],
    "footer_end": ["theme-version"],
}

html_context = {
    "github_user": "JacobCoffee",
    "github_repo": "sphinx-typesense",
    "github_version": "main",
    "doc_path": "examples/docs/source",
}

# -- Extension configuration -------------------------------------------------

# Napoleon settings (Google-style docstrings)
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_use_param = True
napoleon_use_rtype = True

# Autodoc settings
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
}
autodoc_typehints = "description"
autodoc_typehints_description_target = "documented"
autodoc_class_signature = "separated"

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "litestar": ("https://docs.litestar.dev/latest/", None),
    "pydantic": ("https://docs.pydantic.dev/latest/", None),
}

# -- sphinx-typesense configuration ------------------------------------------
typesense_host = os.environ.get("TYPESENSE_HOST", "127.0.0.1")
typesense_port = os.environ.get("TYPESENSE_PORT", "8108")
typesense_protocol = "http"
typesense_api_key = os.environ.get("TYPESENSE_API_KEY", "local_dev_key")
typesense_search_api_key = os.environ.get("TYPESENSE_SEARCH_API_KEY", "local_dev_key")
typesense_collection_name = "example-docs-pydata"
typesense_enable_indexing = True
