"""
Base database manager with connection handling.

This module provides the foundation for all specialized database managers.
It handles basic database connection management and logging setup.

Features:
- Database connection management
- Centralized logging configuration
- Basic error handling
"""

import psycopg2
from psycopg2.extras import DictCursor
import logging
from typing import Optional
import psycopg2.extensions

class BaseManager:
    """
    Base class for all database managers.

    Provides common functionality for database connections and logging.
    All specialized managers should inherit from this class to ensure
    consistent connection handling and logging behavior.

    Attributes:
        database_url (str): PostgreSQL connection string
        logger (logging.Logger): Logger instance for this manager
    """

    def __init__(self, database_url: str):
        """
        Initialize the base manager.

        Args:
            database_url: PostgreSQL connection string in format:
                postgresql://user:password@host:port/database
        """
        self.database_url = database_url

        # Configure logging for all managers
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_connection(self) -> psycopg2.extensions.connection:
        """
        Create and return a new database connection.

        Returns:
            psycopg2.extensions.connection: New PostgreSQL connection

        Raises:
            psycopg2.Error: If connection cannot be established
        """
        try:
            return psycopg2.connect(self.database_url)
        except psycopg2.Error as e:
            self.logger.error(f"Failed to connect to database: {str(e)}")
            raise