"""
Schema generation utilities for converting Python type hints to JSON Schema.
"""

import json
from typing import Any, Dict, List, Optional, Union, get_args, get_origin
from inspect import signature, Parameter


def python_type_to_json_schema(py_type: Any) -> Dict[str, Any]:
    """
    Convert a Python type hint to JSON Schema.

    Args:
        py_type: A Python type annotation

    Returns:
        A dictionary representing the JSON Schema for that type
    """
    # Handle None type
    if py_type is type(None):
        return {"type": "null"}

    # Handle basic types
    if py_type is int:
        return {"type": "integer"}
    if py_type is float:
        return {"type": "number"}
    if py_type is str:
        return {"type": "string"}
    if py_type is bool:
        return {"type": "boolean"}

    # Handle Optional types
    origin = get_origin(py_type)
    args = get_args(py_type)

    if origin is Union:
        # Check if it's Optional (Union with None)
        if type(None) in args:
            # Optional type - get the non-None type
            non_none_types = [t for t in args if t is not type(None)]
            if len(non_none_types) == 1:
                schema = python_type_to_json_schema(non_none_types[0])
                # Make it nullable
                if isinstance(schema, dict):
                    schema = {
                        "anyOf": [
                            schema,
                            {"type": "null"}
                        ]
                    }
                return schema
            else:
                # Union of multiple types
                schemas = [python_type_to_json_schema(t) for t in non_none_types]
                return {"anyOf": schemas}
        else:
            # Regular Union
            schemas = [python_type_to_json_schema(t) for t in args]
            return {"anyOf": schemas}

    # Handle List types
    if origin is list:
        if args:
            item_schema = python_type_to_json_schema(args[0])
            return {
                "type": "array",
                "items": item_schema
            }
        return {"type": "array"}

    # Handle Dict types
    if origin is dict:
        if args and len(args) >= 2:
            value_schema = python_type_to_json_schema(args[1])
            return {
                "type": "object",
                "additionalProperties": value_schema
            }
        return {"type": "object"}

    # Default to string for unknown types
    return {"type": "string"}


def generate_tool_schema(
    func,
    name: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a complete MCP tool schema from a Python function.

    Args:
        func: The Python function to generate schema for
        name: Optional override for the tool name (defaults to function name)
        description: Optional override for the description (defaults to docstring)

    Returns:
        A dictionary containing the tool schema
    """
    sig = signature(func)
    tool_name = name or func.__name__
    tool_description = description or (func.__doc__ or "").strip()

    # Extract parameters
    properties = {}
    required = []

    for param_name, param in sig.parameters.items():
        if param_name in ("self", "cls"):
            continue

        param_schema = python_type_to_json_schema(param.annotation)
        properties[param_name] = param_schema

        # Check if parameter is required (no default value)
        if param.default is Parameter.empty:
            required.append(param_name)

    # Build the input schema
    input_schema = {
        "type": "object",
        "properties": properties,
    }

    if required:
        input_schema["required"] = required

    # Get return type schema
    return_schema = python_type_to_json_schema(sig.return_annotation)

    # Build complete tool schema
    return {
        "name": tool_name,
        "description": tool_description,
        "inputSchema": input_schema,
        "outputSchema": return_schema,
    }


def validate_parameters(params: Dict[str, Any], schema: Dict[str, Any]) -> None:
    """
    Validate parameters against a schema.

    Args:
        params: The parameters to validate
        schema: The input schema to validate against

    Raises:
        ValueError: If validation fails
    """
    properties = schema.get("properties", {})
    required = schema.get("required", [])

    # Check required parameters
    for param_name in required:
        if param_name not in params:
            raise ValueError(f"Missing required parameter: {param_name}")

    # Basic type checking
    for param_name, param_value in params.items():
        if param_name not in properties:
            raise ValueError(f"Unknown parameter: {param_name}")

        param_schema = properties[param_name]
        expected_type = param_schema.get("type")

        if expected_type == "integer" and not isinstance(param_value, int):
            raise ValueError(f"Parameter {param_name} must be an integer")
        elif expected_type == "number" and not isinstance(param_value, (int, float)):
            raise ValueError(f"Parameter {param_name} must be a number")
        elif expected_type == "string" and not isinstance(param_value, str):
            raise ValueError(f"Parameter {param_name} must be a string")
        elif expected_type == "boolean" and not isinstance(param_value, bool):
            raise ValueError(f"Parameter {param_name} must be a boolean")
        elif expected_type == "array" and not isinstance(param_value, list):
            raise ValueError(f"Parameter {param_name} must be an array")
        elif expected_type == "object" and not isinstance(param_value, dict):
            raise ValueError(f"Parameter {param_name} must be an object")


def extract_docstring_parts(docstring: str) -> Dict[str, str]:
    """
    Extract summary and details from a docstring.

    Args:
        docstring: The docstring to parse

    Returns:
        A dictionary with 'summary' and 'details' keys
    """
    if not docstring:
        return {"summary": "", "details": ""}

    lines = docstring.strip().split("\n")
    summary = lines[0].strip()
    details = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""

    return {
        "summary": summary,
        "details": details
    }
