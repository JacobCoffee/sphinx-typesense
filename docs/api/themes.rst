sphinx_typesense.themes
=======================

Theme-specific selectors and configuration. This module provides content
selectors and search bar placement logic for various Sphinx themes, enabling
automatic detection and proper integration.

Module Contents
---------------

.. automodule:: sphinx_typesense.themes
   :members:
   :undoc-members:
   :show-inheritance:

ThemeConfig Class
~~~~~~~~~~~~~~~~~

The ``ThemeConfig`` is a frozen dataclass containing configuration for a
specific Sphinx theme with these attributes:

- ``name``: Theme package name
- ``content_selectors``: CSS selectors for main content area
- ``search_container_selectors``: CSS selectors for search bar placement
- ``search_input_selector``: CSS selector for existing search input

Constants Reference
-------------------

Theme Registries
~~~~~~~~~~~~~~~~

``THEME_SELECTORS`` provides CSS selectors for extracting main content from
each supported theme. Listed in priority order (first match wins).

**Supported themes**:

- ``sphinx_rtd_theme``
- ``furo``
- ``alabaster``
- ``pydata_sphinx_theme``
- ``sphinx_book_theme``

``SEARCH_PLACEMENT_SELECTORS`` provides CSS selectors for where to inject
the search bar in each theme.

``THEME_CONFIGS`` contains complete theme configurations with all details
including content selectors, search container selectors, and search input
selectors.

Default Fallbacks
~~~~~~~~~~~~~~~~~

``DEFAULT_CONTENT_SELECTORS`` provides fallback selectors used when theme
is not recognized:

1. ``article[role=main]``
2. ``main``
3. ``.body``
4. ``.document``
5. ``[role=main]``

``DEFAULT_SEARCH_PLACEMENT`` is ``#typesense-search`` by default.

``DEFAULT_SEARCH_CONTAINER_SELECTORS`` includes:

- ``#typesense-search``
- ``.search``
- ``.searchbox``

Function Examples
-----------------

Content Selectors
~~~~~~~~~~~~~~~~~

.. code-block:: python

   >>> from sphinx_typesense.themes import get_content_selectors
   >>> get_content_selectors("furo")
   ['article[role=main]', '.content']

   >>> get_content_selectors("furo", [".my-content"])
   ['.my-content']

   >>> get_content_selectors("unknown_theme")
   ['article[role=main]', 'main', '.body', '.document', '[role=main]']

Search Placement
~~~~~~~~~~~~~~~~

.. code-block:: python

   >>> from sphinx_typesense.themes import get_search_placement
   >>> get_search_placement("sphinx_rtd_theme")
   '.wy-side-nav-search'

   >>> get_search_placement("unknown_theme")
   '#typesense-search'

Adding New Themes
-----------------

To add support for a new theme, add entries to the module constants:

.. code-block:: python

   # In sphinx_typesense/themes.py

   THEME_SELECTORS["my_theme"] = [
       ".my-content-area",
       "main.content",
   ]

   SEARCH_PLACEMENT_SELECTORS["my_theme"] = ".my-search-container"

   THEME_CONFIGS["my_theme"] = ThemeConfig(
       name="my_theme",
       content_selectors=(".my-content-area", "main.content"),
       search_container_selectors=(".my-search-container",),
       search_input_selector='input[type="search"]',
   )
