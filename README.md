# mcp-toolbox

Expose your Python functions to AI agents with Model Context Protocol (MCP).

## What is mcp-toolbox?

mcp-toolbox is a lightweight Python toolkit for building MCP-compatible tool servers. It makes it effortless to expose Python functions as tools that AI agents (like Claude) can discover and use. With automatic JSON schema generation from type hints and built-in transport support, you can go from Python function to production-ready MCP server in minutes.

## Features

- **Simple Decorator-Based Registration** - Use @tool, @resource, and @prompt decorators to expose Python functions
- **Automatic Schema Generation** - JSON schemas are generated automatically from Python type hints
- **Multiple Transports** - Built-in support for stdio and HTTP transports
- **Full MCP Compliance** - Implements the Model Context Protocol specification
- **Type Safety** - Type hints are validated at runtime against generated schemas
- **Minimal Dependencies** - Uses only Python standard library (no heavy dependencies)
- **Docstring Integration** - Function docstrings become tool descriptions automatically
- **Error Handling** - Proper error propagation with helpful messages

## Installation

```bash
pip install mcp-toolbox
```

Or install from source:

```bash
git clone https://github.com/yourusername/mcp-toolbox.git
cd mcp-toolbox
pip install -e .
```

## Quick Start

Create a simple weather tool server in 5 minutes:

```python
from mcp_toolbox import MCPServer

server = MCPServer(name="weather-tools")

@server.tool()
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    # Your implementation here
    return f"Weather in {city}: Sunny, 72F"

if __name__ == "__main__":
    server.run_stdio()
```

## Usage Examples

### Basic Tool Registration

```python
from mcp_toolbox import MCPServer

server = MCPServer(name="math-tools")

@server.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

@server.tool()
def multiply(x: float, y: float) -> float:
    """Multiply two numbers."""
    return x * y

server.run_stdio()
```

### Advanced Features

```python
from mcp_toolbox import MCPServer
from typing import Optional, List

server = MCPServer(
    name="data-tools",
    description="Tools for working with data"
)

@server.tool(
    name="custom_name",
    description="Custom description",
    tags=["data", "processing"]
)
def process_items(
    items: List[str],
    filter_keyword: Optional[str] = None
) -> List[str]:
    """Process a list of items with optional filtering."""
    if filter_keyword:
        return [item for item in items if filter_keyword in item]
    return items

@server.resource()
def get_database_status() -> dict:
    """Get current database connection status."""
    return {"status": "connected", "queries": 42}

server.run_stdio()
```

### HTTP Transport

```python
from mcp_toolbox import MCPServer

server = MCPServer(name="api-tools")

@server.tool()
def health_check() -> str:
    """Server health check."""
    return "OK"

# Run on HTTP instead of stdio
server.run_http(host="127.0.0.1", port=8000)
```

## How It Works

1. **Register Functions** - Use decorators to mark Python functions as tools
2. **Generate Schemas** - Type hints are automatically converted to JSON Schema
3. **Start Server** - Run the server with stdio or HTTP transport
4. **AI Agents Connect** - Agents discover your tools via MCP and call them

## API Reference

### MCPServer

```python
server = MCPServer(
    name: str,                          # Server name
    description: Optional[str] = None,  # Server description
    version: str = "1.0.0"             # Server version
)
```

Methods:
- `@tool()` - Register a function as an MCP tool
- `@resource()` - Register a function as a resource
- `@prompt()` - Register a prompt template
- `run_stdio()` - Run with stdio transport
- `run_http(host, port)` - Run with HTTP transport

## Architecture

- **server.py** - Core MCPServer class and message handling
- **schema.py** - Type hint to JSON Schema conversion
- **decorators.py** - Decorator-based registration system
- **transport.py** - Stdio and HTTP transport implementations

## Contributing

We welcome contributions! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Examples

See the `examples/` directory for complete working examples:
- `weather_server.py` - Weather tool server
- `calculator_server.py` - Math calculator server
