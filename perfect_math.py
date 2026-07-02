import math

def calculate_area(length: float, width: float) -> float:
    """
    Calculates the area of a rectangle.
    
    Args:
        length (float): The length of the rectangle.
        width (float): The width of the rectangle.
        
    Returns:
        float: The calculated area.
        
    Raises:
        ValueError: If length or width is negative, NaN (Not a Number), or Infinity.
    """
    if any(math.isnan(x) or math.isinf(x) for x in (length, width)):
        raise ValueError("Length and width cannot be NaN or infinity.")
        
    if length < 0 or width < 0:
        raise ValueError("Length and width must be non-negative.")
    
    return length * width
