class UserAlreadyExistsException(Exception):
    """
    Exception raised when attempting to add a user who already exists in the referral system.

    This exception indicates that the user with the specified unique identifier is already
    registered in the referral system. It helps prevent duplicate entries when adding new
    referrals and ensures that each user can only be referred once.
    """
    pass


class SelfReferralException(Exception):
    """
    Raised when a user attempts to use their own referral link for registration.

    This exception is intended to prevent users from benefiting from their own referral code.
    It should be used in referral systems where each user can only be invited by someone else,
    enforcing that users cannot register using their own referral link.
    """
    pass
