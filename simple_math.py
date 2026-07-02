def add_two_integers(first_number: int, second_number: int) -> int:
    """
    Returns the exact mathematical sum of two integers.
    
    Args:
        first_number (int): The first integer to add.
        second_number (int): The second integer to add.
        
    Returns:
        int: The sum of the two integers.
    """
    if not isinstance(first_number, int) or type(first_number) is bool:
        raise TypeError("first_number must be an integer, not a boolean.")
    if not isinstance(second_number, int) or type(second_number) is bool:
        raise TypeError("second_number must be an integer, not a boolean.")
        
    return first_number + second_number
