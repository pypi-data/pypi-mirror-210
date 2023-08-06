class TurandotException(Exception):
    """Exception base class for Turandot exceptions"""
    pass


class TurandotAssetException(TurandotException):
    """Exception thrown on asset expansion"""
    pass


class TurandotConversionException(TurandotException):
    """Exception thrown on errors during conversion"""
    pass


class TurandotConnectionException(TurandotException):
    """Exception thrown if an API connection fails"""
    pass


class TurandotCiteprocException(TurandotException):
    """Exception thrown on errors by citeproc conversion"""
    pass
