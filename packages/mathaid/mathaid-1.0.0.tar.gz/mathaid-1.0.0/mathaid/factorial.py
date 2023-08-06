def factorial(n):
    """
    Calculate the factorial of a non-negative integer.
    
    Args:
        n (int): The non-negative integer.
    
    Returns:
        int: The factorial of `n`.
        
    Raises:
        ValueError: If `n` is a negative number.
    """
    if n < 0:
        raise ValueError("Factorial is undefined for negative numbers.")
    
    result = 1
    for i in range(1, n+1):
        result *= i
    
    return result
