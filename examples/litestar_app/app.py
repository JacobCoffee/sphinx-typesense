"""Litestar example application.

A sample Litestar API demonstrating common patterns for REST APIs
that can be documented with Sphinx and searched with sphinx-typesense.
"""

from __future__ import annotations

from litestar import Litestar
from litestar.openapi import OpenAPIConfig
from litestar.openapi.spec import Contact, License

from .controllers import HealthController, ItemController, UserController


def create_app() -> Litestar:
    """Create and configure the Litestar application.

    This factory function creates a configured Litestar application
    with all controllers registered and OpenAPI documentation enabled.

    Returns:
        Litestar: Configured application instance.

    Example:
        >>> app = create_app()
        >>> # Use with ASGI server
        >>> # uvicorn examples.litestar_app.app:create_app --factory

    """
    return Litestar(
        route_handlers=[
            HealthController,
            UserController,
            ItemController,
        ],
        openapi_config=OpenAPIConfig(
            title="Example Litestar API",
            version="1.0.0",
            description=(
                "A sample Litestar API demonstrating common REST patterns. "
                "This API is used as documentation source material for "
                "sphinx-typesense search functionality."
            ),
            contact=Contact(
                name="API Support",
                email="support@example.com",
            ),
            license=License(
                name="MIT",
                identifier="MIT",
            ),
            tags=[
                {"name": "Health", "description": "Health check endpoints"},
                {"name": "Users", "description": "User management operations"},
                {"name": "Items", "description": "Inventory item operations"},
            ],
        ),
        debug=True,
    )


app = create_app()
"""The application instance for ASGI servers.

Use this instance when running with an ASGI server like uvicorn:

.. code-block:: bash

    uvicorn examples.litestar_app.app:app --reload

Or use the factory function for programmatic creation:

.. code-block:: bash

    uvicorn examples.litestar_app.app:create_app --factory
"""
