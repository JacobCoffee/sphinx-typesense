# sphinx-typesense: Technical Specification

> A Sphinx extension for integrating Typesense search into documentation sites.

**Version**: 0.1.0 (Initial Specification)
**Status**: Draft
**Author**: JacobCoffee
**Date**: 2026-01-18

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Problem Statement](#problem-statement)
3. [Goals & Non-Goals](#goals--non-goals)
4. [Architecture Overview](#architecture-overview)
5. [Technical Design](#technical-design)
6. [Configuration Schema](#configuration-schema)
7. [Implementation Phases](#implementation-phases)
8. [API Reference](#api-reference)
9. [Theme Support](#theme-support)
10. [Security Considerations](#security-considerations)
11. [Testing Strategy](#testing-strategy)
12. [Dependencies](#dependencies)

---

## Executive Summary

`sphinx-typesense` is a Sphinx extension that replaces Sphinx's default search with Typesense, an open-source, typo-tolerant search engine. The extension provides:

- **Build-time indexing**: Automatically indexes documentation during `sphinx-build`
- **Frontend search UI**: Injects DocSearch-compatible modal search interface
- **Theme compatibility**: Works with RTD, Furo, Alabaster, and custom themes
- **Self-hosted & Cloud**: Supports both Typesense Server and Typesense Cloud

---

## Problem Statement

### Current State

Sphinx's built-in search is widely criticized:
- Static JavaScript-based search with poor relevance
- No typo tolerance
- Slow on large documentation sets
- Limited to exact matches

### Market Context

- **55+ million** documentation pages hosted on ReadTheDocs use Sphinx
- Algolia DocSearch is the primary alternative but is proprietary
- Typesense provides an open-source, self-hostable alternative
- [GitHub Issue #695](https://github.com/typesense/typesense/issues/695) shows community demand

### Solution

A native Sphinx extension that:
1. Indexes documentation at build time using Typesense Python client
2. Injects typesense-docsearch.js frontend for search UI
3. Requires minimal configuration in `conf.py`

---

## Goals & Non-Goals

### Goals

| Priority | Goal |
|----------|------|
| P0 | Replace Sphinx default search with Typesense search |
| P0 | Support Typesense Server (self-hosted) and Typesense Cloud |
| P0 | Work with sphinx_rtd_theme out of the box |
| P1 | Support Furo, Alabaster, and PyData themes |
| P1 | Index hierarchical content (h1 > h2 > h3 > text) |
| P1 | Provide search-only API key separation |
| P2 | Support multi-version documentation filtering |
| P2 | Enable semantic/vector search (optional) |

### Non-Goals

- Replacing the typesense-docsearch-scraper (we use Python-native indexing)
- Supporting non-HTML Sphinx builders
- Providing a hosted Typesense service
- Real-time index updates (batch at build time only)

---

## Architecture Overview

```
                    BUILD TIME                          RUNTIME
                    ==========                          =======

┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Sphinx Build   │───▶│ sphinx-typesense │───▶│ Typesense Server│
│  (sphinx-build) │    │    Extension     │    │   (API)         │
└─────────────────┘    └──────────────────┘    └─────────────────┘
        │                      │                        │
        │                      │                        │
        ▼                      ▼                        │
┌─────────────────┐    ┌──────────────────┐            │
│  HTML Output    │    │  Index Documents │            │
│  (_build/html)  │    │  via Python API  │            │
└─────────────────┘    └──────────────────┘            │
        │                                              │
        │              INJECTED ASSETS                 │
        ▼              ===============                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Browser (User)                           │
│  ┌─────────────────┐    ┌──────────────────────────────────┐   │
│  │ docsearch.js    │───▶│ Search Query → Typesense API     │   │
│  │ Modal UI        │◀───│ Results → Render in Modal        │   │
│  └─────────────────┘    └──────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| Indexer | Python + typesense-python | Extract content from Sphinx doctree, create Typesense documents |
| Template Injector | Jinja2 templates | Add search bar HTML and load JS/CSS assets |
| Frontend | typesense-docsearch.js v3 | Modal search UI with keyboard navigation |
| Configuration | Sphinx conf.py values | User-defined settings for Typesense connection |

---

## Technical Design

### 1. Sphinx Extension Entry Point

```python
# src/sphinx_typesense/__init__.py

from sphinx.application import Sphinx
from sphinx_typesense.indexer import TypesenseIndexer
from sphinx_typesense.config import setup_config
from sphinx_typesense.templates import inject_search_assets

__version__ = "0.1.0"

def setup(app: Sphinx) -> dict:
    """Sphinx extension entry point."""
    # Register configuration values
    setup_config(app)

    # Connect to Sphinx events
    app.connect("config-inited", validate_config)
    app.connect("build-finished", index_documents)
    app.connect("html-page-context", inject_search_assets)

    # Add static files
    app.add_css_file("typesense-docsearch.css")
    app.add_js_file("typesense-docsearch.js", priority=500)
    app.add_js_file("typesense-init.js", priority=501)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
```

### 2. Document Schema

The Typesense collection schema for documentation:

```python
DOCS_SCHEMA = {
    "name": "sphinx_docs",  # Configurable via typesense_collection_name
    "fields": [
        # Hierarchical levels (DocSearch compatible)
        {"name": "hierarchy.lvl0", "type": "string", "facet": True},
        {"name": "hierarchy.lvl1", "type": "string", "facet": True, "optional": True},
        {"name": "hierarchy.lvl2", "type": "string", "facet": True, "optional": True},
        {"name": "hierarchy.lvl3", "type": "string", "facet": True, "optional": True},

        # Content
        {"name": "content", "type": "string"},
        {"name": "url", "type": "string"},
        {"name": "url_without_anchor", "type": "string"},
        {"name": "anchor", "type": "string", "optional": True},

        # Metadata
        {"name": "type", "type": "string", "facet": True},  # "lvl0", "lvl1", "content"
        {"name": "version", "type": "string", "facet": True, "optional": True},
        {"name": "language", "type": "string", "facet": True, "optional": True},

        # Ranking
        {"name": "weight", "type": "int32"},
        {"name": "item_priority", "type": "int64"},
    ],
    "default_sorting_field": "item_priority",
    "token_separators": ["_", "-", "."],
}
```

### 3. Content Extraction

```python
# src/sphinx_typesense/indexer.py

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import TYPE_CHECKING, Iterator

from bs4 import BeautifulSoup
import typesense

if TYPE_CHECKING:
    from sphinx.application import Sphinx


class TypesenseIndexer:
    """Extract and index Sphinx documentation content."""

    def __init__(self, app: Sphinx) -> None:
        self.app = app
        self.client = self._create_client()
        self.collection_name = app.config.typesense_collection_name

    def _create_client(self) -> typesense.Client:
        """Initialize Typesense client from Sphinx config."""
        return typesense.Client({
            "nodes": [{
                "host": self.app.config.typesense_host,
                "port": self.app.config.typesense_port,
                "protocol": self.app.config.typesense_protocol,
            }],
            "api_key": self.app.config.typesense_api_key,
            "connection_timeout_seconds": 10,
        })

    def index_all(self) -> int:
        """Index all HTML files from build output."""
        self._ensure_collection()

        html_dir = Path(self.app.outdir)
        documents = []

        for html_file in html_dir.rglob("*.html"):
            documents.extend(self._extract_documents(html_file))

        # Bulk import
        if documents:
            self.client.collections[self.collection_name].documents.import_(
                documents, {"action": "upsert"}
            )

        return len(documents)

    def _extract_documents(self, html_file: Path) -> Iterator[dict]:
        """Extract searchable documents from an HTML file."""
        soup = BeautifulSoup(html_file.read_text(), "html.parser")

        # Get theme-specific content selector
        content = self._get_content_element(soup)
        if not content:
            return

        # Extract hierarchy
        url_base = self._get_relative_url(html_file)
        hierarchy = {"lvl0": "", "lvl1": "", "lvl2": "", "lvl3": ""}

        for element in content.find_all(["h1", "h2", "h3", "h4", "p", "li"]):
            tag = element.name
            text = element.get_text(strip=True)

            if not text:
                continue

            if tag == "h1":
                hierarchy["lvl0"] = text
                hierarchy["lvl1"] = ""
                hierarchy["lvl2"] = ""
                hierarchy["lvl3"] = ""
                yield self._create_document(hierarchy, "", url_base, element, "lvl0")

            elif tag == "h2":
                hierarchy["lvl1"] = text
                hierarchy["lvl2"] = ""
                hierarchy["lvl3"] = ""
                yield self._create_document(hierarchy, "", url_base, element, "lvl1")

            elif tag == "h3":
                hierarchy["lvl2"] = text
                hierarchy["lvl3"] = ""
                yield self._create_document(hierarchy, "", url_base, element, "lvl2")

            elif tag == "h4":
                hierarchy["lvl3"] = text
                yield self._create_document(hierarchy, "", url_base, element, "lvl3")

            elif tag in ("p", "li"):
                yield self._create_document(hierarchy, text, url_base, element, "content")

    def _create_document(
        self,
        hierarchy: dict,
        content: str,
        url_base: str,
        element,
        doc_type: str,
    ) -> dict:
        """Create a Typesense document."""
        anchor = element.get("id", "") or self._find_anchor(element)
        url = f"{url_base}#{anchor}" if anchor else url_base

        doc_id = hashlib.md5(f"{url}:{content[:100]}".encode()).hexdigest()

        return {
            "id": doc_id,
            "hierarchy.lvl0": hierarchy["lvl0"],
            "hierarchy.lvl1": hierarchy["lvl1"],
            "hierarchy.lvl2": hierarchy["lvl2"],
            "hierarchy.lvl3": hierarchy["lvl3"],
            "content": content,
            "url": url,
            "url_without_anchor": url_base,
            "anchor": anchor,
            "type": doc_type,
            "version": self.app.config.typesense_doc_version or "",
            "language": self.app.config.language or "en",
            "weight": self._get_weight(doc_type),
            "item_priority": self._get_priority(doc_type),
        }

    def _get_weight(self, doc_type: str) -> int:
        """Assign weight based on document type."""
        weights = {"lvl0": 100, "lvl1": 90, "lvl2": 80, "lvl3": 70, "content": 50}
        return weights.get(doc_type, 50)

    def _get_priority(self, doc_type: str) -> int:
        """Assign priority for default sorting."""
        priorities = {"lvl0": 100, "lvl1": 90, "lvl2": 80, "lvl3": 70, "content": 50}
        return priorities.get(doc_type, 50)

    def _get_content_element(self, soup: BeautifulSoup):
        """Get main content element based on theme."""
        selectors = self.app.config.typesense_content_selectors or [
            ".wy-nav-content-wrap",  # RTD theme
            "article.bd-article",     # PyData theme
            ".body",                  # Alabaster
            "article[role=main]",     # Furo
            "main",                   # Generic fallback
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element
        return None
```

### 4. Frontend Integration

```javascript
// static/typesense-init.js

document.addEventListener("DOMContentLoaded", function() {
  // Configuration injected by Sphinx template
  const config = window.TYPESENSE_CONFIG || {};

  if (!config.collectionName || !config.apiKey) {
    console.warn("sphinx-typesense: Missing configuration");
    return;
  }

  docsearch({
    container: config.container || "#typesense-search",
    typesenseCollectionName: config.collectionName,
    typesenseServerConfig: {
      nodes: [{
        host: config.host || "localhost",
        port: config.port || "8108",
        protocol: config.protocol || "http",
      }],
      apiKey: config.apiKey,
    },
    typesenseSearchParameters: {
      query_by: "hierarchy.lvl0,hierarchy.lvl1,hierarchy.lvl2,hierarchy.lvl3,content",
      num_typos: config.numTypos || 2,
      per_page: config.perPage || 10,
      filter_by: config.filterBy || "",
    },
    placeholder: config.placeholder || "Search documentation...",
    resultsFooterComponent: () => null,
  });
});
```

### 5. Template Injection

```python
# src/sphinx_typesense/templates.py

from sphinx.application import Sphinx


def inject_search_assets(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict,
    doctree,
) -> None:
    """Inject Typesense search configuration into page context."""

    # Add search container to page
    search_html = f'''
    <div id="typesense-search"></div>
    <script>
      window.TYPESENSE_CONFIG = {{
        collectionName: "{app.config.typesense_collection_name}",
        host: "{app.config.typesense_host}",
        port: "{app.config.typesense_port}",
        protocol: "{app.config.typesense_protocol}",
        apiKey: "{app.config.typesense_search_api_key}",
        placeholder: "{app.config.typesense_placeholder}",
        numTypos: {app.config.typesense_num_typos},
        perPage: {app.config.typesense_per_page},
        filterBy: "{app.config.typesense_filter_by}",
        container: "{app.config.typesense_container}",
      }};
    </script>
    '''

    context["typesense_search_html"] = search_html
```

---

## Configuration Schema

### Required Settings

```python
# conf.py

extensions = ["sphinx_typesense"]

# Typesense Server Connection (REQUIRED)
typesense_host = "localhost"              # Typesense server host
typesense_port = "8108"                   # Typesense server port
typesense_protocol = "http"               # "http" or "https"
typesense_api_key = "xyz"                 # Admin API key (for indexing)
typesense_search_api_key = "abc"          # Search-only API key (for frontend)
```

### Optional Settings

```python
# Collection settings
typesense_collection_name = "sphinx_docs"  # Collection name in Typesense
typesense_doc_version = ""                 # Version tag for filtering

# Search UI settings
typesense_placeholder = "Search documentation..."
typesense_num_typos = 2                    # Typo tolerance (0-2)
typesense_per_page = 10                    # Results per page
typesense_container = "#typesense-search"  # CSS selector for search container
typesense_filter_by = ""                   # Default filter (e.g., "version:=1.0")

# Theme-specific content selectors (auto-detected if not set)
typesense_content_selectors = [
    ".wy-nav-content-wrap",
    "article[role=main]",
    ".body",
    "main",
]

# Advanced
typesense_enable_indexing = True           # Set False to skip indexing
typesense_drop_existing = False            # Drop collection before reindex
```

### Environment Variables

For CI/CD pipelines, API keys can be set via environment variables:

```bash
export TYPESENSE_API_KEY="your_admin_key"
export TYPESENSE_SEARCH_API_KEY="your_search_key"
```

```python
# conf.py
import os
typesense_api_key = os.environ.get("TYPESENSE_API_KEY", "")
typesense_search_api_key = os.environ.get("TYPESENSE_SEARCH_API_KEY", "")
```

---

## Implementation Phases

### Phase 1: Core Extension (MVP)

| Task | Description | Priority |
|------|-------------|----------|
| Project scaffolding | pyproject.toml, src layout, CI setup | P0 |
| Basic indexer | Extract h1-h4 and paragraphs from HTML | P0 |
| Typesense client integration | Create collection, bulk index documents | P0 |
| Frontend injection | Add docsearch.js and init script | P0 |
| RTD theme support | Test and verify with sphinx_rtd_theme | P0 |
| Configuration validation | Verify required settings present | P0 |

### Phase 2: Theme & Polish

| Task | Description | Priority |
|------|-------------|----------|
| Furo theme support | Add selectors, test integration | P1 |
| Alabaster theme support | Add selectors, test integration | P1 |
| PyData theme support | Add selectors, test integration | P1 |
| Custom theme guide | Document how to add custom selectors | P1 |
| Error handling | Graceful degradation if Typesense unavailable | P1 |
| Logging | Add structured logging for debugging | P1 |

### Phase 3: Advanced Features

| Task | Description | Priority |
|------|-------------|----------|
| Multi-version support | Filter by version facet | P2 |
| Semantic search | Optional vector embeddings | P2 |
| Analytics integration | Track search queries | P2 |
| Incremental indexing | Only reindex changed files | P2 |
| Offline fallback | Graceful degradation without connectivity | P2 |

---

## API Reference

### Sphinx Events

| Event | Handler | Purpose |
|-------|---------|---------|
| `config-inited` | `validate_config()` | Validate required settings |
| `build-finished` | `index_documents()` | Index HTML after build completes |
| `html-page-context` | `inject_search_assets()` | Add search UI to each page |

### Python API

```python
from sphinx_typesense import TypesenseIndexer

# Manual indexing (for custom builds)
indexer = TypesenseIndexer(app)
count = indexer.index_all()
print(f"Indexed {count} documents")

# Check collection status
indexer.client.collections[collection_name].retrieve()
```

### JavaScript API

```javascript
// Access search instance
const searchInstance = window.typesenseDocsearch;

// Programmatic search
searchInstance.setQuery("installation");
searchInstance.open();
```

---

## Theme Support

### Supported Themes

| Theme | Content Selector | Status |
|-------|------------------|--------|
| sphinx_rtd_theme | `.wy-nav-content-wrap` | Primary |
| furo | `article[role=main]` | Supported |
| alabaster | `.body` | Supported |
| pydata_sphinx_theme | `article.bd-article` | Supported |
| sphinx_book_theme | `main#main-content` | Supported |

### Adding Custom Theme Support

```python
# conf.py

# Override auto-detection with custom selectors
typesense_content_selectors = [
    ".my-custom-content-wrapper",
    "article.main-content",
]
```

### Search Bar Placement

The extension looks for these elements to place the search bar:

1. `#typesense-search` (explicit container)
2. `.wy-side-nav-search` (RTD theme sidebar)
3. `nav.bd-search` (PyData theme)
4. `.sidebar-search-container` (Furo)
5. Falls back to prepending to `body`

---

## Security Considerations

### API Key Separation

**CRITICAL**: Use separate API keys for indexing and search.

```python
# conf.py

# Admin key - NEVER expose in frontend
# Only used during build for indexing
typesense_api_key = os.environ["TYPESENSE_ADMIN_KEY"]

# Search-only key - Safe for frontend
# Can only perform search operations
typesense_search_api_key = os.environ["TYPESENSE_SEARCH_KEY"]
```

### Creating a Search-Only Key

```bash
curl 'http://localhost:8108/keys' \
  -X POST \
  -H "X-TYPESENSE-API-KEY: ${ADMIN_KEY}" \
  -d '{
    "description": "Search-only key for docs",
    "actions": ["documents:search"],
    "collections": ["sphinx_docs"]
  }'
```

### CI/CD Best Practices

1. Store API keys as secrets (GitHub Secrets, GitLab CI Variables)
2. Never commit API keys to repository
3. Use environment variables in conf.py
4. Rotate search keys periodically

---

## Testing Strategy

### Unit Tests

```python
# tests/test_indexer.py

def test_extract_hierarchy():
    """Test hierarchical content extraction."""
    html = """
    <div class="body">
        <h1>Installation</h1>
        <h2>Prerequisites</h2>
        <p>You need Python 3.9+</p>
    </div>
    """
    docs = list(indexer._extract_documents_from_html(html, "install.html"))

    assert len(docs) == 3
    assert docs[0]["hierarchy.lvl0"] == "Installation"
    assert docs[1]["hierarchy.lvl1"] == "Prerequisites"
    assert docs[2]["content"] == "You need Python 3.9+"
```

### Integration Tests

```python
# tests/test_integration.py

def test_full_build_and_index(tmp_path, typesense_server):
    """Test complete Sphinx build with indexing."""
    # Build docs
    app = make_app("html", srcdir=tmp_path / "docs")
    app.build()

    # Verify collection created
    collection = typesense_server.collections["test_docs"].retrieve()
    assert collection["num_documents"] > 0
```

### E2E Tests

```python
# tests/test_e2e.py

def test_search_ui_renders(browser, docs_server):
    """Test search UI appears and functions."""
    browser.get(docs_server.url)

    search_input = browser.find_element(By.CSS_SELECTOR, "#typesense-search input")
    search_input.send_keys("installation")

    # Wait for results
    results = WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".DocSearch-Hits"))
    )
    assert results.is_displayed()
```

---

## Dependencies

### Python Dependencies

```toml
# pyproject.toml

[project]
dependencies = [
    "sphinx>=7.0.0",
    "typesense>=0.21.0",
    "beautifulsoup4>=4.12.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.0.0",
    "sphinx-autobuild>=2024.0.0",
]
```

### JavaScript Dependencies (CDN)

```html
<!-- CSS -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/typesense-docsearch-css@0.4.1" />

<!-- JavaScript -->
<script src="https://cdn.jsdelivr.net/npm/typesense-docsearch.js@3.8.0"></script>
```

### Typesense Server Requirements

- Typesense Server 0.25.0+ or Typesense Cloud
- Minimum 256MB RAM for small documentation sets
- Recommended: 1GB+ RAM for large documentation (10k+ pages)

---

## File Structure

```
sphinx-typesense/
├── pyproject.toml
├── README.md
├── SPECIFICATION.md          # This document
├── LICENSE                   # MIT
├── src/
│   └── sphinx_typesense/
│       ├── __init__.py       # Extension entry point
│       ├── config.py         # Configuration handling
│       ├── indexer.py        # Content extraction & indexing
│       ├── templates.py      # HTML/JS injection
│       ├── themes.py         # Theme-specific selectors
│       └── static/
│           ├── typesense-docsearch.css
│           └── typesense-init.js
├── tests/
│   ├── conftest.py
│   ├── test_config.py
│   ├── test_indexer.py
│   ├── test_templates.py
│   └── test_integration.py
├── docs/
│   ├── conf.py
│   ├── index.rst
│   ├── installation.rst
│   ├── configuration.rst
│   └── themes.rst
└── examples/
    ├── basic/
    ├── rtd-theme/
    └── multi-version/
```

---

## References

### Official Documentation

- [Typesense DocSearch Guide](https://typesense.org/docs/guide/docsearch.html)
- [Typesense API Reference](https://typesense.org/docs/27.0/api/)
- [Sphinx Extension Development](https://www.sphinx-doc.org/en/master/development/index.html)

### Community Resources

- [Integrating Typesense with Sphinx RTD Template](https://writeexperience.co/integrating-typesense-with-sphinx-readthedocs-template-a-step-by-step-guide/)
- [GitHub Issue #695 - Typesense Sphinx Support](https://github.com/typesense/typesense/issues/695)
- [StackOverflow - Sphinx DocSearch Integration](https://stackoverflow.com/questions/54872828/can-sphinx-docs-support-algolias-doc-search/54960623#54960623)

### Similar Projects

- [sphinx-docsearch](https://github.com/algolia/sphinx-docsearch) - Algolia integration (proprietary)
- [typesense-docsearch-scraper](https://github.com/typesense/typesense-docsearch-scraper) - Docker-based scraper

---

## Changelog

### v0.1.0 (Planned)

- Initial release
- Core indexing functionality
- RTD theme support
- DocSearch.js v3 integration

---

*Specification authored based on research from Typesense documentation, community implementations, and Sphinx extension patterns.*
