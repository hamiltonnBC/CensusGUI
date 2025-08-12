"""
Main database manager that combines all specialized managers.

This module provides a unified interface to all database operations by combining
the specialized managers through multiple inheritance. It serves as the main entry
point for the application to interact with the database.

Implementation follows the principle of composition through inheritance, where each
specialized manager handles a specific domain of database operations while inheriting
common functionality from the BaseManager.

Usage example:
    db = DatabaseManager('postgresql://user:pass@localhost/dbname')
    user_id = db.create_user('username', 'email', 'password')
    session = db.create_session(user_id, '127.0.0.1', 'Mozilla/5.0')
    project_id = db.create_project(user_id, 'My Project')
"""

from .managers import UserManager, SessionManager, SecurityManager, ProjectManager

class DatabaseManager(UserManager, SessionManager, SecurityManager, ProjectManager):
    """
    Comprehensive database manager combining all specialized managers.

    Inherits from all specialized managers to provide a unified interface for:
    - User Management: Account creation, verification, and profile management
    - Session Management: User session handling and authentication
    - Security: Rate limiting, request throttling, and security logging
    - Project Management: Project CRUD operations and search history

    This class uses multiple inheritance where all parent classes inherit from
    BaseManager, ensuring consistent database connection handling across all
    operations.

    Note:
        The order of inheritance matters - managers are listed in order of
        dependency and priority for method resolution.
    """

    def __init__(self, database_url: str):
        """
        Initialize the database manager.

        Initializes all parent managers with the same database connection.

        Args:
            database_url: PostgreSQL connection string in format:
                postgresql://user:password@host:port/database
        """
        # Initialize all parent classes with the same database URL
        super().__init__(database_url)

        # Log successful initialization
        self.logger.info("Database manager initialized successfully")