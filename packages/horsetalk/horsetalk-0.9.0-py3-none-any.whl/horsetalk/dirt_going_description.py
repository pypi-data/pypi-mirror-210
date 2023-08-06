from .going_description import GoingDescription


class DirtGoingDescription(GoingDescription):
    """
    An enumeration that represents a scale of US dirt going descriptions.
    """

    SEALED = 0
    SLOW = 1
    SLOPPY = 2
    MUDDY = 3
    GOOD = 4
    WET_FAST = 5
    FAST = 6
