"""Domain exceptions for the QSO Logging bounded context."""


class FrequencyFormatError(ValueError):
    """Raised when a FREQ string cannot be parsed as a decimal MHz value."""


class FrequencyOutOfBandError(ValueError):
    """Raised when a Frequency does not fall within any known amateur band."""
