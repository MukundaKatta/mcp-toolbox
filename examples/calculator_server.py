#!/usr/bin/env python3
"""
Calculator Tool Server Example

This example demonstrates a complete calculator service with math tools.
Shows type hint to schema conversion and error handling.

Run with: python examples/calculator_server.py
"""

import math
from typing import Optional
from mcp_toolbox import MCPServer


def create_server() -> MCPServer:
    """Create and configure the calculator server."""
    server = MCPServer(
        name="calculator-tools",
        description="Basic math and scientific calculator tools",
        version="1.0.0"
    )

    @server.tool(tags=["basic", "arithmetic"])
    def add(a: float, b: float) -> float:
        """
        Add two numbers.

        Args:
            a: First number
            b: Second number

        Returns:
            The sum of a and b
        """
        return a + b

    @server.tool(tags=["basic", "arithmetic"])
    def subtract(a: float, b: float) -> float:
        """
        Subtract two numbers.

        Args:
            a: First number
            b: Second number (to be subtracted from a)

        Returns:
            The difference (a - b)
        """
        return a - b

    @server.tool(tags=["basic", "arithmetic"])
    def multiply(x: float, y: float) -> float:
        """
        Multiply two numbers.

        Args:
            x: First number
            y: Second number

        Returns:
            The product of x and y
        """
        return x * y

    @server.tool(tags=["basic", "arithmetic"])
    def divide(numerator: float, denominator: float) -> float:
        """
        Divide two numbers.

        Args:
            numerator: The number to be divided
            denominator: The number to divide by

        Returns:
            The quotient (numerator / denominator)

        Raises:
            ValueError: If denominator is zero
        """
        if denominator == 0:
            raise ValueError("Cannot divide by zero")
        return numerator / denominator

    @server.tool(tags=["advanced"])
    def power(base: float, exponent: float) -> float:
        """
        Raise a number to a power.

        Args:
            base: The base number
            exponent: The exponent

        Returns:
            base raised to the power of exponent
        """
        return base ** exponent

    @server.tool(tags=["advanced", "scientific"])
    def sqrt(number: float) -> float:
        """
        Calculate the square root of a number.

        Args:
            number: The number to take the square root of

        Returns:
            The square root of the number

        Raises:
            ValueError: If number is negative
        """
        if number < 0:
            raise ValueError("Cannot take square root of negative number")
        return math.sqrt(number)

    @server.tool(tags=["advanced", "scientific"])
    def logarithm(value: float, base: float = 10.0) -> float:
        """
        Calculate the logarithm of a value.

        Args:
            value: The value to take logarithm of
            base: The base of the logarithm (defaults to 10)

        Returns:
            The logarithm of value with given base
        """
        if value <= 0:
            raise ValueError("Logarithm value must be positive")
        if base <= 0 or base == 1:
            raise ValueError("Logarithm base must be positive and not equal to 1")
        return math.log(value, base)

    @server.tool(tags=["trigonometry", "scientific"])
    def sine(angle_degrees: float) -> float:
        """
        Calculate the sine of an angle.

        Args:
            angle_degrees: The angle in degrees

        Returns:
            The sine of the angle
        """
        angle_radians = math.radians(angle_degrees)
        return math.sin(angle_radians)

    @server.tool(tags=["trigonometry", "scientific"])
    def cosine(angle_degrees: float) -> float:
        """
        Calculate the cosine of an angle.

        Args:
            angle_degrees: The angle in degrees

        Returns:
            The cosine of the angle
        """
        angle_radians = math.radians(angle_degrees)
        return math.cos(angle_radians)

    @server.tool()
    def factorial(n: int) -> int:
        """
        Calculate the factorial of a number.

        Args:
            n: The number to calculate factorial for

        Returns:
            The factorial of n (n!)

        Raises:
            ValueError: If n is negative
        """
        if n < 0:
            raise ValueError("Factorial is not defined for negative numbers")
        if n == 0 or n == 1:
            return 1
        return math.factorial(n)

    @server.tool()
    def percentage(value: float, total: float) -> float:
        """
        Calculate what percentage value is of total.

        Args:
            value: The partial value
            total: The total value

        Returns:
            The percentage (0-100)

        Raises:
            ValueError: If total is zero
        """
        if total == 0:
            raise ValueError("Total cannot be zero")
        return (value / total) * 100

    @server.resource()
    def get_calculator_info() -> dict:
        """
        Get information about the calculator service.

        Returns:
            A dictionary with calculator information
        """
        return {
            "service": "calculator-tools",
            "version": "1.0.0",
            "capabilities": [
                "basic arithmetic",
                "advanced math",
                "trigonometry",
                "logarithms",
                "factorials"
            ],
            "error_handling": "enabled",
            "precision": "IEEE 754 double precision"
        }

    @server.prompt(tags=["math", "education"])
    def create_math_lesson_prompt(topic: str) -> str:
        """
        Create a prompt for a math lesson.

        Args:
            topic: The math topic to create a lesson for

        Returns:
            A formatted prompt for math instruction
        """
        return f"""Create a lesson plan for teaching {topic}.
        Include:
        1. Key concepts and definitions
        2. Step-by-step explanation
        3. Real-world applications
        4. Practice problems with solutions
        5. Common mistakes to avoid"""

    return server


if __name__ == "__main__":
    print("Starting Calculator Tool Server...")
    print("Press Ctrl+C to exit")
    print()

    server = create_server()
    server.run_stdio()
