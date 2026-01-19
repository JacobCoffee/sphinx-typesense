# sphinx-typesense

A Sphinx extension for integrating Typesense search into documentation sites.

[![PyPI version](https://img.shields.io/pypi/v/sphinx-typesense.svg)](https://pypi.org/project/sphinx-typesense/)
[![Python versions](https://img.shields.io/pypi/pyversions/sphinx-typesense.svg)](https://pypi.org/project/sphinx-typesense/)
[![License](https://img.shields.io/pypi/l/sphinx-typesense.svg)](https://github.com/JacobCoffee/sphinx-typesense/blob/main/LICENSE)
[![CI](https://github.com/JacobCoffee/sphinx-typesense/actions/workflows/ci.yml/badge.svg)](https://github.com/JacobCoffee/sphinx-typesense/actions/workflows/ci.yml)
[![Documentation Status](https://readthedocs.org/projects/sphinx-typesense/badge/?version=latest)](https://sphinx-typesense.readthedocs.io/en/latest/?badge=latest)

Replace Sphinx's built-in search with Typesense for fast, typo-tolerant search that scales from small projects to large documentation portals.

![sphinx-typesense search example](docs/_static/images/search-example.png)

## Features

- **Fast Search** - Typesense provides sub-50ms search responses
- **Typo Tolerance** - Built-in typo correction (configurable 0-2 typos)
- **Build-time Indexing** - Automatic content extraction during Sphinx builds
- **DocSearch Compatible** - Uses the DocSearch hierarchical schema for familiar UX
- **Multiple Theme Support** - Works with RTD, Furo, Alabaster, PyData, and Book themes
- **Self-hosted or Cloud** - Supports both Typesense Server and Typesense Cloud

## Installation

```bash
pip install sphinx-typesense
```

Or with uv:

```bash
uv add sphinx-typesense
```

## Quick Start

Add to your Sphinx `conf.py`:

```python
extensions = ["sphinx_typesense"]

# Typesense server connection
typesense_host = "localhost"
typesense_port = "8108"
typesense_protocol = "http"

# API keys (use environment variables in production)
import os
typesense_api_key = os.environ.get("TYPESENSE_API_KEY", "")
typesense_search_api_key = os.environ.get("TYPESENSE_SEARCH_API_KEY", "")
```

Build your documentation and the search index will be automatically created:

```bash
sphinx-build -b html docs docs/_build/html
```

## Documentation

Full documentation is available at [sphinx-typesense.readthedocs.io](https://sphinx-typesense.readthedocs.io).

- [Installation Guide](https://sphinx-typesense.readthedocs.io/en/latest/getting-started/installation.html)
- [Configuration Reference](https://sphinx-typesense.readthedocs.io/en/latest/configuration.html)
- [Theme Support](https://sphinx-typesense.readthedocs.io/en/latest/themes.html)
- [API Reference](https://sphinx-typesense.readthedocs.io/en/latest/api/index.html)

## License

MIT License - see [LICENSE](LICENSE) for details.
