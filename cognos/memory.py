"""
Memory — persistent context store for Cognos Cloud agents.

Memory is enabled automatically when you set memory=True on an Agent.
This module provides the low-level client if you need direct access.

Usage (automatic — recommended):
    agent = Agent(name="my-agent", memory=True)

Usage (manual):
    from cognos.memory import Memory

    mem = Memory(agent_name="my-agent")
    mem.write("user-123", "Prefers dark mode and Python")
    results = mem.search("user preferences", top_k=5)
"""

from __future__ import annotations

from typing import Any
from .client import CognosClient


class Memory:
    """
    Low-level client for the Cognos Cloud Memory store.

    Status: Coming Soon — basic read/write is available now.
    Vector search and per-user namespaces are in development.
    """

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self._client    = CognosClient()

    def write(self, key: str, value: str, namespace: str = "default") -> None:
        """
        Write a key-value item to the memory store.

        Args:
            key:       Unique identifier for this memory item.
            value:     The content to store (plain text or JSON string).
            namespace: Scope for this item. Use user IDs to isolate per-user
                       memory. Defaults to "default".
        """
        self._client.post(f"/agents/{self.agent_name}/memory", {
            "key":       key,
            "value":     value,
            "namespace": namespace,
        })

    def read(self, key: str, namespace: str = "default") -> str | None:
        """
        Read a specific item from the memory store by key.

        Args:
            key:       The key to retrieve.
            namespace: The namespace to search in. Defaults to "default".

        Returns:
            The stored value string, or None if not found.
        """
        result = self._client.get(
            f"/agents/{self.agent_name}/memory/{key}",
            params={"namespace": namespace},
        )
        return result.get("value")

    def search(self, query: str, top_k: int = 5, namespace: str = "default") -> list[dict]:
        """
        Semantic search over stored memory items. (Coming Soon)

        Args:
            query:     Natural language query to search for.
            top_k:     Number of results to return. Defaults to 5.
            namespace: The namespace to search in. Defaults to "default".

        Returns:
            List of matching items sorted by relevance, each with
            {"key": str, "value": str, "score": float}.
        """
        return self._client.post(f"/agents/{self.agent_name}/memory/search", {
            "query":     query,
            "top_k":     top_k,
            "namespace": namespace,
        })

    def delete(self, key: str, namespace: str = "default") -> None:
        """Delete a specific memory item."""
        self._client.delete(
            f"/agents/{self.agent_name}/memory/{key}",
            params={"namespace": namespace},
        )

    def clear(self, namespace: str = "default") -> None:
        """Clear all memory items in a namespace."""
        self._client.delete(
            f"/agents/{self.agent_name}/memory",
            params={"namespace": namespace},
        )

    def list(self, namespace: str = "default") -> list[dict[str, Any]]:
        """List all items in a namespace."""
        return self._client.get(
            f"/agents/{self.agent_name}/memory",
            params={"namespace": namespace},
        )
