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
    
    return length * width
