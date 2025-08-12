"""
Session management functionality for the database.
Handles all session-related operations including:
- Session creation
- Session verification
- Session invalidation (logout)
"""

import logging
import secrets
from datetime import datetime, timedelta
from typing import Optional
import psycopg2

class SessionManager:
    def __init__(self, database_url: str):
        """Initialize session manager with database connection."""
        self.database_url = database_url
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def get_connection(self):
        """Create and return a new database connection."""
        return psycopg2.connect(self.database_url)

    def create_session(self, user_id: int, ip_address: str,
                       user_agent: str) -> Optional[str]:
        """
        Create a new session for authenticated user.

        Security measures:
        - Secure random token generation
        - IP and user agent tracking
        - Session expiration

        Args:
            user_id: ID of authenticated user
            ip_address: Client IP address
            user_agent: Client user agent string

        Returns:
            Optional[str]: Session token if successful, None if failed
        """
        try:
            session_token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(hours=24)

            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO user_sessions (
                            user_id, session_token, ip_address, 
                            user_agent, expires_at
                        )
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING session_token
                    """, (user_id, session_token, ip_address, user_agent, expires_at))
                    return cur.fetchone()[0]
        except Exception as e:
            self.logger.error(f"Error creating session: {str(e)}")
            return None

    def verify_session(self, session_token: str, ip_address: str,
                       user_agent: str) -> Optional[int]:
        """
        Verify session token is valid and not expired.

        Security measures:
        - Session expiration check
        - IP address verification
        - User agent verification

        Args:
            session_token: Token to verify
            ip_address: Client IP address
            user_agent: Client user agent string

        Returns:
            Optional[int]: User ID if session is valid, None if not
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT user_id
                        FROM user_sessions
                        WHERE session_token = %s
                          AND ip_address = %s
                          AND user_agent = %s
                          AND expires_at > CURRENT_TIMESTAMP
                          AND is_active = TRUE
                    """, (session_token, ip_address, user_agent))
                    result = cur.fetchone()
                    return result[0] if result else None
        except Exception as e:
            self.logger.error(f"Error verifying session: {str(e)}")
            return None

    def invalidate_session(self, session_token: str) -> bool:
        """
        Invalidate a session (logout).

        Args:
            session_token: Token to invalidate

        Returns:
            bool: True if session was invalidated, False otherwise
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE user_sessions
                        SET is_active = FALSE
                        WHERE session_token = %s
                        RETURNING session_id
                    """, (session_token,))
                    return cur.fetchone() is not None
        except Exception as e:
            self.logger.error(f"Error invalidating session: {str(e)}")
            return False