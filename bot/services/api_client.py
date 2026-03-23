"""LMS API client.

Handles HTTP requests to the Learning Management Service backend.
Uses Bearer token authentication.
"""

import httpx
from typing import Any


class LMSAPIClient:
    """Client for the LMS backend API.

    All requests include Bearer token authentication.
    """

    def __init__(self, base_url: str, api_key: str):
        """Initialize the API client.

        Args:
            base_url: Base URL of the LMS API (e.g., http://localhost:42002).
            api_key: API key for authentication.
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=10.0,
        )

    def get_items(self) -> list[dict[str, Any]]:
        """Get all items from the LMS.

        Returns:
            List of item records (labs, tasks, etc.).

        Raises:
            httpx.HTTPError: If the request fails.
        """
        response = self._client.get("/items/")
        response.raise_for_status()
        return response.json()

    def get_labs(self) -> list[dict[str, Any]]:
        """Get all labs from the LMS.

        Returns:
            List of lab records (items with type='lab').

        Raises:
            httpx.HTTPError: If the request fails.
        """
        items = self.get_items()
        return [item for item in items if item.get("type") == "lab"]

    def get_tasks_for_lab(self, lab_id: int) -> list[dict[str, Any]]:
        """Get all tasks for a specific lab.

        Args:
            lab_id: The ID of the lab.

        Returns:
            List of task records with the given parent_id.

        Raises:
            httpx.HTTPError: If the request fails.
        """
        items = self.get_items()
        return [
            item
            for item in items
            if item.get("type") == "task" and item.get("parent_id") == lab_id
        ]

    def get_learner(self, learner_id: int) -> dict[str, Any] | None:
        """Get a learner by ID.

        Args:
            learner_id: The ID of the learner.

        Returns:
            Learner record or None if not found.

        Raises:
            httpx.HTTPError: If the request fails (other than 404).
        """
        try:
            response = self._client.get(f"/learners/{learner_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise

    def is_healthy(self) -> bool:
        """Check if the backend is reachable.

        Returns:
            True if the backend responds to a basic request.
        """
        try:
            response = self._client.get("/items/")
            return response.status_code == 200
        except httpx.HTTPError:
            return False

    def get_item_count(self) -> int:
        """Get the total number of items in the backend.

        Returns:
            Number of items.

        Raises:
            httpx.HTTPError: If the request fails.
        """
        items = self.get_items()
        return len(items)
