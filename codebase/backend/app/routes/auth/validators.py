"""
Validation functions for authentication.
"""

import re
from email_validator import validate_email, EmailNotValidError
from typing import Tuple

def validate_password(password: str) -> Tuple[bool, str]:
    """
    Validate password strength.
    Requirements:
    - At least 8 characters
    - Contains uppercase and lowercase
    - Contains numbers
    - Contains special characters
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain uppercase letters"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain lowercase letters"
    if not re.search(r"\d", password):
        return False, "Password must contain numbers"
    if not re.search(r"[ !@#$%&'()*+,-./[\\\]^_`{|}~"+r'"]', password):
        return False, "Password must contain special characters"
    return True, ""

def validate_email_address(email: str) -> Tuple[bool, str, str]:
    """
    Validate email address format.
    Returns: (is_valid, normalized_email, error_message)
    """
    try:
        valid = validate_email(email)
        return True, valid.email, ""
    except EmailNotValidError as e:
        return False, "", str(e)

def validate_username(username: str) -> Tuple[bool, str]:
    """
    Validate username format.
    Requirements:
    - 3-20 characters
    - Only letters, numbers, underscores, and hyphens
    """
    if not re.match(r"^[a-zA-Z0-9_-]{3,20}$", username):
        return False, "Username must be 3-20 characters and contain only letters, numbers, underscores, and hyphens"
    return True, ""