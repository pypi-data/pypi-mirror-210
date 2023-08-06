def lcm(a, b):
    """
    Calculate the least common multiple (LCM) of two numbers.

    Args:
        a (int): First number.
        b (int): Second number.

    Returns:
        int: The LCM of the two numbers.
    """
    # Find the greater number
    greater = max(a, b)

    # Initialize the LCM as the greater number
    lcm = greater

    while True:
        if lcm % a == 0 and lcm % b == 0:
            # If the LCM is divisible by both numbers, it is found
            break
        lcm += greater

    return lcm

def hcf(a, b):
    """
    Calculate the highest common factor (HCF) or greatest common divisor (GCD) of two numbers.

    Args:
        a (int): First number.
        b (int): Second number.

    Returns:
        int: The HCF or GCD of the two numbers.
    """
    while b != 0:
        a, b = b, a % b

    return a
