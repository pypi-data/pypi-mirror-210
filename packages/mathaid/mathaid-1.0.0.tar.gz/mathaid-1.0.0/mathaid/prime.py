import random

def random_prime(start=2, end=100):
    """
    Generate a random prime number within a given range.

    Args:
        start (int, optional): The start of the range (inclusive). Defaults to 2.
        end (int, optional): The end of the range (exclusive). Defaults to 100.

    Returns:
        int: A random prime number within the specified range.

    Raises:
        ValueError: If the start value is greater than or equal to the end value.
    """
    if start >= end:
        raise ValueError("Invalid range: start value should be less than the end value.")

    prime = None

    while True:
        num = random.randint(start, end - 1)
        if is_prime(num):
            prime = num
            break

    return prime

def is_prime(num):
    """
    Check if a number is prime.

    Args:
        num (int): The number to check.

    Returns:
        bool: True if the number is prime, False otherwise.
    """
    if num < 2:
        return False

    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            return False

    return True
