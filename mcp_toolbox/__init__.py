"""
mcp-toolbox: A lightweight Python toolkit for building MCP-compatible tool servers.

This package makes it easy to expose Python functions as tools that AI agents can discover
and use via the Model Context Protocol (MCP).

Example:
    >>> from mcp_toolbox import MCPServer
    >>> server = MCPServer(name="my-tools")
    >>> @server.tool()
    ... def add(a: int, b: int) -> int:
    ...     return a + b
    >>> server.run_stdio()
"""

from .server import MCPServer
from .schema import (
    python_type_to_json_schema,
    generate_tool_schema,
    validate_parameters,
    extract_docstring_parts,
)
from .decorators import ToolRegistry
from .transport import Transport, StdioTransport, HTTPTransport

__version__ = "1.0.0"
__author__ = "Mukunda Katta"

__all__ = [
    "MCPServer",
    "ToolRegistry",
    "python_type_to_json_schema",
    "generate_tool_schema",
    "validate_parameters",
    "extract_docstring_parts",
    "Transport",
    "StdioTransport",
    "HTTPTransport",
]
