class ValidationError(Exception):
    """Raised when user input fails a domain validation rule."""


class NotFoundError(Exception):
    """Raised when a requested record does not exist."""
