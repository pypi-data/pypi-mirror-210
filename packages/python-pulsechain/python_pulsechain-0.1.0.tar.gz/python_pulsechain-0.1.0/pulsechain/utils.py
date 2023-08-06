"""
utils.py

This module provides helper functions.
"""


def add_decimal_sign(string: str, decimal_places: int = 18) -> str:
    """
    Insert a dot into a string at a specific position from the right.

    :param string: The string to insert the dot into.
    :type string: str
    :param decimal_places: The number of decimal places to separate from the right.
    :type decimal_places: int
    :return: The string with the dot inserted.
    :rtype: str
    """
    return string[:-decimal_places] + "." + string[-decimal_places:]
