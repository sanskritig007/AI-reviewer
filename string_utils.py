def capitalize_words(text: str) -> str:
    """
    Capitalizes the first letter of each word in a string.
    
    Args:
        text (str): The input string.
        
    Returns:
        str: The string with capitalized words.
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string.")
    return text.title()
