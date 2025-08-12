"""
Security management functionality for the database.
Handles all security-related operations including:
- Rate limiting
- Request throttling
- Security logging
"""

import logging
import psycopg2
from typing import Optional, Tuple

class SecurityManager:
    def __init__(self, database_url: str):
        """Initialize security manager with database connection."""
        self.database_url = database_url
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def get_connection(self):
        """Create and return a new database connection."""
        return psycopg2.connect(self.database_url)

    def check_rate_limit(self, ip_address: str, endpoint: str) -> bool:
        """
        Check if request should be rate limited.

        Security measures:
        - Configurable rate limits per endpoint
        - IP-based tracking
        - Progressive lockouts

        Args:
            ip_address: Client IP address
            endpoint: API endpoint being accessed

        Returns:
            bool: True if request is allowed, False if should be rate limited
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # Get rate limit rules for endpoint
                    cur.execute("""
                        SELECT max_attempts, time_window, lockout_duration
                        FROM throttle_rules
                        WHERE endpoint = %s
                    """, (endpoint,))
                    rule = cur.fetchone()

                    if not rule:
                        return True  # No rule found, allow request

                    max_attempts, time_window, lockout_duration = rule

                    # Check attempts within time window
                    cur.execute("""
                        SELECT COUNT(*) 
                        FROM throttle_log
                        WHERE ip_address = %s
                          AND endpoint = %s
                          AND timestamp > CURRENT_TIMESTAMP - interval '1 second' * %s
                    """, (ip_address, endpoint, time_window))

                    attempt_count = cur.fetchone()[0]

                    # Log attempt
                    is_blocked = attempt_count >= max_attempts
                    cur.execute("""
                        INSERT INTO throttle_log (ip_address, endpoint, is_blocked)
                        VALUES (%s, %s, %s)
                    """, (ip_address, endpoint, is_blocked))

                    if is_blocked:
                        self.logger.warning(
                            f"Rate limit exceeded for IP {ip_address} on endpoint {endpoint}"
                        )

                    return not is_blocked

        except Exception as e:
            self.logger.error(f"Error checking rate limit: {str(e)}")
            return False

    def get_rate_limit_status(self, ip_address: str, endpoint: str) -> Tuple[int, int]:
        """
        Get current rate limit status for an IP/endpoint combination.

        Args:
            ip_address: Client IP address
            endpoint: API endpoint

        Returns:
            Tuple[int, int]: (attempts_remaining, seconds_until_reset)
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # Get rate limit rule
                    cur.execute("""
                        SELECT max_attempts, time_window
                        FROM throttle_rules
                        WHERE endpoint = %s
                    """, (endpoint,))
                    rule = cur.fetchone()

                    if not rule:
                        return (-1, -1)  # No limit

                    max_attempts, time_window = rule

                    # Get current attempt count
                    cur.execute("""
                        SELECT COUNT(*), 
                               EXTRACT(EPOCH FROM (
                                   CURRENT_TIMESTAMP - MIN(timestamp)
                               ))::INTEGER as elapsed_seconds
                        FROM throttle_log
                        WHERE ip_address = %s
                          AND endpoint = %s
                          AND timestamp > CURRENT_TIMESTAMP - interval '1 second' * %s
                    """, (ip_address, endpoint, time_window))

                    result = cur.fetchone()
                    current_attempts = result[0]
                    elapsed_seconds = result[1] or 0

                    remaining_attempts = max(0, max_attempts - current_attempts)
                    seconds_until_reset = max(0, time_window - elapsed_seconds)

                    return (remaining_attempts, seconds_until_reset)

        except Exception as e:
            self.logger.error(f"Error getting rate limit status: {str(e)}")
            return (0, 0)

    def clear_expired_logs(self) -> bool:
        """
        Clear expired entries from the throttle log.
        Should be run periodically to prevent table bloat.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        DELETE FROM throttle_log
                        WHERE timestamp < CURRENT_TIMESTAMP - interval '1 day'
                    """)
                    return True
        except Exception as e:
            self.logger.error(f"Error clearing expired logs: {str(e)}")
            return False