"""
Decorator-based registration system for tools, resources, and prompts.
"""

from typing import Any, Callable, Optional, List


class ToolRegistry:
    """Registry for tools, resources, and prompts."""

    def __init__(self):
        self.tools: dict[str, dict[str, Any]] = {}
        self.resources: dict[str, dict[str, Any]] = {}
        self.prompts: dict[str, dict[str, Any]] = {}

    def register_tool(
        self,
        func: Callable,
        name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Callable:
        """
        Register a function as a tool.

        Args:
            func: The function to register
            name: Optional name (defaults to function name)
            description: Optional description (defaults to docstring)
            tags: Optional list of tags for categorization

        Returns:
            The original function unchanged
        """
        tool_name = name or func.__name__
        tool_description = description or (func.__doc__ or "").strip()

        self.tools[tool_name] = {
            "func": func,
            "name": tool_name,
            "description": tool_description,
            "tags": tags or [],
        }

        return func

    def register_resource(
        self,
        func: Callable,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Callable:
        """
        Register a function as a resource.

        Args:
            func: The function to register
            name: Optional name (defaults to function name)
            description: Optional description (defaults to docstring)

        Returns:
            The original function unchanged
        """
        resource_name = name or func.__name__
        resource_description = description or (func.__doc__ or "").strip()

        self.resources[resource_name] = {
            "func": func,
            "name": resource_name,
            "description": resource_description,
        }

        return func

    def register_prompt(
        self,
        func: Callable,
        name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Callable:
        """
        Register a function as a prompt template.

        Args:
            func: The function to register
            name: Optional name (defaults to function name)
            description: Optional description (defaults to docstring)
            tags: Optional list of tags

        Returns:
            The original function unchanged
        """
        prompt_name = name or func.__name__
        prompt_description = description or (func.__doc__ or "").strip()

        self.prompts[prompt_name] = {
            "func": func,
            "name": prompt_name,
            "description": prompt_description,
            "tags": tags or [],
        }

        return func

    def tool(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Callable:
        """
        Decorator to register a function as a tool.

        Usage:
            @registry.tool(name="custom_name")
            def my_function(x: int) -> int:
                return x * 2
        """
        def decorator(func: Callable) -> Callable:
            return self.register_tool(func, name=name, description=description, tags=tags)
        return decorator

    def resource(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Callable:
        """
        Decorator to register a function as a resource.

        Usage:
            @registry.resource()
            def get_status() -> dict:
                return {"status": "ok"}
        """
        def decorator(func: Callable) -> Callable:
            return self.register_resource(func, name=name, description=description)
        return decorator

    def prompt(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Callable:
        """
        Decorator to register a function as a prompt template.

        Usage:
            @registry.prompt(tags=["analysis"])
            def analyze_code(code: str) -> str:
                return f"Analyze this code: {code}"
        """
        def decorator(func: Callable) -> Callable:
            return self.register_prompt(func, name=name, description=description, tags=tags)
        return decorator
