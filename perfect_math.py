import math

def calculate_area(length: float, width: float) -> float:
    """
    Calculates the area of a rectangle.
    
    Args:
        length (float): The length of the rectangle.
        width (float): The width of the rectangle.
        
    Returns:
        float: The calculated area.
    """
    if length < 0 or width < 0:
        raise ValueError("Length and width must be non-negative.")
        
    if math.isnan(length) or math.isnan(width) or math.isinf(length) or math.isinf(width):
        raise ValueError("Length and width cannot be NaN or infinity.")
    
    return length * width
