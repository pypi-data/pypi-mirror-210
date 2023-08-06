from .parsing_enum import ParsingEnum


class HorseExperienceLevel(ParsingEnum):
    """
    An enumeration that represents a horse's experience level.

    """

    MAIDEN = 1
    NOVICE = 2
    BEGINNER = 3

    # Alternatives
    NOVICES = NOVICE
    BEGINNERS = BEGINNER
