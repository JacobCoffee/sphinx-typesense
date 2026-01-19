Litestar Example API Documentation
===================================

This documentation demonstrates the sphinx-typesense search integration
with a sample Litestar REST API application.

The example API provides endpoints for managing users and items, along with
health check functionality. This documentation is auto-generated from Python
docstrings using Sphinx autodoc.

Getting Started
---------------

The example application can be run with uvicorn:

.. code-block:: bash

   uvicorn examples.litestar_app.app:app --reload

Or using the factory function:

.. code-block:: bash

   uvicorn examples.litestar_app.app:create_app --factory

API Overview
------------

**Health Checks**
   Monitor application health and readiness.

**Users**
   Full CRUD operations for user management with role-based access.

**Items**
   Inventory management with filtering and reservation support.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
