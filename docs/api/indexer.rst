sphinx_typesense.indexer
========================

Content extraction and Typesense indexing. This module handles extracting
searchable content from Sphinx HTML output and indexing it into Typesense
collections using a DocSearch-compatible hierarchical schema.

Module Contents
---------------

.. automodule:: sphinx_typesense.indexer
   :members:
   :undoc-members:
   :show-inheritance:

TypesenseIndexer Usage
~~~~~~~~~~~~~~~~~~~~~~

The main indexer class handles the complete indexing pipeline:

1. Initialize Typesense client from Sphinx config
2. Ensure collection exists with correct schema
3. Parse HTML files and extract hierarchical content
4. Create and bulk import documents

**Usage Example**:

.. code-block:: python

   from sphinx_typesense.indexer import TypesenseIndexer

   # In a Sphinx event handler or build script
   indexer = TypesenseIndexer(app)
   count = indexer.index_all()
   print(f"Indexed {count} documents")

Constants Reference
-------------------

Collection Schema
~~~~~~~~~~~~~~~~~

The ``DOCS_SCHEMA`` constant defines the Typesense collection schema for
documentation. It follows the DocSearch schema for frontend compatibility.
Fields include:

- ``hierarchy.lvl0-3``: Hierarchical heading levels (faceted)
- ``content``: Paragraph/list text
- ``url``: Full URL with anchor
- ``url_without_anchor``: URL without fragment
- ``anchor``: Fragment identifier
- ``type``: Document type (lvl0, lvl1, content, etc.)
- ``version``: Documentation version (faceted)
- ``language``: Content language (faceted)
- ``weight``: Search ranking weight
- ``item_priority``: Default sorting priority

Document Weights
~~~~~~~~~~~~~~~~

The ``DOC_TYPE_WEIGHTS`` and ``DOC_TYPE_PRIORITIES`` constants define
weight values for search ranking by document type:

- ``lvl0``: 100 (page titles)
- ``lvl1``: 90 (h2 headings)
- ``lvl2``: 80 (h3 headings)
- ``lvl3``: 70 (h4 headings)
- ``content``: 50 (paragraphs and list items)

Indexing Process
----------------

The indexing process follows these steps:

1. **Collection Setup**: Create the Typesense collection if it does not exist,
   or drop and recreate if ``typesense_drop_existing`` is True.

2. **HTML Parsing**: Iterate through all ``.html`` files in the build output
   directory.

3. **Content Extraction**: For each HTML file:

   - Find the main content element using theme-specific selectors
   - Extract hierarchical structure (h1 > h2 > h3 > h4)
   - Extract content from paragraphs and list items
   - Generate unique document IDs using SHA256 hashes

4. **Bulk Import**: Import all documents to Typesense using the upsert action.

Document Structure
------------------

Each indexed document has the following structure:

.. code-block:: python

   {
       "id": "abc123...",                    # SHA256 hash
       "hierarchy.lvl0": "Page Title",       # h1
       "hierarchy.lvl1": "Section",          # h2
       "hierarchy.lvl2": "Subsection",       # h3
       "hierarchy.lvl3": "Sub-subsection",   # h4
       "content": "Paragraph text...",       # p, li
       "url": "page.html#anchor",
       "url_without_anchor": "page.html",
       "anchor": "anchor",
       "type": "content",                    # lvl0, lvl1, lvl2, lvl3, content
       "version": "1.0",
       "language": "en",
       "weight": 50,
       "item_priority": 50,
   }
