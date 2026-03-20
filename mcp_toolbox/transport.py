"""
Transport layer for MCP communication - supports stdio and HTTP.
"""

import json
import sys
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading


class Transport(ABC):
    """Abstract base class for MCP transports."""

    @abstractmethod
    def start(self) -> None:
        """Start the transport server."""
        pass

    @abstractmethod
    def send_message(self, message: Dict[str, Any]) -> None:
        """Send a message through the transport."""
        pass

    @abstractmethod
    def set_message_handler(self, handler: Callable) -> None:
        """Set the handler for incoming messages."""
        pass


class StdioTransport(Transport):
    """
    Transport using standard input/output for JSON-RPC communication.
    Used for stdio-based MCP servers.
    """

    def __init__(self):
        self.message_handler: Optional[Callable] = None
        self.running = False

    def set_message_handler(self, handler: Callable) -> None:
        """Set the handler for incoming messages."""
        self.message_handler = handler

    def start(self) -> None:
        """Start reading from stdin and processing messages."""
        self.running = True
        try:
            while self.running:
                line = sys.stdin.readline()
                if not line:
                    break

                try:
                    message = json.loads(line.strip())
                    if self.message_handler:
                        response = self.message_handler(message)
                        if response:
                            self.send_message(response)
                except json.JSONDecodeError:
                    error_response = {
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32700,
                            "message": "Parse error"
                        },
                        "id": None
                    }
                    self.send_message(error_response)
                except Exception as e:
                    error_response = {
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32603,
                            "message": f"Internal error: {str(e)}"
                        },
                        "id": None
                    }
                    self.send_message(error_response)
        except KeyboardInterrupt:
            self.running = False

    def send_message(self, message: Dict[str, Any]) -> None:
        """Send a message as a JSON line to stdout."""
        json_line = json.dumps(message)
        sys.stdout.write(json_line + "\n")
        sys.stdout.flush()

    def stop(self) -> None:
        """Stop the transport."""
        self.running = False


class HTTPTransport(Transport):
    """
    HTTP-based transport for MCP communication.
    Uses Python's built-in http.server.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 8000):
        self.host = host
        self.port = port
        self.message_handler: Optional[Callable] = None
        self.server: Optional[HTTPServer] = None
        self.thread: Optional[threading.Thread] = None

    def set_message_handler(self, handler: Callable) -> None:
        """Set the handler for incoming messages."""
        self.message_handler = handler

    def start(self) -> None:
        """Start the HTTP server."""
        transport = self

        class MCPRequestHandler(BaseHTTPRequestHandler):
            def do_POST(self):
                """Handle POST requests."""
                if self.path != "/":
                    self.send_response(404)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Not found"}).encode())
                    return

                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length)

                try:
                    message = json.loads(body.decode("utf-8"))
                    if transport.message_handler:
                        response = transport.message_handler(message)
                    else:
                        response = {
                            "jsonrpc": "2.0",
                            "error": {
                                "code": -32603,
                                "message": "Handler not set"
                            },
                            "id": message.get("id")
                        }

                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(response).encode())
                except json.JSONDecodeError:
                    self.send_response(400)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    error = {
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32700,
                            "message": "Parse error"
                        },
                        "id": None
                    }
                    self.wfile.write(json.dumps(error).encode())
                except Exception as e:
                    self.send_response(500)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    error = {
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32603,
                            "message": f"Internal error: {str(e)}"
                        },
                        "id": None
                    }
                    self.wfile.write(json.dumps(error).encode())

            def log_message(self, format, *args):
                """Suppress default logging."""
                pass

        self.server = HTTPServer((self.host, self.port), MCPRequestHandler)

        # Run server in a background thread
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()

        print(f"HTTP server started on http://{self.host}:{self.port}")

    def send_message(self, message: Dict[str, Any]) -> None:
        """HTTP transport doesn't actively send messages (response-based)."""
        pass

    def stop(self) -> None:
        """Stop the HTTP server."""
        if self.server:
            self.server.shutdown()
            if self.thread:
                self.thread.join(timeout=5)
