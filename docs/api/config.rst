sphinx_typesense.config
=======================

Configuration handling for sphinx-typesense. This module manages all
Typesense-related configuration values, including validation, defaults,
and environment variable support.

Module Contents
---------------

.. automodule:: sphinx_typesense.config
   :members:
   :undoc-members:
   :show-inheritance:

Constants
---------

Default Values
~~~~~~~~~~~~~~

.. py:data:: DEFAULT_HOST
   :type: str
   :value: "localhost"

   Default Typesense server hostname.

.. py:data:: DEFAULT_PORT
   :type: str
   :value: "8108"

   Default Typesense server port.

.. py:data:: DEFAULT_PROTOCOL
   :type: str
   :value: "http"

   Default connection protocol.

.. py:data:: DEFAULT_COLLECTION_NAME
   :type: str
   :value: "sphinx_docs"

   Default collection name for indexed documents.

.. py:data:: DEFAULT_PLACEHOLDER
   :type: str
   :value: "Search documentation..."

   Default placeholder text for search input.

.. py:data:: DEFAULT_NUM_TYPOS
   :type: int
   :value: 2

   Default typo tolerance level.

.. py:data:: DEFAULT_PER_PAGE
   :type: int
   :value: 10

   Default number of results per page.

.. py:data:: DEFAULT_CONTAINER
   :type: str
   :value: "#typesense-search"

   Default CSS selector for search container.

Validation Constants
~~~~~~~~~~~~~~~~~~~~

.. py:data:: MIN_NUM_TYPOS
   :type: int
   :value: 0

   Minimum allowed value for typo tolerance.

.. py:data:: MAX_NUM_TYPOS
   :type: int
   :value: 2

   Maximum allowed value for typo tolerance.

.. py:data:: VALID_PROTOCOLS
   :type: set[str]
   :value: {"http", "https"}

   Valid protocol values.

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

.. py:data:: ENV_API_KEY
   :type: str
   :value: "TYPESENSE_API_KEY"

   Environment variable name for admin API key fallback.

.. py:data:: ENV_SEARCH_API_KEY
   :type: str
   :value: "TYPESENSE_SEARCH_API_KEY"

   Environment variable name for search API key fallback.

Theme Selectors
~~~~~~~~~~~~~~~

.. py:data:: DEFAULT_CONTENT_SELECTORS
   :type: list[str]

   Default CSS selectors for content extraction, used when theme-specific
   selectors are not available:

   - ``.wy-nav-content-wrap`` (RTD theme)
   - ``article.bd-article`` (PyData theme)
   - ``.body`` (Alabaster)
   - ``article[role=main]`` (Furo)
   - ``main`` (Generic fallback)
