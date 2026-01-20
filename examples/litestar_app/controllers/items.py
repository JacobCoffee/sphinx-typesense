"""Item management controller.

Provides CRUD operations for inventory item resources.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, ClassVar

from litestar import Controller, delete, get, patch, post
from litestar.exceptions import NotFoundException
from litestar.params import Parameter

from ..models import (
    ItemCreate,
    ItemResponse,
    ItemStatus,
    ItemUpdate,
    PaginatedResponse,
)

# In-memory storage for demonstration
_items_db: dict[int, dict] = {}
_item_counter = 0


class ItemController(Controller):
    """Controller for inventory item management.

    Provides full CRUD operations for managing items in the
    inventory system.

    Attributes:
        path: Base path for all item endpoints.
        tags: OpenAPI tags for documentation grouping.

    """

    path = "/items"
    tags: ClassVar[list[str]] = ["Items"]

    @get("/")
    async def list_items(
        self,
        page: Annotated[int, Parameter(ge=1, description="Page number")] = 1,
        page_size: Annotated[int, Parameter(ge=1, le=100, description="Items per page")] = 20,
        status: Annotated[ItemStatus | None, Parameter(description="Filter by status")] = None,
        min_price: Annotated[int | None, Parameter(ge=0, description="Minimum price in cents")] = None,
        max_price: Annotated[int | None, Parameter(ge=0, description="Maximum price in cents")] = None,
        in_stock: Annotated[bool | None, Parameter(description="Filter items in stock")] = None,
    ) -> PaginatedResponse:
        """List all items with pagination and filtering.

        Retrieves a paginated list of inventory items with optional
        filtering by status, price range, and stock availability.

        Args:
            page: Page number to retrieve (1-indexed).
            page_size: Number of items per page (max 100).
            status: Optional filter for item status.
            min_price: Optional minimum price filter (in cents).
            max_price: Optional maximum price filter (in cents).
            in_stock: Optional filter for items with quantity > 0.

        Returns:
            PaginatedResponse: Paginated list of items.

        Example:
            >>> response = await client.get("/items?status=available&in_stock=true")
            >>> data = response.json()
            >>> all(item["status"] == "available" for item in data["items"])
            True

        """
        items = list(_items_db.values())

        # Apply filters
        if status is not None:
            items = [i for i in items if i["status"] == status.value]
        if min_price is not None:
            items = [i for i in items if i["price"] >= min_price]
        if max_price is not None:
            items = [i for i in items if i["price"] <= max_price]
        if in_stock is not None:
            if in_stock:
                items = [i for i in items if i["quantity"] > 0]
            else:
                items = [i for i in items if i["quantity"] == 0]

        total = len(items)
        total_pages = (total + page_size - 1) // page_size
        start = (page - 1) * page_size
        end = start + page_size
        response_items = [ItemResponse(**i) for i in items[start:end]]

        return PaginatedResponse(
            items=response_items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    @get("/{item_id:int}")
    async def get_item(self, item_id: int) -> ItemResponse:
        """Get a specific item by ID.

        Retrieves detailed information about a single inventory item.

        Args:
            item_id: Unique identifier of the item.

        Returns:
            ItemResponse: The requested item's information.

        Raises:
            NotFoundException: If the item does not exist.

        Example:
            >>> response = await client.get("/items/1")
            >>> response.json()["name"]
            "Widget Pro"

        """
        if item_id not in _items_db:
            msg = f"Item with ID {item_id} not found"
            raise NotFoundException(msg)
        return ItemResponse(**_items_db[item_id])

    @post("/")
    async def create_item(self, data: ItemCreate) -> ItemResponse:
        """Create a new inventory item.

        Adds a new item to the inventory system.

        Args:
            data: Item creation data including name, price, and quantity.

        Returns:
            ItemResponse: The newly created item's information.

        Example:
            >>> payload = {
            ...     "name": "Widget Pro",
            ...     "description": "Professional-grade widget",
            ...     "price": 2999,
            ...     "quantity": 100
            ... }
            >>> response = await client.post("/items", json=payload)
            >>> response.status_code
            201

        """
        global _item_counter
        _item_counter += 1
        now = datetime.now(timezone.utc)

        item_data = {
            "id": _item_counter,
            "name": data.name,
            "description": data.description,
            "price": data.price,
            "quantity": data.quantity,
            "status": data.status.value,
            "created_at": now,
            "updated_at": now,
        }
        _items_db[_item_counter] = item_data

        return ItemResponse(**item_data)

    @patch("/{item_id:int}")
    async def update_item(self, item_id: int, data: ItemUpdate) -> ItemResponse:
        """Update an existing item.

        Partially updates an item's information. Only provided fields
        will be updated.

        Args:
            item_id: Unique identifier of the item to update.
            data: Fields to update (all optional).

        Returns:
            ItemResponse: The updated item's information.

        Raises:
            NotFoundException: If the item does not exist.

        Example:
            >>> payload = {"price": 3499, "quantity": 50}
            >>> response = await client.patch("/items/1", json=payload)
            >>> response.json()["price"]
            3499

        """
        if item_id not in _items_db:
            msg = f"Item with ID {item_id} not found"
            raise NotFoundException(msg)

        item = _items_db[item_id]
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if value is not None:
                if field == "status":
                    item[field] = value.value
                else:
                    item[field] = value

        item["updated_at"] = datetime.now(timezone.utc)
        return ItemResponse(**item)

    @delete("/{item_id:int}")
    async def delete_item(self, item_id: int) -> None:
        """Delete an inventory item.

        Permanently removes an item from the inventory.

        Args:
            item_id: Unique identifier of the item to delete.

        Raises:
            NotFoundException: If the item does not exist.

        Warning:
            Consider marking items as discontinued instead of
            deleting them to preserve historical data.

        Example:
            >>> response = await client.delete("/items/1")
            >>> response.status_code
            204

        """
        if item_id not in _items_db:
            msg = f"Item with ID {item_id} not found"
            raise NotFoundException(msg)
        del _items_db[item_id]

    @post("/{item_id:int}/reserve")
    async def reserve_item(
        self,
        item_id: int,
        quantity: Annotated[int, Parameter(ge=1, description="Quantity to reserve")] = 1,
    ) -> ItemResponse:
        """Reserve a quantity of an item.

        Marks a specified quantity of the item as reserved for purchase.

        Args:
            item_id: Unique identifier of the item to reserve.
            quantity: Number of items to reserve.

        Returns:
            ItemResponse: The updated item's information.

        Raises:
            NotFoundException: If the item does not exist.
            ValueError: If insufficient quantity is available.

        Note:
            Reserved items are still counted in the total quantity
            but cannot be reserved again.

        Example:
            >>> response = await client.post("/items/1/reserve?quantity=5")
            >>> response.json()["status"]
            "reserved"

        """
        if item_id not in _items_db:
            msg = f"Item with ID {item_id} not found"
            raise NotFoundException(msg)

        item = _items_db[item_id]
        if item["quantity"] < quantity:
            msg = f"Insufficient quantity. Available: {item['quantity']}"
            raise ValueError(msg)

        item["quantity"] -= quantity
        item["status"] = ItemStatus.RESERVED.value if item["quantity"] == 0 else item["status"]
        item["updated_at"] = datetime.now(timezone.utc)

        return ItemResponse(**item)
