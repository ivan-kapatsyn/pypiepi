class DuplicationError(Exception):
    """
    Raised when an attempt is made to create a duplicate entry in the database.
    """
    pass

class WrongTokenError(Exception):
    """
    Raised if a non-existent token is used.
    """
    pass

class TutorAvailabilityError(Exception):
    """
    Exception raised when a tutor is not available at a specified schedule.
    """
    pass
