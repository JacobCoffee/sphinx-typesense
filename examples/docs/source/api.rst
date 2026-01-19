API Reference
=============

This section contains the complete API reference for the Litestar example
application, auto-generated from Python docstrings.

Application
-----------

.. automodule:: litestar_app
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: litestar_app.app
   :members:
   :undoc-members:
   :show-inheritance:

Models
------

The models module contains Pydantic models for request validation and
response serialization.

.. automodule:: litestar_app.models
   :members:
   :undoc-members:
   :show-inheritance:

Enumerations
~~~~~~~~~~~~

.. autoclass:: litestar_app.models.UserRole
   :members:
   :undoc-members:

.. autoclass:: litestar_app.models.ItemStatus
   :members:
   :undoc-members:

User Models
~~~~~~~~~~~

.. autoclass:: litestar_app.models.UserCreate
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: litestar_app.models.UserResponse
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: litestar_app.models.UserUpdate
   :members:
   :undoc-members:
   :show-inheritance:

Item Models
~~~~~~~~~~~

.. autoclass:: litestar_app.models.ItemCreate
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: litestar_app.models.ItemResponse
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: litestar_app.models.ItemUpdate
   :members:
   :undoc-members:
   :show-inheritance:

Response Models
~~~~~~~~~~~~~~~

.. autoclass:: litestar_app.models.HealthResponse
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: litestar_app.models.PaginatedResponse
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: litestar_app.models.ErrorResponse
   :members:
   :undoc-members:
   :show-inheritance:

Controllers
-----------

The controllers module contains route handlers organized by resource type.

.. automodule:: litestar_app.controllers
   :members:
   :undoc-members:
   :show-inheritance:

Health Controller
~~~~~~~~~~~~~~~~~

.. automodule:: litestar_app.controllers.health
   :members:
   :undoc-members:
   :show-inheritance:

User Controller
~~~~~~~~~~~~~~~

.. automodule:: litestar_app.controllers.users
   :members:
   :undoc-members:
   :show-inheritance:

Item Controller
~~~~~~~~~~~~~~~

.. automodule:: litestar_app.controllers.items
   :members:
   :undoc-members:
   :show-inheritance:
