"""Pydantic models for the Litestar example API.

This module contains all the data models used for request validation
and response serialization in the example API.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    """User role enumeration.

    Defines the available roles for users in the system.

    Attributes:
        ADMIN: Administrator with full access.
        USER: Standard user with limited access.
        GUEST: Guest user with read-only access.

    """

    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class ItemStatus(str, Enum):
    """Item status enumeration.

    Represents the current state of an item in the inventory.

    Attributes:
        AVAILABLE: Item is available for use.
        RESERVED: Item has been reserved.
        SOLD: Item has been sold.
        DISCONTINUED: Item is no longer available.

    """

    AVAILABLE = "available"
    RESERVED = "reserved"
    SOLD = "sold"
    DISCONTINUED = "discontinued"


class UserBase(BaseModel):
    """Base user model with common attributes.

    This model contains the shared attributes between user creation
    and user responses.

    Attributes:
        email: The user's email address.
        username: The user's unique username.
        full_name: The user's full display name.
        role: The user's assigned role.

    """

    email: EmailStr
    username: Annotated[str, Field(min_length=3, max_length=50)]
    full_name: Annotated[str, Field(max_length=100)] | None = None
    role: UserRole = UserRole.USER


class UserCreate(UserBase):
    """Model for creating a new user.

    Extends UserBase with password field required for registration.

    Attributes:
        password: The user's password (min 8 characters).

    """

    password: Annotated[str, Field(min_length=8)]


class UserResponse(UserBase):
    """Model for user API responses.

    Extends UserBase with server-generated fields.

    Attributes:
        id: Unique identifier for the user.
        created_at: Timestamp when the user was created.
        is_active: Whether the user account is active.

    """

    id: int
    created_at: datetime
    is_active: bool = True

    class Config:
        """Pydantic model configuration."""

        from_attributes = True


class UserUpdate(BaseModel):
    """Model for updating user information.

    All fields are optional to allow partial updates.

    Attributes:
        email: New email address.
        full_name: New display name.
        role: New user role.
        is_active: New active status.

    """

    email: EmailStr | None = None
    full_name: Annotated[str, Field(max_length=100)] | None = None
    role: UserRole | None = None
    is_active: bool | None = None


class ItemBase(BaseModel):
    """Base item model with common attributes.

    Represents a product or item in the inventory system.

    Attributes:
        name: The item's display name.
        description: Detailed description of the item.
        price: The item's price in cents.
        quantity: Number of items in stock.
        status: Current availability status.

    """

    name: Annotated[str, Field(min_length=1, max_length=200)]
    description: Annotated[str, Field(max_length=2000)] | None = None
    price: Annotated[int, Field(ge=0, description="Price in cents")]
    quantity: Annotated[int, Field(ge=0)] = 0
    status: ItemStatus = ItemStatus.AVAILABLE


class ItemCreate(ItemBase):
    """Model for creating a new item.

    Uses all fields from ItemBase.
    """


class ItemResponse(ItemBase):
    """Model for item API responses.

    Extends ItemBase with server-generated fields.

    Attributes:
        id: Unique identifier for the item.
        created_at: Timestamp when the item was created.
        updated_at: Timestamp of the last update.

    """

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic model configuration."""

        from_attributes = True


class ItemUpdate(BaseModel):
    """Model for updating item information.

    All fields are optional to allow partial updates.

    Attributes:
        name: New item name.
        description: New item description.
        price: New price in cents.
        quantity: New stock quantity.
        status: New availability status.

    """

    name: Annotated[str, Field(min_length=1, max_length=200)] | None = None
    description: Annotated[str, Field(max_length=2000)] | None = None
    price: Annotated[int, Field(ge=0)] | None = None
    quantity: Annotated[int, Field(ge=0)] | None = None
    status: ItemStatus | None = None


class HealthResponse(BaseModel):
    """Health check response model.

    Returns the current status of the API and its dependencies.

    Attributes:
        status: Overall health status.
        version: API version string.
        timestamp: Current server timestamp.
        database: Database connection status.
        cache: Cache connection status.

    """

    status: str
    version: str
    timestamp: datetime
    database: str = "healthy"
    cache: str = "healthy"


class PaginatedResponse(BaseModel):
    """Generic paginated response wrapper.

    Provides pagination metadata for list endpoints.

    Attributes:
        items: List of items in the current page.
        total: Total number of items across all pages.
        page: Current page number (1-indexed).
        page_size: Number of items per page.
        total_pages: Total number of pages.

    """

    items: list
    total: int
    page: Annotated[int, Field(ge=1)]
    page_size: Annotated[int, Field(ge=1, le=100)]
    total_pages: int


class ErrorResponse(BaseModel):
    """Standard error response model.

    Used for consistent error responses across the API.

    Attributes:
        error: Error type or code.
        message: Human-readable error message.
        details: Additional error details.

    """

    error: str
    message: str
    details: dict | None = None
