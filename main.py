from fastmcp import FastMCP
import random
import json

mcp = FastMCP("Simple Calculator Server")

# Tool: add two numbers
@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers.
    
    Args:
        a (float): First number.
        b (float): Second number.
    
    Returns:
        The sum of a and b
    """
    return a + b

# Tool: generate a random number
@mcp.tool()
def generate_random_number(min_value: int = 1, max_value: int = 100) -> int:
    """Generate a random number between min_value and max_value.
    
    Args:
        min_value (int): Minimum value (default is 1).
        max_value (int): Maximum value (default is 100).
    
    Returns:
        A random integer between min_value and max_value.
    """
    return random.randint(min_value, max_value)

# Resource: Server information
@mcp.resource("info://server")
def server_info() -> str:
    """Get server information"""
    info = {
        "name": "Simple Calculator Server",
        "version": "1.0.0",
        "description": "A simple server with maths tool.",
        "tools": ["add", "generate_random_number"]
    }
    return json.dumps(info, indent=4)

# Start the server as remote HTTP server
if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)