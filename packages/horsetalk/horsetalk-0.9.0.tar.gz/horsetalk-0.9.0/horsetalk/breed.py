from .parsing_enum import ParsingEnum


class Breed(ParsingEnum):
    """
    An enumeration representing a breed of horse.

    """

    THOROUGHBRED = 1
    ARABIAN = 2
    QUARTER_HORSE = 3
    AQPS = 4

    # Abbreviations
    TB = THOROUGHBRED
    QH = QUARTER_HORSE
