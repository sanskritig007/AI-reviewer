import sqlite3

# EDGE CASE 1: Hardcoded Secrets (Security Vulnerability)
# The AI should immediately flag this as a critical security risk.
SECRET_API_KEY = "sk-live-1234567890abcdef1234567890abcdef"
AWS_SECRET_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"

def get_user_data(username):
    # EDGE CASE 2: SQL Injection (Security Vulnerability)
    # The AI should warn about string formatting in SQL queries and suggest parameterized queries.
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    return cursor.fetchall()

def calculate_average(numbers):
    # EDGE CASE 3: Logic Bug (Division by zero risk & Off-by-one error)
    # The AI should catch that passing an empty list will cause a ZeroDivisionError.
    total = 0
    for i in range(len(numbers) + 1):  # Off-by-one error: will cause IndexError
        total += numbers[i]
    
    avg = total / len(numbers)
    return avg

def poorly_written_function():
    # EDGE CASE 4: Unused variables and bad naming conventions (Best Practices)
    # The AI should suggest removing unused variables and using descriptive names.
    x1 = 10
    y2 = 20
    z3 = 30 # Unused variable
    
    return x1 + y2

def perfect_function(a: int, b: int) -> int:
    """
    EDGE CASE 5: Clean Code
    The AI should find NO issues here and praise the clean implementation.
    """
    return a + b
