API Reference
=============

This section provides detailed API documentation for all sphinx-typesense
modules, classes, and functions.

.. toctree::
   :maxdepth: 2

   config
   indexer
   templates
   themes

Module Overview
---------------

sphinx-typesense consists of the following modules:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Module
     - Description
   * - :doc:`config`
     - Configuration handling, validation, and defaults
   * - :doc:`indexer`
     - Content extraction and Typesense indexing
   * - :doc:`templates`
     - HTML and JavaScript injection for search UI
   * - :doc:`themes`
     - Theme-specific selectors and configuration

Extension Entry Point
---------------------

The main entry point is the ``setup`` function in the package root:

.. autofunction:: sphinx_typesense.setup

.. autofunction:: sphinx_typesense.index_documents
