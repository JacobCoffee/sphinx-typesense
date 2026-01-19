"""Litestar example application package.

This package contains a sample Litestar API application that demonstrates
common REST API patterns. It serves as documentation source material for
testing sphinx-typesense search functionality.

Modules:
    app: Application factory and configuration.
    models: Pydantic models for request/response schemas.
    controllers: Route controllers organized by resource type.

Example:
    Running the application with uvicorn::

        $ uvicorn examples.litestar_app.app:app --reload

    Or using the factory function::

        $ uvicorn examples.litestar_app.app:create_app --factory

The API provides the following endpoints:

Health Checks:
    - GET /health - Overall health status
    - GET /health/ready - Readiness probe
    - GET /health/live - Liveness probe

Users:
    - GET /users - List users with pagination
    - GET /users/{id} - Get user by ID
    - POST /users - Create new user
    - PATCH /users/{id} - Update user
    - DELETE /users/{id} - Delete user

Items:
    - GET /items - List items with filtering
    - GET /items/{id} - Get item by ID
    - POST /items - Create new item
    - PATCH /items/{id} - Update item
    - DELETE /items/{id} - Delete item
    - POST /items/{id}/reserve - Reserve item quantity
"""

from __future__ import annotations

__version__ = "1.0.0"
__author__ = "Example Author"

from .app import app, create_app
from .models import (
    ErrorResponse,
    HealthResponse,
    ItemCreate,
    ItemResponse,
    ItemStatus,
    ItemUpdate,
    PaginatedResponse,
    UserCreate,
    UserResponse,
    UserRole,
    UserUpdate,
)

__all__ = [
    "app",
    "create_app",
    "ErrorResponse",
    "HealthResponse",
    "ItemCreate",
    "ItemResponse",
    "ItemStatus",
    "ItemUpdate",
    "PaginatedResponse",
    "UserCreate",
    "UserResponse",
    "UserRole",
    "UserUpdate",
]
