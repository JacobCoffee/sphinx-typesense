sphinx_typesense.templates
==========================

HTML and JavaScript injection for the sphinx-typesense search UI. This
module handles injecting the Typesense DocSearch configuration and search
container into Sphinx HTML pages.

Module Contents
---------------

.. automodule:: sphinx_typesense.templates
   :members:
   :undoc-members:
   :show-inheritance:

Injection Process
-----------------

The template injection follows these steps for each HTML page:

1. **Container HTML**: Generate a div element with the configured container ID
2. **Config Script**: Generate a script tag with ``window.TYPESENSE_CONFIG``
3. **Meta Tags**: Add meta tags for CSP-compliant JavaScript access
4. **Context Update**: Add the combined HTML to the template context

Generated HTML
--------------

The ``typesense_search_html`` context variable contains:

.. code-block:: html

   <div id="typesense-search"></div>
   <script>
     window.TYPESENSE_CONFIG = {
       "collectionName": "sphinx_docs",
       "host": "localhost",
       "port": "8108",
       "protocol": "http",
       "apiKey": "search_api_key_here",
       "placeholder": "Search documentation...",
       "numTypos": 2,
       "perPage": 10,
       "filterBy": "",
       "container": "#typesense-search"
     };
   </script>

Meta Tags
---------

For Content Security Policy (CSP) compliant implementations, configuration
is also available via meta tags:

.. code-block:: html

   <meta name="typesense-collection" content="sphinx_docs">
   <meta name="typesense-host" content="localhost">
   <meta name="typesense-port" content="8108">
   <meta name="typesense-protocol" content="http">
   <meta name="typesense-api-key" content="search_api_key_here">
   <meta name="typesense-placeholder" content="Search documentation...">
   <meta name="typesense-num-typos" content="2">
   <meta name="typesense-per-page" content="10">
   <meta name="typesense-filter-by" content="">
   <meta name="typesense-container" content="#typesense-search">

JavaScript can read these with:

.. code-block:: javascript

   const host = document.querySelector('meta[name="typesense-host"]')?.content;

Template Integration
--------------------

To include the search UI in custom templates:

.. code-block:: html+jinja

   {# In your theme's layout template #}
   {% if typesense_search_html %}
     {{ typesense_search_html | safe }}
   {% endif %}

Static Assets
-------------

The extension adds the following static files to each page:

- ``typesense-docsearch.css``: DocSearch styling
- ``typesense-docsearch.js``: DocSearch library (priority 500)
- ``typesense-init.js``: Initialization script (priority 501)

These are registered in the main ``setup`` function via:

.. code-block:: python

   app.add_css_file("typesense-docsearch.css")
   app.add_js_file("typesense-docsearch.js", priority=500)
   app.add_js_file("typesense-init.js", priority=501)
