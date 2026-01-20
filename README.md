# sphinx-typesense

A Sphinx extension for integrating powerful search into documentation sites with support for both Typesense and Pagefind backends.

[![PyPI version](https://img.shields.io/pypi/v/sphinx-typesense.svg)](https://pypi.org/project/sphinx-typesense/)
[![Python versions](https://img.shields.io/pypi/pyversions/sphinx-typesense.svg)](https://pypi.org/project/sphinx-typesense/)
[![License](https://img.shields.io/pypi/l/sphinx-typesense.svg)](https://github.com/JacobCoffee/sphinx-typesense/blob/main/LICENSE)
[![CI](https://github.com/JacobCoffee/sphinx-typesense/actions/workflows/ci.yml/badge.svg)](https://github.com/JacobCoffee/sphinx-typesense/actions/workflows/ci.yml)
[![Docs](https://img.shields.io/badge/docs-typesense.scriptr.dev-blue)](https://typesense.scriptr.dev/)

Replace Sphinx's built-in search with fast, typo-tolerant search that scales from small projects to large documentation portals.

![sphinx-typesense search example](docs/_static/images/search-example.png)

## Features

- **Dual Backend Support** - Choose between Typesense (server-based) or Pagefind (static, no server required)
- **Fast Search** - Sub-50ms search responses with either backend
- **Typo Tolerance** - Built-in typo correction (configurable 0-2 typos)
- **Build-time Indexing** - Automatic content extraction during Sphinx builds
- **DocSearch Compatible** - Uses the DocSearch hierarchical schema for familiar UX
- **Multiple Theme Support** - Works with RTD, Furo, Alabaster, PyData, Book, and Shibuya themes
- **Self-hosted or Cloud** - Typesense supports both Server and Cloud deployments

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

# Backend selection: "auto", "typesense", or "pagefind"
typesense_backend = "auto"  # Uses Typesense if configured, falls back to Pagefind
```

### Pagefind (Static, No Server)

For static sites without a server, Pagefind works out of the box:

```python
typesense_backend = "pagefind"
```

### Typesense (Server-based)

For server-based search with advanced features:

```python
import os

typesense_backend = "typesense"
typesense_host = "localhost"
typesense_port = "8108"
typesense_protocol = "http"
typesense_api_key = os.environ.get("TYPESENSE_API_KEY", "")
typesense_search_api_key = os.environ.get("TYPESENSE_SEARCH_API_KEY", "")
```

Build your documentation and the search index will be automatically created:

```bash
sphinx-build -b html docs docs/_build/html
```

## Documentation

Full documentation is available at [typesense.scriptr.dev](https://typesense.scriptr.dev/).

- [Installation Guide](https://typesense.scriptr.dev/getting-started/installation.html)
- [Configuration Reference](https://typesense.scriptr.dev/configuration.html)
- [Theme Support](https://typesense.scriptr.dev/themes.html)
- [API Reference](https://typesense.scriptr.dev/api/index.html)

## License

MIT License - see [LICENSE](LICENSE) for details.
