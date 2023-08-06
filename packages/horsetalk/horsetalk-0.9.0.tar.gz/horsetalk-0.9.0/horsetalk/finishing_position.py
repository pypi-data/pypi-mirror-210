from enum import Enum


class FinishingPosition(Enum):
    """
    An enumeration that represents the finishing position of a horse in a race.

    """

    UNPLACED = 0
    FIRST = 1
    SECOND = 2
    THIRD = 3
    FOURTH = 4
    FIFTH = 5
    SIXTH = 6
    SEVENTH = 7
    EIGHTH = 8
    NINTH = 9

    def __str__(self):
        return str(self.value)
