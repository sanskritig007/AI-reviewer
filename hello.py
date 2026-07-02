"""
This is a simple module to demonstrate the AI code reviewer functionality.
It contains basic string manipulation without complex logic.
"""


def say_hello(name: str) -> str:
    """Returns a greeting for the given name."""
    if not name:
        return "Hello, World!"
    return f"Hello, {name}!"
