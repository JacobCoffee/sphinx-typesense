Theme Support
=============

sphinx-typesense supports multiple popular Sphinx themes out of the box.
This page documents the supported themes, their content selectors, and how
to add support for custom themes.

Supported Themes
----------------

The following themes are automatically detected and configured:

.. list-table::
   :header-rows: 1
   :widths: 25 35 40

   * - Theme
     - Package Name
     - Content Selectors
   * - ReadTheDocs
     - ``sphinx_rtd_theme``
     - ``.wy-nav-content-wrap``, ``.wy-nav-content``, ``[role=main]``
   * - Furo
     - ``furo``
     - ``article[role=main]``, ``.content``
   * - Alabaster
     - ``alabaster``
     - ``.body``, ``.document``
   * - PyData
     - ``pydata_sphinx_theme``
     - ``article.bd-article``, ``main.bd-content``
   * - Book
     - ``sphinx_book_theme``
     - ``main#main-content``, ``article.bd-article``

Search Bar Placement
--------------------

Each theme has a different location for the search bar. sphinx-typesense
automatically detects the appropriate placement:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Theme
     - Search Placement Selector
   * - ReadTheDocs
     - ``.wy-side-nav-search``
   * - Furo
     - ``.sidebar-search-container``
   * - Alabaster
     - ``.searchbox``
   * - PyData
     - ``nav.bd-search``
   * - Book
     - ``.search-button-field``

Default Fallback
----------------

For themes not in the supported list, sphinx-typesense uses these fallback
selectors:

**Content Selectors** (in priority order):

1. ``article[role=main]``
2. ``main``
3. ``.body``
4. ``.document``
5. ``[role=main]``

**Search Placement**: ``#typesense-search``

Custom Theme Support
--------------------

If your theme is not automatically detected, you can provide custom selectors
in your ``conf.py``:

.. code-block:: python

   # Custom content selectors
   typesense_content_selectors = [
       ".my-theme-content",
       "article.main-content",
       "main",
   ]

Content Selector Guidelines
~~~~~~~~~~~~~~~~~~~~~~~~~~~

When defining custom content selectors:

1. **Be specific**: Target the main content area, not navigation or sidebars
2. **Order matters**: List selectors from most specific to least specific
3. **Exclude noise**: The selector should not include headers, footers, or TOCs
4. **Test extraction**: Build your docs and verify the indexed content is correct

Example for a custom theme:

.. code-block:: python

   # For a theme with main content in <article class="content-main">
   typesense_content_selectors = [
       "article.content-main",
       ".content-main",
       "article",
   ]

Search Container Placement
~~~~~~~~~~~~~~~~~~~~~~~~~~

The search container selector determines where the search UI is injected.
For most custom themes, you can:

1. Add a container div in your theme template:

   .. code-block:: html

      <div id="typesense-search"></div>

2. Use the default selector (no configuration needed):

   .. code-block:: python

      typesense_container = "#typesense-search"

Or specify a custom selector:

.. code-block:: python

   typesense_container = ".my-search-wrapper"

Theme Detection
---------------

sphinx-typesense detects your theme from the ``html_theme`` setting in
``conf.py``. The detection happens automatically at build time.

To verify which theme is detected:

.. code-block:: python

   from sphinx_typesense.themes import get_theme_config

   # In a Sphinx extension or build script
   config = get_theme_config(app)
   print(f"Detected theme: {config.name}")
   print(f"Content selectors: {config.content_selectors}")

Contributing Theme Support
--------------------------

To add support for a new theme:

1. Identify the theme's content area CSS selector(s)
2. Identify the search bar placement selector
3. Submit a pull request adding the theme to ``sphinx_typesense/themes.py``

Example addition to ``THEME_CONFIGS``:

.. code-block:: python

   "my_custom_theme": ThemeConfig(
       name="my_custom_theme",
       content_selectors=(".custom-content", "article"),
       search_container_selectors=(".custom-search",),
       search_input_selector='input[name="q"]',
   ),

Troubleshooting
---------------

**Content not being indexed correctly**
   Check that your content selectors match the actual HTML structure.
   Use browser developer tools to inspect the generated HTML.

**Search bar not appearing**
   Verify the search container selector exists in your theme's HTML.
   You may need to add a container div to your theme templates.

**Wrong content indexed (navigation, sidebars)**
   Your content selector is too broad. Use a more specific selector
   that targets only the main content area.
