Configuration
=============

This page documents all configuration options for sphinx-typesense.
Add these settings to your Sphinx ``conf.py`` file.

Backend Selection
-----------------

typesense_backend
~~~~~~~~~~~~~~~~~

:Type: ``str``
:Default: ``"auto"``
:Valid Values: ``"auto"``, ``"typesense"``, ``"pagefind"``

Select the search backend to use.

- ``"auto"`` (default): Use Typesense if API key is configured, otherwise Pagefind
- ``"typesense"``: Force Typesense backend (requires API keys)
- ``"pagefind"``: Force Pagefind backend (static search, no server needed)

.. code-block:: python

   # Auto-select based on configuration (recommended)
   typesense_backend = "auto"

   # Or force a specific backend
   typesense_backend = "pagefind"  # Static search only
   typesense_backend = "typesense"  # Server-based search

See :doc:`backends` for detailed information about each backend.

Server Settings (Typesense Backend)
-----------------------------------

These settings configure the Typesense server connection. They are required
when using the Typesense backend (``typesense_backend = "typesense"`` or
``"auto"`` with API keys configured).

typesense_host
~~~~~~~~~~~~~~

:Type: ``str``
:Default: ``"localhost"``

The hostname or IP address of your Typesense server.

.. code-block:: python

   # Self-hosted
   typesense_host = "localhost"

   # Typesense Cloud
   typesense_host = "your-cluster.a1.typesense.net"

typesense_port
~~~~~~~~~~~~~~

:Type: ``str``
:Default: ``"8108"``

The port number for your Typesense server.

.. code-block:: python

   # Self-hosted (default port)
   typesense_port = "8108"

   # Typesense Cloud
   typesense_port = "443"

typesense_protocol
~~~~~~~~~~~~~~~~~~

:Type: ``str``
:Default: ``"http"``
:Valid Values: ``"http"``, ``"https"``

The protocol to use for connecting to Typesense.

.. code-block:: python

   # Self-hosted (local development)
   typesense_protocol = "http"

   # Production / Typesense Cloud
   typesense_protocol = "https"

typesense_api_key
~~~~~~~~~~~~~~~~~

:Type: ``str``
:Default: ``""``
:Environment Variable: ``TYPESENSE_API_KEY``

The admin API key for indexing operations. This key needs write permissions
to create collections and index documents.

.. warning::

   Never commit API keys to version control. Use environment variables.

.. code-block:: python

   import os
   typesense_api_key = os.environ.get("TYPESENSE_API_KEY", "")

typesense_search_api_key
~~~~~~~~~~~~~~~~~~~~~~~~

:Type: ``str``
:Default: ``""``
:Environment Variable: ``TYPESENSE_SEARCH_API_KEY``

The search-only API key for the frontend search interface. This key should
have read-only permissions for security.

.. code-block:: python

   import os
   typesense_search_api_key = os.environ.get("TYPESENSE_SEARCH_API_KEY", "")

Optional Settings
-----------------

Collection Settings
~~~~~~~~~~~~~~~~~~~

typesense_collection_name
^^^^^^^^^^^^^^^^^^^^^^^^^

:Type: ``str``
:Default: ``"sphinx_docs"``

The name of the Typesense collection to use for indexing.

.. code-block:: python

   # Use a project-specific collection name
   typesense_collection_name = "myproject_docs"

   # Version-specific collection
   typesense_collection_name = f"myproject_docs_v{release}"

typesense_doc_version
^^^^^^^^^^^^^^^^^^^^^

:Type: ``str``
:Default: ``""``

A version tag to associate with indexed documents. Useful for filtering
search results by documentation version.

.. code-block:: python

   typesense_doc_version = release  # Use Sphinx release version

Search UI Settings
~~~~~~~~~~~~~~~~~~

typesense_placeholder
^^^^^^^^^^^^^^^^^^^^^

:Type: ``str``
:Default: ``"Search documentation..."``

Placeholder text displayed in the search input field.

.. code-block:: python

   typesense_placeholder = "Search the docs..."

typesense_num_typos
^^^^^^^^^^^^^^^^^^^

:Type: ``int``
:Default: ``2``
:Valid Range: ``0`` to ``2``

The number of typos to tolerate in search queries. Higher values provide
more fuzzy matching but may return less relevant results.

.. code-block:: python

   # Strict matching (no typos)
   typesense_num_typos = 0

   # Default (2 typos)
   typesense_num_typos = 2

typesense_per_page
^^^^^^^^^^^^^^^^^^

:Type: ``int``
:Default: ``10``

The number of search results to display per page.

.. code-block:: python

   typesense_per_page = 15

typesense_container
^^^^^^^^^^^^^^^^^^^

:Type: ``str``
:Default: ``"#typesense-search"``

CSS selector for the search container element.

.. code-block:: python

   typesense_container = "#my-search-container"

typesense_filter_by
^^^^^^^^^^^^^^^^^^^

:Type: ``str``
:Default: ``""``

Default filter to apply to all search queries. Uses Typesense filter syntax.

.. code-block:: python

   # Filter by version
   typesense_filter_by = "version:=1.0"

   # Filter by language
   typesense_filter_by = "language:=en"

Content Extraction Settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~

typesense_content_selectors
^^^^^^^^^^^^^^^^^^^^^^^^^^^

:Type: ``list[str]``
:Default: Theme-specific selectors

List of CSS selectors to use for extracting main content from HTML pages.
Selectors are tried in order; the first match is used.

.. code-block:: python

   # Custom selectors for a custom theme
   typesense_content_selectors = [
       ".my-content-area",
       "article.main",
       "main",
   ]

See :doc:`themes` for default selectors for each supported theme.

Advanced Settings
~~~~~~~~~~~~~~~~~

typesense_enable_indexing
^^^^^^^^^^^^^^^^^^^^^^^^^

:Type: ``bool``
:Default: ``True``

Enable or disable automatic indexing during builds.

.. code-block:: python

   # Disable for local development
   typesense_enable_indexing = False

   # Enable based on environment
   import os
   typesense_enable_indexing = os.environ.get("CI", "false") == "true"

typesense_drop_existing
^^^^^^^^^^^^^^^^^^^^^^^

:Type: ``bool``
:Default: ``False``

Drop and recreate the collection before indexing. Useful for clean rebuilds.

.. warning::

   This will delete all existing documents in the collection.

.. code-block:: python

   # Force clean reindex
   typesense_drop_existing = True

Environment Variables
---------------------

sphinx-typesense supports the following environment variables as fallbacks
for API key configuration:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Variable
     - Description
   * - ``TYPESENSE_API_KEY``
     - Admin API key for indexing
   * - ``TYPESENSE_SEARCH_API_KEY``
     - Search-only API key for frontend

These are used when the corresponding conf.py settings are empty.

Complete Example
----------------

Here is a complete configuration example:

.. code-block:: python

   import os

   # sphinx-typesense extension
   extensions = ["sphinx_typesense"]

   # Server connection
   typesense_host = os.environ.get("TYPESENSE_HOST", "localhost")
   typesense_port = os.environ.get("TYPESENSE_PORT", "8108")
   typesense_protocol = os.environ.get("TYPESENSE_PROTOCOL", "http")

   # API keys (from environment)
   typesense_api_key = os.environ.get("TYPESENSE_API_KEY", "")
   typesense_search_api_key = os.environ.get("TYPESENSE_SEARCH_API_KEY", "")

   # Collection settings
   typesense_collection_name = f"myproject_docs_{release}"
   typesense_doc_version = release

   # Search UI
   typesense_placeholder = "Search MyProject docs..."
   typesense_num_typos = 2
   typesense_per_page = 10

   # Indexing behavior
   typesense_enable_indexing = os.environ.get("CI", "false") == "true"
   typesense_drop_existing = False
