# Simple greeting module for testing
def say_hello(name: str) -> str:
    """Returns a greeting for the given name."""
    if not name:
        return "Hello, World!"
    return f"Hello, {name}!"
