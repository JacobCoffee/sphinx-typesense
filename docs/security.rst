Security
========

This page documents security best practices for using sphinx-typesense
in production environments.

API Key Separation
------------------

sphinx-typesense uses two API keys with different permission levels:

Admin API Key (``typesense_api_key``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This key is used for:

- Creating and managing collections
- Indexing documents during builds

**Required permissions**:

- ``collections:create``
- ``collections:delete`` (if using ``typesense_drop_existing``)
- ``documents:create``
- ``documents:update``
- ``documents:delete``

**Security considerations**:

- Never expose this key in client-side code
- Only use during build processes
- Store securely in CI/CD secrets

Search API Key (``typesense_search_api_key``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This key is used for:

- Frontend search queries
- Exposed in browser JavaScript

**Required permissions**:

- ``documents:search`` (read-only)

**Security considerations**:

- Should be scoped to search-only operations
- Safe to expose in client-side code
- Consider scoping to specific collections

Creating Scoped API Keys
------------------------

In Typesense, create a scoped search key for production:

.. code-block:: bash

   curl 'http://localhost:8108/keys' \
     -X POST \
     -H "X-TYPESENSE-API-KEY: ${TYPESENSE_ADMIN_KEY}" \
     -H 'Content-Type: application/json' \
     -d '{
       "description": "Search-only key for docs",
       "actions": ["documents:search"],
       "collections": ["sphinx_docs"]
     }'

Environment Variables
---------------------

Never hardcode API keys in ``conf.py``. Use environment variables:

.. code-block:: python

   import os

   typesense_api_key = os.environ.get("TYPESENSE_API_KEY", "")
   typesense_search_api_key = os.environ.get("TYPESENSE_SEARCH_API_KEY", "")

For local development, use a ``.env`` file (add to ``.gitignore``):

.. code-block:: bash

   # .env (DO NOT COMMIT)
   TYPESENSE_API_KEY=your_admin_key_here
   TYPESENSE_SEARCH_API_KEY=your_search_key_here

CI/CD Best Practices
--------------------

GitHub Actions
~~~~~~~~~~~~~~

Store API keys as repository secrets:

.. code-block:: yaml

   # .github/workflows/docs.yml
   name: Build Documentation

   on:
     push:
       branches: [main]

   jobs:
     build:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4

         - name: Build docs
           env:
             TYPESENSE_API_KEY: ${{ secrets.TYPESENSE_API_KEY }}
             TYPESENSE_SEARCH_API_KEY: ${{ secrets.TYPESENSE_SEARCH_API_KEY }}
           run: |
             make html

GitLab CI
~~~~~~~~~

Use CI/CD variables (Settings > CI/CD > Variables):

.. code-block:: yaml

   # .gitlab-ci.yml
   build_docs:
     script:
       - make html
     variables:
       TYPESENSE_API_KEY: $TYPESENSE_API_KEY
       TYPESENSE_SEARCH_API_KEY: $TYPESENSE_SEARCH_API_KEY

Read the Docs
~~~~~~~~~~~~~

Set environment variables in project settings (Admin > Environment Variables):

- ``TYPESENSE_API_KEY``: Your admin key
- ``TYPESENSE_SEARCH_API_KEY``: Your search key

Network Security
----------------

HTTPS in Production
~~~~~~~~~~~~~~~~~~~

Always use HTTPS for production Typesense connections:

.. code-block:: python

   typesense_protocol = "https"
   typesense_port = "443"

Typesense Cloud
~~~~~~~~~~~~~~~

Typesense Cloud enforces HTTPS and provides automatic TLS certificates.

Self-hosted Typesense
~~~~~~~~~~~~~~~~~~~~~

For self-hosted instances:

1. Use a reverse proxy (nginx, Caddy) with TLS termination
2. Or configure Typesense with TLS certificates directly

Content Security
----------------

Indexed Content
~~~~~~~~~~~~~~~

Be aware that sphinx-typesense indexes all content from your HTML output.
This includes:

- Page titles and headings
- Paragraph text
- List items

**Do not include** sensitive information in your documentation that should
not be searchable.

Search Result Filtering
~~~~~~~~~~~~~~~~~~~~~~~

Use ``typesense_filter_by`` to restrict search results:

.. code-block:: python

   # Only show results for the current version
   typesense_filter_by = f"version:={release}"

Audit and Monitoring
--------------------

Enable Typesense API logging to monitor usage:

.. code-block:: json

   {
     "log-level": "info",
     "enable-access-logging": true
   }

Monitor for:

- Unusual query patterns
- Failed authentication attempts
- High request volumes

Security Checklist
------------------

Before deploying to production:

.. code-block:: text

   [ ] Admin API key stored in CI/CD secrets, not in code
   [ ] Search API key has read-only permissions
   [ ] HTTPS enabled for Typesense connection
   [ ] API keys not committed to version control
   [ ] .env file added to .gitignore
   [ ] Typesense server not publicly accessible (if self-hosted)
   [ ] Search key scoped to specific collection(s)
