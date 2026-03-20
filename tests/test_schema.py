"""
Unit tests for schema generation and validation.
"""

import unittest
from typing import Optional, List, Dict, Union
from mcp_toolbox.schema import (
    python_type_to_json_schema,
    generate_tool_schema,
    validate_parameters,
    extract_docstring_parts,
)


class TestPythonTypeToJsonSchema(unittest.TestCase):
    """Test conversion of Python types to JSON Schema."""

    def test_basic_types(self):
        """Test basic type conversions."""
        # Integer
        schema = python_type_to_json_schema(int)
        self.assertEqual(schema["type"], "integer")

        # Float
        schema = python_type_to_json_schema(float)
        self.assertEqual(schema["type"], "number")

        # String
        schema = python_type_to_json_schema(str)
        self.assertEqual(schema["type"], "string")

        # Boolean
        schema = python_type_to_json_schema(bool)
        self.assertEqual(schema["type"], "boolean")

    def test_optional_types(self):
        """Test Optional type handling."""
        schema = python_type_to_json_schema(Optional[str])
        self.assertIn("anyOf", schema)
        self.assertEqual(len(schema["anyOf"]), 2)

    def test_list_types(self):
        """Test List type handling."""
        schema = python_type_to_json_schema(List[str])
        self.assertEqual(schema["type"], "array")
        self.assertEqual(schema["items"]["type"], "string")

    def test_dict_types(self):
        """Test Dict type handling."""
        schema = python_type_to_json_schema(Dict[str, int])
        self.assertEqual(schema["type"], "object")
        self.assertEqual(schema["additionalProperties"]["type"], "integer")

    def test_none_type(self):
        """Test None type."""
        schema = python_type_to_json_schema(type(None))
        self.assertEqual(schema["type"], "null")


class TestGenerateToolSchema(unittest.TestCase):
    """Test tool schema generation."""

    def test_simple_function(self):
        """Test schema generation for simple function."""
        def add(a: int, b: int) -> int:
            """Add two numbers."""
            return a + b

        schema = generate_tool_schema(add)
        self.assertEqual(schema["name"], "add")
        self.assertEqual(schema["description"], "Add two numbers.")
        self.assertIn("a", schema["inputSchema"]["properties"])
        self.assertIn("b", schema["inputSchema"]["properties"])
        self.assertIn("a", schema["inputSchema"]["required"])
        self.assertIn("b", schema["inputSchema"]["required"])

    def test_function_with_optional_params(self):
        """Test schema generation with optional parameters."""
        def greet(name: str, greeting: Optional[str] = None) -> str:
            """Greet someone."""
            return f"{greeting or 'Hello'}, {name}!"

        schema = generate_tool_schema(greet)
        self.assertIn("name", schema["inputSchema"]["required"])
        self.assertNotIn("greeting", schema["inputSchema"]["required"])

    def test_function_with_defaults(self):
        """Test schema generation with default values."""
        def power(base: float, exponent: float = 2.0) -> float:
            """Raise to a power."""
            return base ** exponent

        schema = generate_tool_schema(power)
        self.assertIn("base", schema["inputSchema"]["required"])
        self.assertNotIn("exponent", schema["inputSchema"]["required"])

    def test_custom_name_and_description(self):
        """Test custom name and description."""
        def my_func(x: int) -> int:
            return x * 2

        schema = generate_tool_schema(
            my_func,
            name="custom_name",
            description="Custom description"
        )
        self.assertEqual(schema["name"], "custom_name")
        self.assertEqual(schema["description"], "Custom description")


class TestValidateParameters(unittest.TestCase):
    """Test parameter validation."""

    def test_valid_parameters(self):
        """Test validation with valid parameters."""
        schema = {
            "type": "object",
            "properties": {
                "x": {"type": "integer"},
                "y": {"type": "integer"}
            },
            "required": ["x", "y"]
        }

        # Should not raise
        validate_parameters({"x": 1, "y": 2}, schema)

    def test_missing_required_parameter(self):
        """Test validation with missing required parameter."""
        schema = {
            "type": "object",
            "properties": {
                "x": {"type": "integer"}
            },
            "required": ["x"]
        }

        with self.assertRaises(ValueError):
            validate_parameters({}, schema)

    def test_unknown_parameter(self):
        """Test validation with unknown parameter."""
        schema = {
            "type": "object",
            "properties": {
                "x": {"type": "integer"}
            },
            "required": ["x"]
        }

        with self.assertRaises(ValueError):
            validate_parameters({"x": 1, "unknown": 2}, schema)

    def test_type_validation(self):
        """Test type validation."""
        schema = {
            "type": "object",
            "properties": {
                "x": {"type": "integer"}
            },
            "required": ["x"]
        }

        # Should raise for wrong type
        with self.assertRaises(ValueError):
            validate_parameters({"x": "not an integer"}, schema)

    def test_optional_parameters(self):
        """Test with optional parameters."""
        schema = {
            "type": "object",
            "properties": {
                "x": {"type": "integer"},
                "y": {"type": "integer"}
            },
            "required": ["x"]
        }

        # y is optional
        validate_parameters({"x": 1}, schema)
        validate_parameters({"x": 1, "y": 2}, schema)


class TestExtractDocstringParts(unittest.TestCase):
    """Test docstring extraction."""

    def test_empty_docstring(self):
        """Test with empty docstring."""
        result = extract_docstring_parts("")
        self.assertEqual(result["summary"], "")
        self.assertEqual(result["details"], "")

    def test_single_line_docstring(self):
        """Test with single-line docstring."""
        result = extract_docstring_parts("This is a summary")
        self.assertEqual(result["summary"], "This is a summary")
        self.assertEqual(result["details"], "")

    def test_multiline_docstring(self):
        """Test with multi-line docstring."""
        docstring = """Summary line
        First detail line
        Second detail line"""
        result = extract_docstring_parts(docstring)
        self.assertEqual(result["summary"], "Summary line")
        self.assertIn("First detail line", result["details"])
        self.assertIn("Second detail line", result["details"])

    def test_docstring_with_whitespace(self):
        """Test docstring with extra whitespace."""
        docstring = """  Summary
           Detail   """
        result = extract_docstring_parts(docstring)
        self.assertEqual(result["summary"], "Summary")
        self.assertIn("Detail", result["details"])


class TestComplexSchemas(unittest.TestCase):
    """Test complex schema generation scenarios."""

    def test_function_with_list_parameter(self):
        """Test function with list parameter."""
        def process_items(items: List[str]) -> str:
            """Process items."""
            return ", ".join(items)

        schema = generate_tool_schema(process_items)
        items_schema = schema["inputSchema"]["properties"]["items"]
        self.assertEqual(items_schema["type"], "array")
        self.assertEqual(items_schema["items"]["type"], "string")

    def test_function_with_dict_parameter(self):
        """Test function with dict parameter."""
        def merge_dicts(data: Dict[str, int]) -> int:
            """Merge dictionaries."""
            return sum(data.values())

        schema = generate_tool_schema(merge_dicts)
        data_schema = schema["inputSchema"]["properties"]["data"]
        self.assertEqual(data_schema["type"], "object")
        self.assertEqual(
            data_schema["additionalProperties"]["type"],
            "integer"
        )

    def test_function_with_union_parameter(self):
        """Test function with union parameter."""
        def process(value: Union[int, str]) -> str:
            """Process a value."""
            return str(value)

        schema = generate_tool_schema(process)
        value_schema = schema["inputSchema"]["properties"]["value"]
        self.assertIn("anyOf", value_schema)


if __name__ == "__main__":
    unittest.main()
