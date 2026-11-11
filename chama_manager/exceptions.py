"""Custom exceptions for the chama manager.

Every error inherits from ChamaError, so callers can catch all domain errors with a single `except ChamaError`.
"""

class ChamaError(Exception):
    """Base class for all chama-related errors."""

class InvalidAmountError(ChamaError):
    """Raised when a money amount is badly types, zero, or negative."""

class InvalidMemberError(ChamaError):
    """Raised when member details (name, phone) fail validation."""

class InvalidRulesError(ChamaError):
    """Raised when the chama's rules contain impossible values."""

class DuplicateMemberError(ChamaError):
    """Raised when a member with the same phone number already exists."""

class MemberNotFoundError(ChamaError):
    """Raised when an operation refers to an uknown member id."""

class LoanNotFoundError(ChamaError):
    """Raised when an operation refers to an unknown load id."""

class InvalidTermError(ChamaError):
    """Raised when a loan term is outside the chama's allowed range."""

class LoanNotAllowedError(ChamaError):
    """Base class for the reasons a loan request can be refused."""

class ActiveLoanExistsError(LoanNotAllowedError):
    """Raised when a member asks for a loan while another is unpaid."""

class LoanLimitExceededError(LoanNotAllowedError):
    """Raised when a loan is larger than the member's savings allow."""

class InsufficientFundsError(LoanNotAllowedError):
    """Raised when the chama doesn't hold enough cash to lend the amount."""

class RepaymentExceedsBalanceError(ChamaError):
    """Raised when a repayment is larger than what is still owed."""