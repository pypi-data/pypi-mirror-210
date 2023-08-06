def dec_to_bin(num):
    """
    Convert a decimal number to binary representation.

    Args:
        num (int): Decimal number.

    Returns:
        str: Binary representation of the decimal number.
    """
    return bin(num)[2:]  # Using built-in bin() function and removing the '0b' prefix


def bin_to_dec(binary):
    """
    Convert a binary number to decimal representation.

    Args:
        binary (str): Binary number.

    Returns:
        int: Decimal representation of the binary number.
    """
    return int(binary, 2)  # Using built-in int() function with base 2


def dec_to_hex(num):
    """
    Convert a decimal number to hexadecimal representation.

    Args:
        num (int): Decimal number.

    Returns:
        str: Hexadecimal representation of the decimal number.
    """
    return hex(num)[2:]  # Using built-in hex() function and removing the '0x' prefix


def hex_to_dec(hexadecimal):
    """
    Convert a hexadecimal number to decimal representation.

    Args:
        hexadecimal (str): Hexadecimal number.

    Returns:
        int: Decimal representation of the hexadecimal number.
    """
    return int(hexadecimal, 16)  # Using built-in int() function with base 16


def dec_to_oct(num):
    """
    Convert a decimal number to octal representation.

    Args:
        num (int): Decimal number.

    Returns:
        str: Octal representation of the decimal number.
    """
    return oct(num)[2:]  # Using built-in oct() function and removing the '0o' prefix


def oct_to_dec(octal):
    """
    Convert an octal number to decimal representation.

    Args:
        octal (str): Octal number.

    Returns:
        int: Decimal representation of the octal number.
    """
    return int(octal, 8)  # Using built-in int() function with base 8
