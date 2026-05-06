"""Main Tool Registry implementation."""

from __future__ import annotations

import fnmatch
from typing import Any, Callable, Optional

from .tool import Tool, ToolMetadata
from .errors import ToolNotFoundError, ToolValidationError, ToolExecutionError


class ToolRegistry:
    """Lightweight tool registry and discovery system for AI agents."""

    def __init__(self, namespace: Optional[str] = None) -> None:
        """Initialize the registry.

        Args:
            namespace: Optional namespace prefix for all tools
        """
        self._namespace = namespace
        self._tools: dict[str, Tool] = {}

    def _full_name(self, name: str) -> str:
        """Get full tool name with namespace."""
        if self._namespace:
            return f"{self._namespace}.{name}"
        return name

    def tool(
        self,
        name: str,
        description: str,
        tags: Optional[list[str]] = None,
        examples: Optional[list[dict[str, Any]]] = None,
        rate_limit: Optional[int] = None,
        timeout: Optional[int] = None,
        requires_auth: bool = False,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator to register a tool.

        Args:
            name: Tool name (will be prefixed with namespace if set)
            description: Human-readable description
            tags: Optional tags for discovery
            examples: Optional usage examples
            rate_limit: Optional rate limit (calls per minute)
            timeout: Optional timeout (seconds)
            requires_auth: Whether auth is required

        Returns:
            Decorator function
        """
        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            full_name = self._full_name(name)
            metadata = ToolMetadata(
                name=full_name,
                description=description,
                tags=tags or [],
                examples=examples or [],
                rate_limit=rate_limit,
                timeout=timeout,
                requires_auth=requires_auth,
                namespace=self._namespace,
            )
            self._tools[full_name] = Tool(fn, metadata)
            return fn
        return decorator

    def register(
        self,
        fn: Callable[..., Any],
        name: str,
        description: str,
        tags: Optional[list[str]] = None,
        examples: Optional[list[dict[str, Any]]] = None,
        rate_limit: Optional[int] = None,
        timeout: Optional[int] = None,
        requires_auth: bool = False,
    ) -> Tool:
        """Explicitly register a tool.

        Args:
            fn: The function to register
            name: Tool name
            description: Human-readable description
            tags: Optional tags for discovery
            examples: Optional usage examples
            rate_limit: Optional rate limit (calls per minute)
            timeout: Optional timeout (seconds)
            requires_auth: Whether auth is required

        Returns:
            The registered Tool
        """
        full_name = self._full_name(name)
        metadata = ToolMetadata(
            name=full_name,
            description=description,
            tags=tags or [],
            examples=examples or [],
            rate_limit=rate_limit,
            timeout=timeout,
            requires_auth=requires_auth,
            namespace=self._namespace,
        )
        tool = Tool(fn, metadata)
        self._tools[full_name] = tool
        return tool

    def execute(self, name: str, params: dict[str, Any]) -> Any:
        """Execute a tool by name.

        Args:
            name: Tool name
            params: Input parameters

        Returns:
            Tool result

        Raises:
            ToolNotFoundError: If tool not found
            ToolValidationError: If validation fails
            ToolExecutionError: If execution fails
        """
        if name not in self._tools:
            raise ToolNotFoundError(name)

        tool = self._tools[name]

        try:
            validated = tool.validate_input(params)
        except Exception as e:
            raise ToolValidationError(name, [str(e)])

        try:
            return tool.fn(**validated)
        except Exception as e:
            raise ToolExecutionError(name, e)

    def get_tool(self, name: str) -> Tool:
        """Get a tool by name."""
        if name not in self._tools:
            raise ToolNotFoundError(name)
        return self._tools[name]

    def list_tools(self) -> list[Tool]:
        """List all registered tools."""
        return list(self._tools.values())

    def find_tools(self, pattern: str) -> list[Tool]:
        """Find tools by name pattern (glob-style).

        Args:
            pattern: Glob pattern to match tool names

        Returns:
            List of matching tools
        """
        return [
            tool
            for name, tool in self._tools.items()
            if fnmatch.fnmatch(name, pattern)
        ]

    def find_by_tags(self, tags: list[str]) -> list[Tool]:
        """Find tools that have any of the specified tags.

        Args:
            tags: Tags to search for

        Returns:
            List of matching tools
        """
        return [
            tool
            for tool in self._tools.values()
            if any(tag in tool.metadata.tags for tag in tags)
        ]

    def search(self, query: str) -> list[Tool]:
        """Search tools by description keywords.

        Args:
            query: Search query

        Returns:
            List of matching tools
        """
        query_lower = query.lower()
        return [
            tool
            for tool in self._tools.values()
            if query_lower in tool.metadata.description.lower()
        ]

    def get_openai_schema(self, name: str) -> dict[str, Any]:
        """Get OpenAI-compatible schema for a tool."""
        return self.get_tool(name).get_openai_schema()

    def get_all_openai_schemas(self) -> list[dict[str, Any]]:
        """Get OpenAI-compatible schemas for all tools."""
        return [tool.get_openai_schema() for tool in self._tools.values()]

    def namespace(self, name: str) -> ToolRegistry:
        """Create a namespaced sub-registry.

        Args:
            name: Namespace name

        Returns:
            New ToolRegistry with namespace prefix
        """
        full_namespace = self._full_name(name)
        return ToolRegistry(namespace=full_namespace)
