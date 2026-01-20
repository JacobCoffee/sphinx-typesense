"""Sphinx configuration for sphinx-typesense documentation."""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Add source directory to path for autodoc
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# -- Project information -----------------------------------------------------
project = "sphinx-typesense"
copyright = "2025, JacobCoffee"
author = "JacobCoffee"
release = "0.1.0"
version = "0.1.0"

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx_typesense",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Suppress duplicate object warnings from autosummary + manual docs
suppress_warnings = ["ref.python"]

# -- Options for HTML output -------------------------------------------------
html_theme = "shibuya"
html_static_path = ["_static"]
html_css_files = ["custom.css"]

html_theme_options = {
    "github_url": "https://github.com/JacobCoffee/sphinx-typesense",
    "nav_links": [
        {"title": "Getting Started", "url": "getting-started/index"},
        {"title": "Configuration", "url": "configuration"},
        {"title": "API Reference", "url": "api/index"},
    ],
}

html_context = {
    "source_type": "github",
    "source_user": "JacobCoffee",
    "source_repo": "sphinx-typesense",
}

# -- Extension configuration -------------------------------------------------

# Napoleon settings
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

# Autosummary settings
autosummary_generate = True

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
}

# -- sphinx-typesense configuration ------------------------------------------
# Use auto backend: Typesense in CI (if keys available), Pagefind locally

# Backend selection (auto = typesense if keys present, pagefind otherwise)
typesense_backend = "auto"

# Typesense settings (for CI/production when TYPESENSE_API_KEY is set)
typesense_host = os.environ.get("TYPESENSE_HOST", "localhost")
typesense_port = os.environ.get("TYPESENSE_PORT", "8108")
typesense_protocol = os.environ.get("TYPESENSE_PROTOCOL", "http")
typesense_api_key = os.environ.get("TYPESENSE_API_KEY", "")
typesense_search_api_key = os.environ.get("TYPESENSE_SEARCH_KEY", "")

# Collection and UI settings
typesense_collection_name = "sphinx-typesense-docs"
typesense_placeholder = "Search sphinx-typesense docs..."

# Enable indexing only if a backend is available
# (Typesense requires API key, Pagefind requires CLI)
typesense_enable_indexing = True
