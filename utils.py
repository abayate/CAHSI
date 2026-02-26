import os

from bitstring import BitArray


def checkPath(path):
    """
    Checks if a directory path exists and creates it if it does not.
    Args:
        path (str): The path to the directory to check and create.
    """

    if not os.path.exists(path):
        os.makedirs(path)


def BinaryBeauty(word: BitArray) -> str:
    """
    Formats an integer as a binary string with spaces every 4 bits for readability.

    This function converts the given integer to a zero-padded binary string of the specified length,
    then inserts a space after every 4 bits to improve human readability (e.g., for visualizing cipher states).

    Args:
        word (int): The integer to format as a binary string.
        length (int): The total length (number of bits) for the output string.

    Returns:
        str: The formatted binary string with spaces every 4 bits.
    """
    binary_string = word.bin

    nibbles = [binary_string[i:i+4] for i in range(0, len(binary_string), 4)]

    return ' '.join(nibbles)


def TextToBinary(text: str) -> str:
    """
    Converts a string to its binary representation.

    This function encodes each character in the input string to its binary equivalent,
    concatenating them into a single binary string.

    Args:
        text (str): The input string to convert to binary.

    Returns:
        str: The binary representation of the input string.
    """
    return ''.join(format(ord(char), '08b') for char in text)


def splitBinaryGroupsInt(number: int, length: int, groupSize: int) -> list[int]:
    """
    Splits a binary number into groups of n bits (without converting to string).

    Args:
        number (int): The integer to split.
        length (int): The total length (number of bits).
        group_size (int): The size of each group in bits.

    Returns:
        list[int]: A list of integers, each representing a group of n bits.

    Example:
        >>> split_binary_groups_int(0b1010110010101100, 16, 4)
        [0b1010, 0b1100, 0b1010, 0b1100]
    """
    groups = []
    for i in reversed(range(0, length, groupSize)):
        group = (number >> i) & ((1 << groupSize) - 1)
        groups.append(group)
    return groups
