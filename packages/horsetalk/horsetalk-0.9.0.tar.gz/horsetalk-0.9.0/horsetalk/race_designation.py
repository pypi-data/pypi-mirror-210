from .parsing_enum import ParsingEnum


class RaceDesignation(ParsingEnum):
    """
    An enumeration representing the designation or type of race.

    """

    HANDICAP = 1
    CONDITIONS = 2
    AUCTION = 3
    CLAIMER = 4
    SELLER = 5

    # Abbreviations
    HCAP = HANDICAP
    AU = AUCTION
    CL = CLAIMER
    S = SELLER

    # Alternatives
    CLAIMING = CLAIMER
    SELLING = SELLER
