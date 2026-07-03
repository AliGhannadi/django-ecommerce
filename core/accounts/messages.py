class Messages:
    """Centralized API response and validation messages."""

    # Success
    registered_successfully = "User registered successfully. Check your email for verification"
    authenticated_successfully = "Authenticated successfully."
    password_changed_successfully = "Password changed successfully."
    token_refreshed_successfully = "Token refreshed successfully."
    password_reset_link_sent = "Password reset link sent."
    password_reset_completed = "Password reset completed."
    logout_successfully = "Logged out successfully."

    # Auth errors
    user_not_found = "User not found."
    invalid_credentials = "Invalid credentials."
    jwt_missing = "Refresh token is missing."
    jwt_invalid = "Invalid or expired refresh token."

    # Password errors
    passwords_doesnt_match = "Passwords does not match."
    old_password_doenst_match = "Old password does not match."
    new_password_doenst_match = "New passwords do not match."
    reset_link_invalid = "The reset link is invalid."

    # Registration / reset
    registration_failed = "An error occured."
    no_user_with_email = "There is no user with provided email."
    token_expired = "Token expired."
    token_invalid = "Token invalid."

    # Field validation (DRF error_messages)
    email_missing = "Email is missing"
    password_missing = "Password is missing"
