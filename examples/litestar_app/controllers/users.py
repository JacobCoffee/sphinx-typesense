"""User management controller.

Provides CRUD operations for user resources.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, ClassVar

from litestar import Controller, delete, get, patch, post
from litestar.exceptions import NotFoundException
from litestar.params import Parameter

from ..models import (
    PaginatedResponse,
    UserCreate,
    UserResponse,
    UserRole,
    UserUpdate,
)

# In-memory storage for demonstration
_users_db: dict[int, dict] = {}
_user_counter = 0


class UserController(Controller):
    """Controller for user management endpoints.

    Provides full CRUD operations for managing user accounts
    in the system.

    Attributes:
        path: Base path for all user endpoints.
        tags: OpenAPI tags for documentation grouping.

    """

    path = "/users"
    tags: ClassVar[list[str]] = ["Users"]

    @get("/")
    async def list_users(
        self,
        page: Annotated[int, Parameter(ge=1, description="Page number")] = 1,
        page_size: Annotated[int, Parameter(ge=1, le=100, description="Items per page")] = 20,
        role: Annotated[UserRole | None, Parameter(description="Filter by role")] = None,
        is_active: Annotated[bool | None, Parameter(description="Filter by active status")] = None,
    ) -> PaginatedResponse:
        """List all users with pagination and filtering.

        Retrieves a paginated list of users with optional filtering
        by role and active status.

        Args:
            page: Page number to retrieve (1-indexed).
            page_size: Number of items per page (max 100).
            role: Optional filter for user role.
            is_active: Optional filter for active status.

        Returns:
            PaginatedResponse: Paginated list of users.

        Example:
            >>> response = await client.get("/users?page=1&page_size=10")
            >>> data = response.json()
            >>> len(data["items"])
            10

        """
        users = list(_users_db.values())

        # Apply filters
        if role is not None:
            users = [u for u in users if u["role"] == role.value]
        if is_active is not None:
            users = [u for u in users if u["is_active"] == is_active]

        total = len(users)
        total_pages = (total + page_size - 1) // page_size
        start = (page - 1) * page_size
        end = start + page_size
        items = [UserResponse(**u) for u in users[start:end]]

        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    @get("/{user_id:int}")
    async def get_user(self, user_id: int) -> UserResponse:
        """Get a specific user by ID.

        Retrieves detailed information about a single user.

        Args:
            user_id: Unique identifier of the user.

        Returns:
            UserResponse: The requested user's information.

        Raises:
            NotFoundException: If the user does not exist.

        Example:
            >>> response = await client.get("/users/1")
            >>> response.json()["username"]
            "johndoe"

        """
        if user_id not in _users_db:
            msg = f"User with ID {user_id} not found"
            raise NotFoundException(msg)
        return UserResponse(**_users_db[user_id])

    @post("/")
    async def create_user(self, data: UserCreate) -> UserResponse:
        """Create a new user account.

        Registers a new user in the system with the provided information.

        Args:
            data: User creation data including email, username, and password.

        Returns:
            UserResponse: The newly created user's information.

        Note:
            The password is hashed before storage (not shown in response).

        Example:
            >>> payload = {
            ...     "email": "john@example.com",
            ...     "username": "johndoe",
            ...     "password": "securepassword123"
            ... }
            >>> response = await client.post("/users", json=payload)
            >>> response.status_code
            201

        """
        global _user_counter
        _user_counter += 1

        user_data = {
            "id": _user_counter,
            "email": data.email,
            "username": data.username,
            "full_name": data.full_name,
            "role": data.role.value,
            "created_at": datetime.now(timezone.utc),
            "is_active": True,
        }
        _users_db[_user_counter] = user_data

        return UserResponse(**user_data)

    @patch("/{user_id:int}")
    async def update_user(self, user_id: int, data: UserUpdate) -> UserResponse:
        """Update an existing user.

        Partially updates a user's information. Only provided fields
        will be updated.

        Args:
            user_id: Unique identifier of the user to update.
            data: Fields to update (all optional).

        Returns:
            UserResponse: The updated user's information.

        Raises:
            NotFoundException: If the user does not exist.

        Example:
            >>> payload = {"full_name": "John Doe Jr."}
            >>> response = await client.patch("/users/1", json=payload)
            >>> response.json()["full_name"]
            "John Doe Jr."

        """
        if user_id not in _users_db:
            msg = f"User with ID {user_id} not found"
            raise NotFoundException(msg)

        user = _users_db[user_id]
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if value is not None:
                if field == "role":
                    user[field] = value.value
                else:
                    user[field] = value

        return UserResponse(**user)

    @delete("/{user_id:int}")
    async def delete_user(self, user_id: int) -> None:
        """Delete a user account.

        Permanently removes a user from the system.

        Args:
            user_id: Unique identifier of the user to delete.

        Raises:
            NotFoundException: If the user does not exist.

        Warning:
            This action is irreversible. Consider deactivating
            the user instead for audit purposes.

        Example:
            >>> response = await client.delete("/users/1")
            >>> response.status_code
            204

        """
        if user_id not in _users_db:
            msg = f"User with ID {user_id} not found"
            raise NotFoundException(msg)
        del _users_db[user_id]
