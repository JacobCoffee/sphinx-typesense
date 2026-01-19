Search Backends
===============

sphinx-typesense supports two search backends, giving you flexibility to choose
the right solution for your deployment environment.

.. contents:: On this page
   :local:
   :depth: 2

Overview
--------

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Feature
     - Typesense
     - Pagefind
   * - Server Required
     - Yes (self-hosted or cloud)
     - No (static files only)
   * - Typo Tolerance
     - Built-in (0-2 typos)
     - Basic
   * - Hosting
     - Any (requires API)
     - Static hosting (GitHub Pages, Netlify, etc.)
   * - Cost
     - Server costs or Typesense Cloud pricing
     - Free
   * - Best For
     - Large sites, advanced search features
     - Small-to-medium sites, zero-cost deployment

Typesense Backend
-----------------

The Typesense backend provides server-based search using Typesense Server or
Typesense Cloud.

Advantages
~~~~~~~~~~

- **Typo Tolerance**: Built-in fuzzy matching with configurable typo tolerance (0-2)
- **Fast Search**: Sub-50ms search responses even for large documentation sites
- **Advanced Features**: Faceting, filtering, and weighted ranking
- **Scalability**: Handles large documentation portals with thousands of pages
- **Real-time Updates**: Index updates are immediately searchable

Requirements
~~~~~~~~~~~~

- Typesense Server (self-hosted) or Typesense Cloud account
- Admin API key for indexing (write permissions)
- Search API key for frontend (read-only permissions)

Configuration
~~~~~~~~~~~~~

.. code-block:: python

   # conf.py
   extensions = ["sphinx_typesense"]

   typesense_backend = "typesense"

   # Server connection
   typesense_host = "localhost"
   typesense_port = "8108"
   typesense_protocol = "http"

   # API keys (use environment variables in production)
   import os
   typesense_api_key = os.environ.get("TYPESENSE_API_KEY", "")
   typesense_search_api_key = os.environ.get("TYPESENSE_SEARCH_API_KEY", "")

For Typesense Cloud:

.. code-block:: python

   typesense_backend = "typesense"
   typesense_host = "your-cluster.a1.typesense.net"
   typesense_port = "443"
   typesense_protocol = "https"

Pagefind Backend
----------------

The Pagefind backend provides static search that runs entirely in the browser.
No server is required after the build process completes.

Advantages
~~~~~~~~~~

- **No Server Required**: Search runs entirely client-side in the browser
- **Zero-Cost Deployment**: Works on free static hosting platforms
- **Simple Setup**: No API keys or server configuration needed
- **Privacy**: No search queries sent to external servers
- **Fast for Small Sites**: Efficient for documentation with hundreds of pages

Requirements
~~~~~~~~~~~~

Install Pagefind using one of these methods (in order of recommendation):

1. **Python package** (recommended): ``pip install sphinx-typesense[pagefind]``

   This bundles the Pagefind binary and requires no Node.js installation.

2. **npm global install**: ``npm install -g pagefind``

   Requires Node.js to be installed.

3. **npx** (auto-downloads on first run): Just have ``npx`` available

   Pagefind will be downloaded automatically when needed.

Configuration
~~~~~~~~~~~~~

Minimal configuration for Pagefind:

.. code-block:: python

   # conf.py
   extensions = ["sphinx_typesense"]

   typesense_backend = "pagefind"

Optional customization:

.. code-block:: python

   # conf.py
   typesense_backend = "pagefind"

   # Customize search UI
   typesense_placeholder = "Search docs..."
   typesense_container = "#search-box"

How It Works
~~~~~~~~~~~~

When using the Pagefind backend:

1. Sphinx builds your documentation HTML as usual
2. After the build, Pagefind indexes all HTML files in the output directory
3. Pagefind generates a static search index (JavaScript and JSON files)
4. The search UI loads this index and performs searches client-side

The generated index files are typically small (a few hundred KB for most
documentation sites) and are loaded on-demand.

Auto Backend Selection
----------------------

The ``"auto"`` mode (default) automatically selects the best backend based on
your configuration:

1. If ``typesense_api_key`` is set and not empty, use Typesense
2. Otherwise, use Pagefind

This is ideal for workflows where:

- You want full Typesense search in production (CI/CD with API keys)
- You want working search in local development (without running Typesense)
- You want to test documentation changes without server dependencies

Configuration
~~~~~~~~~~~~~

.. code-block:: python

   # conf.py - Auto backend (recommended for most projects)
   import os

   extensions = ["sphinx_typesense"]

   typesense_backend = "auto"  # This is the default

   # Typesense settings (only used when API key is available)
   typesense_host = os.environ.get("TYPESENSE_HOST", "localhost")
   typesense_port = os.environ.get("TYPESENSE_PORT", "8108")
   typesense_protocol = os.environ.get("TYPESENSE_PROTOCOL", "http")

   # When these are set, Typesense is used; otherwise Pagefind
   typesense_api_key = os.environ.get("TYPESENSE_API_KEY", "")
   typesense_search_api_key = os.environ.get("TYPESENSE_SEARCH_API_KEY", "")

Example Workflow
~~~~~~~~~~~~~~~~

**Local Development** (no environment variables set):

.. code-block:: bash

   # No API keys configured - Pagefind is used automatically
   make html
   # Output: "sphinx-typesense: Using Pagefind backend (auto-selected)"

**CI/CD Production Build** (environment variables set):

.. code-block:: bash

   export TYPESENSE_API_KEY="your_admin_key"
   export TYPESENSE_SEARCH_API_KEY="your_search_key"
   make html
   # Output: "sphinx-typesense: Using Typesense backend"

Choosing a Backend
------------------

Use **Typesense** when:

- You need typo-tolerant search with fuzzy matching
- Your documentation has thousands of pages
- You want advanced search features (faceting, filtering)
- You already have Typesense infrastructure
- You need real-time index updates

Use **Pagefind** when:

- You deploy to static hosting (GitHub Pages, Netlify, Vercel)
- You want zero-cost, zero-maintenance search
- Your documentation has fewer than 1000 pages
- You do not need advanced search features
- Privacy is important (no external API calls)

Use **Auto** (default) when:

- You want the best of both worlds
- Your team has mixed environments (some with Typesense, some without)
- You want search to "just work" regardless of environment

Migration Between Backends
--------------------------

Switching backends is straightforward since both use the same configuration
structure for UI customization:

.. code-block:: python

   # These settings work with both backends
   typesense_placeholder = "Search documentation..."
   typesense_container = "#typesense-search"

To switch from Pagefind to Typesense, add the API key configuration:

.. code-block:: python

   # Before: Pagefind (no API keys)
   typesense_backend = "pagefind"

   # After: Typesense (with API keys)
   typesense_backend = "typesense"
   typesense_api_key = os.environ.get("TYPESENSE_API_KEY", "")
   typesense_search_api_key = os.environ.get("TYPESENSE_SEARCH_API_KEY", "")

To switch from Typesense to Pagefind, simply change the backend:

.. code-block:: python

   # Before: Typesense
   typesense_backend = "typesense"

   # After: Pagefind (API keys are ignored)
   typesense_backend = "pagefind"
