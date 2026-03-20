"""
Core MCP Server implementation with JSON-RPC protocol support.
"""

import json
from typing import Any, Callable, Dict, List, Optional
from .schema import generate_tool_schema, validate_parameters
from .decorators import ToolRegistry
from .transport import StdioTransport, HTTPTransport, Transport


class MCPServer:
    """
    Main MCP Server class that handles tool registration and JSON-RPC requests.
    Implements the Model Context Protocol for tool discovery and execution.
    """

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        version: str = "1.0.0"
    ):
        """
        Initialize an MCP server.

        Args:
            name: The name of the server
            description: Optional description of what the server does
            version: Version string (defaults to "1.0.0")
        """
        self.name = name
        self.description = description or f"MCP Server: {name}"
        self.version = version

        self.registry = ToolRegistry()
        self.transport: Optional[Transport] = None

    def tool(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Callable:
        """
        Decorator to register a function as an MCP tool.

        Usage:
            @server.tool()
            def my_tool(x: int) -> int:
                return x * 2
        """
        return self.registry.tool(name=name, description=description, tags=tags)

    def resource(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Callable:
        """
        Decorator to register a function as a resource.

        Usage:
            @server.resource()
            def get_status() -> dict:
                return {"status": "ok"}
        """
        return self.registry.resource(name=name, description=description)

    def prompt(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Callable:
        """
        Decorator to register a prompt template.

        Usage:
            @server.prompt()
            def create_prompt(topic: str) -> str:
                return f"Write about {topic}"
        """
        return self.registry.prompt(name=name, description=description, tags=tags)

    def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the initialize request."""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {
                    "listChanged": True
                },
                "resources": {
                    "listChanged": True
                },
                "prompts": {
                    "listChanged": True
                }
            },
            "serverInfo": {
                "name": self.name,
                "version": self.version
            }
        }

    def _handle_list_tools(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/list request."""
        tools = []

        for tool_name, tool_info in self.registry.tools.items():
            func = tool_info["func"]
            schema = generate_tool_schema(
                func,
                name=tool_name,
                description=tool_info["description"]
            )
            tools.append(schema)

        return {"tools": tools}

    def _handle_list_resources(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resources/list request."""
        resources = []

        for resource_name, resource_info in self.registry.resources.items():
            resources.append({
                "uri": f"resource://{resource_name}",
                "name": resource_name,
                "description": resource_info["description"],
                "mimeType": "application/json"
            })

        return {"resources": resources}

    def _handle_list_prompts(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle prompts/list request."""
        prompts = []

        for prompt_name, prompt_info in self.registry.prompts.items():
            prompts.append({
                "name": prompt_name,
                "description": prompt_info["description"],
                "arguments": []
            })

        return {"prompts": prompts}

    def _handle_call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool/call request."""
        tool_name = params.get("name")
        tool_args = params.get("arguments", {})

        if tool_name not in self.registry.tools:
            raise ValueError(f"Unknown tool: {tool_name}")

        tool_info = self.registry.tools[tool_name]
        func = tool_info["func"]

        # Validate parameters
        schema = generate_tool_schema(func, name=tool_name)
        validate_parameters(tool_args, schema["inputSchema"])

        # Call the function
        try:
            result = func(**tool_args)
            return {
                "content": [
                    {
                        "type": "text",
                        "text": str(result) if not isinstance(result, str) else result
                    }
                ]
            }
        except Exception as e:
            raise RuntimeError(f"Tool execution failed: {str(e)}")

    def _handle_read_resource(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resources/read request."""
        uri = params.get("uri", "")

        # Extract resource name from URI
        if uri.startswith("resource://"):
            resource_name = uri[len("resource://"):]
        else:
            resource_name = uri

        if resource_name not in self.registry.resources:
            raise ValueError(f"Unknown resource: {resource_name}")

        resource_info = self.registry.resources[resource_name]
        func = resource_info["func"]

        try:
            result = func()
            return {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps(result) if not isinstance(result, str) else result
                    }
                ]
            }
        except Exception as e:
            raise RuntimeError(f"Resource read failed: {str(e)}")

    def _handle_get_prompt(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle prompts/get request."""
        prompt_name = params.get("name")
        prompt_args = params.get("arguments", {})

        if prompt_name not in self.registry.prompts:
            raise ValueError(f"Unknown prompt: {prompt_name}")

        prompt_info = self.registry.prompts[prompt_name]
        func = prompt_info["func"]

        try:
            result = func(**prompt_args)
            return {
                "messages": [
                    {
                        "role": "user",
                        "content": {
                            "type": "text",
                            "text": str(result)
                        }
                    }
                ]
            }
        except Exception as e:
            raise RuntimeError(f"Prompt generation failed: {str(e)}")

    def _handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main JSON-RPC message handler. Implements MCP protocol methods.
        """
        jsonrpc = message.get("jsonrpc", "2.0")
        method = message.get("method")
        params = message.get("params", {})
        msg_id = message.get("id")

        try:
            # Route to appropriate handler
            if method == "initialize":
                result = self._handle_initialize(params)
            elif method == "tools/list":
                result = self._handle_list_tools(params)
            elif method == "tools/call":
                result = self._handle_call_tool(params)
            elif method == "resources/list":
                result = self._handle_list_resources(params)
            elif method == "resources/read":
                result = self._handle_read_resource(params)
            elif method == "prompts/list":
                result = self._handle_list_prompts(params)
            elif method == "prompts/get":
                result = self._handle_get_prompt(params)
            else:
                return {
                    "jsonrpc": jsonrpc,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    },
                    "id": msg_id
                }

            # Build success response
            response = {
                "jsonrpc": jsonrpc,
                "result": result,
                "id": msg_id
            }
            return response

        except ValueError as e:
            return {
                "jsonrpc": jsonrpc,
                "error": {
                    "code": -32602,
                    "message": f"Invalid params: {str(e)}"
                },
                "id": msg_id
            }
        except Exception as e:
            return {
                "jsonrpc": jsonrpc,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                },
                "id": msg_id
            }

    def run_stdio(self) -> None:
        """
        Run the server using stdio transport (stdin/stdout).
        This is the standard way to run MCP servers.
        """
        self.transport = StdioTransport()
        self.transport.set_message_handler(self._handle_message)
        self.transport.start()

    def run_http(self, host: str = "127.0.0.1", port: int = 8000) -> None:
        """
        Run the server using HTTP transport.

        Args:
            host: The host to bind to (default: 127.0.0.1)
            port: The port to bind to (default: 8000)
        """
        self.transport = HTTPTransport(host=host, port=port)
        self.transport.set_message_handler(self._handle_message)
        self.transport.start()

        # Keep the server running
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            if self.transport:
                self.transport.stop()
