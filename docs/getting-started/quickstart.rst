Quickstart
==========

This guide walks you through the minimal configuration needed to get
search working in your Sphinx documentation.

sphinx-typesense supports two search backends:

- **Typesense**: Server-based search with typo tolerance and advanced features
- **Pagefind**: Static search that works on any hosting platform (no server needed)

By default, the extension uses "auto" mode which selects Typesense if API keys
are configured, otherwise falls back to Pagefind.

Pagefind Backend (Simplest)
---------------------------

For zero-config static search, just add the extension:

.. code-block:: python

   # conf.py
   extensions = [
       # ... your other extensions
       "sphinx_typesense",
   ]

   # Use Pagefind backend (no server required)
   typesense_backend = "pagefind"

That is it. Build your docs and search will work automatically.

Typesense Backend
-----------------

For server-based search with typo tolerance, add the following to your Sphinx ``conf.py``:

.. code-block:: python

   # Add sphinx-typesense to extensions
   extensions = [
       # ... your other extensions
       "sphinx_typesense",
   ]

   # Typesense server connection
   typesense_host = "localhost"
   typesense_port = "8108"
   typesense_protocol = "http"

   # API keys
   typesense_api_key = "your_admin_api_key"
   typesense_search_api_key = "your_search_only_api_key"

Using Environment Variables (Recommended)
-----------------------------------------

For security, use environment variables for API keys:

.. code-block:: python

   import os

   extensions = ["sphinx_typesense"]

   typesense_host = "localhost"
   typesense_port = "8108"
   typesense_protocol = "http"

   # Read API keys from environment
   typesense_api_key = os.environ.get("TYPESENSE_API_KEY", "")
   typesense_search_api_key = os.environ.get("TYPESENSE_SEARCH_API_KEY", "")

Then set the environment variables before building:

.. code-block:: bash

   export TYPESENSE_API_KEY="your_admin_api_key"
   export TYPESENSE_SEARCH_API_KEY="your_search_only_api_key"
   make html

Typesense Cloud Configuration
-----------------------------

If using Typesense Cloud instead of a self-hosted server:

.. code-block:: python

   import os

   extensions = ["sphinx_typesense"]

   # Typesense Cloud connection
   typesense_host = "your-cluster.a1.typesense.net"
   typesense_port = "443"
   typesense_protocol = "https"

   # API keys from Typesense Cloud dashboard
   typesense_api_key = os.environ.get("TYPESENSE_API_KEY", "")
   typesense_search_api_key = os.environ.get("TYPESENSE_SEARCH_API_KEY", "")

Building Your Documentation
---------------------------

Build your documentation as usual:

.. code-block:: bash

   cd docs
   make html

During the build, sphinx-typesense will:

1. Extract content from all generated HTML pages
2. Create a Typesense collection (if it does not exist)
3. Index all documentation content with proper hierarchy

You should see output similar to:

.. code-block:: text

   sphinx-typesense: Indexed 150 documents to Typesense

Disabling Indexing for Development
----------------------------------

During development, you may want to disable indexing to speed up builds:

.. code-block:: python

   # Disable indexing for local development
   typesense_enable_indexing = False

Or use an environment variable:

.. code-block:: python

   import os

   typesense_enable_indexing = os.environ.get("SPHINX_TYPESENSE_INDEX", "false").lower() == "true"

Verifying Search Works
----------------------

After building, open your documentation in a browser. You should see the
Typesense search interface. Try searching for a term that appears in your
documentation to verify the integration is working.

Troubleshooting
---------------

**Build fails with "Missing required configuration"**
   Ensure all required settings are provided: ``typesense_host``, ``typesense_port``,
   ``typesense_protocol``, ``typesense_api_key``, and ``typesense_search_api_key``.

**Indexing completes but search returns no results**
   Check that your Typesense server is running and accessible. Verify the
   ``typesense_search_api_key`` has read permissions on the collection.

**Search UI does not appear**
   Ensure your theme is supported. See :doc:`../themes` for the list of
   supported themes and how to add custom theme support.

Next Steps
----------

- See :doc:`../backends` for detailed information about Typesense vs Pagefind backends
- See :doc:`../configuration` for all available configuration options
- See :doc:`../themes` for theme-specific configuration
- See :doc:`../security` for production security best practices
