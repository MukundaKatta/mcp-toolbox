#!/usr/bin/env python3
"""
Weather Tool Server Example

This example demonstrates a complete weather service with multiple tools.
Shows how to use decorators, type hints, and docstrings.

Run with: python examples/weather_server.py
"""

from typing import Optional, List
from mcp_toolbox import MCPServer


def create_server() -> MCPServer:
    """Create and configure the weather server."""
    server = MCPServer(
        name="weather-tools",
        description="Weather and forecast tools for checking conditions and alerts",
        version="1.0.0"
    )

    @server.tool()
    def get_weather(city: str) -> str:
        """
        Get the current weather for a city.

        Returns a human-readable weather description.
        """
        # Simulated weather data
        weather_data = {
            "New York": "Partly cloudy, 65F, 60% humidity",
            "San Francisco": "Sunny, 72F, 45% humidity",
            "London": "Rainy, 55F, 85% humidity",
            "Tokyo": "Clear, 68F, 50% humidity",
            "Sydney": "Sunny, 77F, 55% humidity",
        }

        if city not in weather_data:
            return f"Weather data not available for {city}"

        return f"Weather in {city}: {weather_data[city]}"

    @server.tool()
    def get_forecast(city: str, days: int = 3) -> str:
        """
        Get a weather forecast for a city.

        Args:
            city: The city to get forecast for
            days: Number of days to forecast (1-7)

        Returns:
            A multi-day forecast as a string.
        """
        if days < 1 or days > 7:
            return "Error: days must be between 1 and 7"

        forecast = []
        conditions = ["Sunny", "Cloudy", "Rainy", "Partly Cloudy"]

        for day in range(1, days + 1):
            condition = conditions[day % len(conditions)]
            temp = 65 + (day * 2)
            forecast.append(f"Day {day}: {condition}, {temp}F")

        return f"Forecast for {city}:\n" + "\n".join(forecast)

    @server.tool(tags=["alerts", "safety"])
    def get_alerts(city: str, alert_type: Optional[str] = None) -> str:
        """
        Get active weather alerts for a city.

        Args:
            city: The city to check for alerts
            alert_type: Optional filter for specific alert type

        Returns:
            Information about active weather alerts.
        """
        alerts = {
            "New York": ["Winter Storm Warning", "Wind Advisory"],
            "San Francisco": [],
            "London": ["Flood Watch"],
            "Tokyo": ["Tsunami Watch"],
            "Sydney": [],
        }

        if city not in alerts:
            return f"No alert data available for {city}"

        city_alerts = alerts.get(city, [])

        if alert_type:
            city_alerts = [a for a in city_alerts if alert_type.lower() in a.lower()]

        if not city_alerts:
            return f"No active alerts for {city}"

        return f"Active alerts for {city}:\n- " + "\n- ".join(city_alerts)

    @server.tool()
    def get_temperature(city: str) -> float:
        """
        Get just the temperature for a city.

        Returns temperature in Fahrenheit.
        """
        temps = {
            "New York": 65.0,
            "San Francisco": 72.0,
            "London": 55.0,
            "Tokyo": 68.0,
            "Sydney": 77.0,
        }
        return temps.get(city, 70.0)

    @server.resource()
    def get_service_status() -> dict:
        """
        Get the status of the weather service.

        Returns a dictionary with status information.
        """
        return {
            "service": "weather-tools",
            "status": "operational",
            "version": "1.0.0",
            "uptime_hours": 168,
            "requests_processed": 42000,
        }

    @server.prompt(tags=["analysis"])
    def create_weather_analysis_prompt(city: str, metric: str = "temperature") -> str:
        """
        Create a prompt for analyzing weather.

        Args:
            city: The city to analyze weather for
            metric: The metric to focus on (temperature, precipitation, wind)

        Returns:
            A formatted prompt for weather analysis.
        """
        return f"""Analyze the weather for {city}, focusing on {metric}.
        Provide:
        1. Current conditions
        2. Trends over the next week
        3. Notable patterns or anomalies
        4. Recommendations for activities"""

    return server


if __name__ == "__main__":
    print("Starting Weather Tool Server...")
    print("Press Ctrl+C to exit")
    print()

    server = create_server()
    server.run_stdio()
