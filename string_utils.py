def capitalize_words(text: str) -> str:
    """
    Converts the string to title case, where the first letter of each word is 
    capitalized and all other letters are lowercased.
    
    Note: Due to the behavior of str.title(), words with apostrophes 
    (like "I'm") will be capitalized after the apostrophe (e.g., "I'M").
    
    Args:
        text (str): The input string.
        
    Returns:
        str: The string converted to title case.
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string.")
    return text.title()
