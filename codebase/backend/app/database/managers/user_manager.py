"""
User management functionality for the database.
Handles all user-related operations including:
- User creation
- User verification
- Account activation
- User retrieval
"""
#TODO Remove the email bypass and implement the email verification process once google email works again
#TODO NEED TO UPDATE DOCUMENTATION TO INCLUDE ADD USER SETTINGS THAT ARE HERE AND THAT ARE NOW IN THE DATABASE
import bcrypt
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import psycopg2
from psycopg2.extras import DictCursor

class UserManager:
    def __init__(self, database_url: str):
        """Initialize user manager with database connection."""
        self.database_url = database_url
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def get_connection(self):
        """Create and return a new database connection."""
        return psycopg2.connect(self.database_url)

    def create_user(self, username: str, email: str, password: str) -> Optional[int]:
        """
        Create a new user with security features.

        Args:
            username: Desired username
            email: User's email
            password: Plain text password to be hashed

        Returns:
            Optional[int]: User ID if successful, None if failed
        """
        try:
            # Generate secure password hash with high work factor
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12))

            # Generate activation token
            activation_token = secrets.token_urlsafe(32)

            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # Check for existing user
                    cur.execute("""
                        SELECT username, email FROM users 
                        WHERE username = %s OR email = %s
                    """, (username, email))

                    if cur.fetchone():
                        self.logger.warning(f"Attempted duplicate registration: {username}")
                        return None

                    # Create new user with activation token
                    #TODO change is_active to False
                    cur.execute("""
                        INSERT INTO users (
                            username, email, password_hash, 
                            is_active, activation_token, 
                            activation_token_created_at
                        )
                        VALUES (%s, %s, %s, TRUE, %s, CURRENT_TIMESTAMP)
                        RETURNING user_id
                    """, (username, email, password_hash.decode('utf-8'), activation_token))

                    user_id = cur.fetchone()[0]
                    return user_id

        except Exception as e:
            self.logger.error(f"Error in create_user: {str(e)}")
            return None

    def verify_user(self, username: str, password: str, ip_address: str = None,
                    user_agent: str = None) -> Optional[Dict[str, Any]]:
        """
        Verify user credentials with security checks.

        Args:
            username: Username attempting to log in
            password: Password to verify
            ip_address: Client IP address
            user_agent: Client user agent string

        Returns:
            Optional[Dict[str, Any]]: User data if verified, None if not
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    # Check if account is locked
                    cur.execute("""
                        SELECT user_id, username, password_hash, is_active,
                               failed_login_attempts, account_locked_until
                        FROM users
                        WHERE username = %s
                    """, (username,))
                    user = cur.fetchone()

                    if not user:
                        self._log_login_attempt(None, ip_address, user_agent, False, "User not found")
                        return None

                    # Check account lockout
                    if user['account_locked_until'] and user['account_locked_until'] > datetime.now():
                        self._log_login_attempt(
                            user['user_id'], ip_address, user_agent, False,
                            "Account locked"
                        )
                        return None

                    # Verify password
                    if not bcrypt.checkpw(password.encode('utf-8'),
                                          user['password_hash'].encode('utf-8')):
                        # Update failed login attempts
                        cur.execute("""
                            UPDATE users 
                            SET failed_login_attempts = failed_login_attempts + 1,
                                last_failed_login = CURRENT_TIMESTAMP,
                                account_locked_until = CASE 
                                    WHEN failed_login_attempts + 1 >= 5 
                                    THEN CURRENT_TIMESTAMP + interval '15 minutes'
                                    ELSE account_locked_until
                                END
                            WHERE user_id = %s
                        """, (user['user_id'],))

                        self._log_login_attempt(
                            user['user_id'], ip_address, user_agent, False,
                            "Invalid password"
                        )
                        return None

                    # Check if account is activated
                    if not user['is_active']:
                        self._log_login_attempt(
                            user['user_id'], ip_address, user_agent, False,
                            "Account not activated"
                        )
                        return None

                    # Successful login - reset failed attempts and update last login
                    cur.execute("""
                        UPDATE users
                        SET failed_login_attempts = 0,
                            account_locked_until = NULL,
                            last_login = CURRENT_TIMESTAMP
                        WHERE user_id = %s
                    """, (user['user_id'],))

                    self._log_login_attempt(
                        user['user_id'], ip_address, user_agent, True, None
                    )

                    return dict(user)

        except Exception as e:
            self.logger.error(f"Error in verify_user: {str(e)}")
            return None

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user details by ID.

        Args:
            user_id: ID of the user to retrieve

        Returns:
            Optional[Dict[str, Any]]: User data if found, None if not
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute("""
                        SELECT user_id, username, email, is_active, 
                               activation_token, reset_password_token
                        FROM users
                        WHERE user_id = %s
                    """, (user_id,))
                    user = cur.fetchone()
                    return dict(user) if user else None
        except Exception as e:
            self.logger.error(f"Error retrieving user: {str(e)}")
            return None

    def activate_user(self, token: str) -> bool:
        """
        Activate a user account using the activation token.

        Args:
            token: Activation token sent to user's email

        Returns:
            bool: True if activation successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # First, check if token exists and is valid
                    cur.execute("""
                        SELECT user_id, is_active, activation_token_created_at
                        FROM users 
                        WHERE activation_token = %s
                    """, (token,))

                    user = cur.fetchone()
                    if not user:
                        self.logger.warning(f"Invalid activation token attempted: {token}")
                        return False

                    user_id, is_active, token_created_at = user

                    # Check if already activated
                    if is_active:
                        self.logger.info(f"Already activated account accessed: {user_id}")
                        return True

                    # Check if token has expired (24 hours)
                    current_time = datetime.now(token_created_at.tzinfo)
                    if token_created_at < current_time - timedelta(days=1):
                        self.logger.warning(f"Expired activation token used: {user_id}")
                        return False

                    # Activate the account
                    cur.execute("""
                        UPDATE users 
                        SET is_active = TRUE,
                            activation_token = NULL,
                            activation_token_created_at = NULL
                        WHERE user_id = %s
                    """, (user_id,))

                    self.logger.info(f"Successfully activated account: {user_id}")
                    return True

        except Exception as e:
            self.logger.error(f"Error in activate_user: {str(e)}")
            return False

    def _log_login_attempt(self, user_id: Optional[int], ip_address: Optional[str],
                           user_agent: Optional[str], successful: bool,
                           failure_reason: Optional[str]) -> None:
        """
        Log login attempt to database for security auditing.

        Args:
            user_id: ID of user attempting to log in
            ip_address: Client IP address
            user_agent: Client user agent string
            successful: Whether login attempt was successful
            failure_reason: Reason for failure if unsuccessful
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO login_history (
                            user_id, ip_address, user_agent, 
                            login_successful, failure_reason
                        )
                        VALUES (%s, %s, %s, %s, %s)
                    """, (user_id, ip_address, user_agent, successful, failure_reason))
        except Exception as e:
            self.logger.error(f"Error logging login attempt: {str(e)}")



    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user details by ID.

        Args:
            user_id: ID of the user to retrieve

        Returns:
            Optional[Dict[str, Any]]: User data if found, None if not found
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute("""
                        SELECT user_id, username, email, is_active, 
                               api_key, notify_search_complete, notify_account_activity,
                               default_view, created_at, last_login
                        FROM users
                        WHERE user_id = %s
                    """, (user_id,))
                    user = cur.fetchone()
                    return dict(user) if user else None
        except Exception as e:
            self.logger.error(f"Error retrieving user: {str(e)}")
            return None

    def update_user_profile(self, user_id: int, username: str, email: str) -> bool:
        """
        Update user profile information.

        Args:
            user_id: ID of the user to update
            username: New username
            email: New email address

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # Check if username or email already exists
                    cur.execute("""
                        SELECT user_id FROM users 
                        WHERE (username = %s OR email = %s) AND user_id != %s
                    """, (username, email, user_id))

                    if cur.fetchone():
                        self.logger.warning(f"Username or email already exists: {username}, {email}")
                        return False

                    cur.execute("""
                        UPDATE users 
                        SET username = %s, 
                            email = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = %s
                        RETURNING user_id
                    """, (username, email, user_id))

                    return cur.fetchone() is not None
        except Exception as e:
            self.logger.error(f"Error updating user profile: {str(e)}")
            return False

    def update_user_settings(self, user_id: int, notify_search_complete: bool = False,
                             notify_account_activity: bool = False, default_view: str = 'table',
                             api_key: Optional[str] = None) -> bool:
        """
        Update user settings.

        Args:
            user_id: ID of the user to update
            notify_search_complete: Whether to notify on search completion
            notify_account_activity: Whether to notify on account activity
            default_view: Default data view preference
            api_key: Census API key

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    update_fields = []
                    params = []

                    # Build dynamic update query
                    if notify_search_complete is not None:
                        update_fields.append("notify_search_complete = %s")
                        params.append(notify_search_complete)

                    if notify_account_activity is not None:
                        update_fields.append("notify_account_activity = %s")
                        params.append(notify_account_activity)

                    if default_view:
                        update_fields.append("default_view = %s")
                        params.append(default_view)

                    if api_key is not None:
                        update_fields.append("api_key = %s")
                        params.append(api_key)

                    if not update_fields:
                        return True  # No updates needed

                    update_fields.append("updated_at = CURRENT_TIMESTAMP")
                    query = f"""
                        UPDATE users 
                        SET {', '.join(update_fields)}
                        WHERE user_id = %s
                        RETURNING user_id
                    """
                    params.append(user_id)

                    cur.execute(query, params)
                    return cur.fetchone() is not None
        except Exception as e:
            self.logger.error(f"Error updating user settings: {str(e)}")
            return False

    def delete_user(self, user_id: int) -> bool:
        """
        Delete a user and all associated data.

        Args:
            user_id: ID of the user to delete

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # First, delete all user-related data
                    # Projects and searches will be deleted via CASCADE
                    cur.execute("""
                        DELETE FROM users
                        WHERE user_id = %s
                        RETURNING user_id
                    """, (user_id,))

                    return cur.fetchone() is not None
        except Exception as e:
            self.logger.error(f"Error deleting user: {str(e)}")
            return False


    def update_password(self, user_id: int, new_password: str) -> bool:
        """
        Update user's password.

        Args:
            user_id: ID of the user
            new_password: New password to set

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Generate new password hash
            password_hash = bcrypt.hashpw(
                new_password.encode('utf-8'),
                bcrypt.gensalt(rounds=12)
            ).decode('utf-8')

            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # Update password
                    cur.execute("""
                        UPDATE users 
                        SET password_hash = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = %s
                        RETURNING user_id
                    """, (password_hash, user_id))

                    # Store in password history
                    if cur.fetchone():
                        cur.execute("""
                            INSERT INTO password_history (user_id, password_hash)
                            VALUES (%s, %s)
                        """, (user_id, password_hash))
                        return True
                    return False

        except Exception as e:
            self.logger.error(f"Error updating password: {str(e)}")
            return False