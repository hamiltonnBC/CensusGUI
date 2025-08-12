"""
Database Reset Utility Script

This script provides functionality to reset security-related database tables
and counters, particularly useful during development and testing.

Usage:
    python db_reset.py [--all] [--throttle] [--users] [--confirm]
"""

import psycopg2
import argparse
import logging
from typing import Optional

def setup_logger() -> logging.Logger:
    """Configure and return a logger for the script."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

class DatabaseResetter:
    """Handles resetting of security-related database tables and counters."""

    def __init__(self, database_url: str):
        """
        Initialize the database resetter.

        Args:
            database_url: PostgreSQL connection string
        """
        self.database_url = database_url
        self.logger = setup_logger()

    def get_connection(self):
        """Create and return a new database connection."""
        return psycopg2.connect(self.database_url)

    def reset_throttle_logs(self) -> bool:
        """
        Reset all throttle logs and rate limiting data.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("TRUNCATE TABLE throttle_log")
                    self.logger.info("Successfully cleared throttle logs")
                    return True
        except Exception as e:
            self.logger.error(f"Error clearing throttle logs: {str(e)}")
            return False

    def reset_user_security_counters(self) -> bool:
        """
        Reset all user security counters including failed login attempts
        and account lockouts.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE users
                        SET failed_login_attempts = 0,
                            account_locked_until = NULL,
                            last_failed_login = NULL
                    """)
                    self.logger.info("Successfully reset user security counters")
                    return True
        except Exception as e:
            self.logger.error(f"Error resetting user security counters: {str(e)}")
            return False

    def reset_login_history(self) -> bool:
        """
        Clear the login history table.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("TRUNCATE TABLE login_history")
                    self.logger.info("Successfully cleared login history")
                    return True
        except Exception as e:
            self.logger.error(f"Error clearing login history: {str(e)}")
            return False

def main():
    """Main function to handle command line arguments and execute resets."""
    parser = argparse.ArgumentParser(description='Reset database security tables and counters')
    parser.add_argument('--all', action='store_true', help='Reset all security-related data')
    parser.add_argument('--throttle', action='store_true', help='Reset only throttle logs')
    parser.add_argument('--users', action='store_true', help='Reset only user security counters')
    parser.add_argument('--confirm', action='store_true', help='Skip confirmation prompt')
    parser.add_argument('--database-url',
                    default='postgresql://acs_user:Nick_ACS_DB_Password@localhost:5432/acs_db',
                    help='Database connection URL')

    args = parser.parse_args()

    # If no specific reset option is chosen, default to --all
    if not (args.all or args.throttle or args.users):
        args.all = True

    # Confirm action unless --confirm is used
    if not args.confirm:
        print("WARNING: This will reset security-related data in your database.")
        print("This action cannot be undone.")
        response = input("Are you sure you want to continue? (y/N): ")
        if response.lower() != 'y':
            print("Operation cancelled.")
            return

    resetter = DatabaseResetter(args.database_url)

    if args.all or args.throttle:
        resetter.reset_throttle_logs()

    if args.all or args.users:
        resetter.reset_user_security_counters()
        resetter.reset_login_history()

if __name__ == "__main__":
    main()