from .parsing_enum import ParsingEnum


class Sex(ParsingEnum):
    """
    An enumeration representing the sex of a horse.

    """

    MALE = 1
    FEMALE = 2

    # Abbreviations
    M = MALE
    XY = MALE
    F = FEMALE
    XX = FEMALE
