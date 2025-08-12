"""
Project management functionality for the database.
Handles all project-related operations including:
- Project CRUD operations
- Search history
- AI interactions
"""

import logging
from typing import Optional, List, Dict, Any
import psycopg2
from psycopg2.extras import DictCursor

class ProjectManager:
    def __init__(self, database_url: str):
        """Initialize project manager with database connection."""
        self.database_url = database_url
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def get_connection(self):
        """Create and return a new database connection."""
        return psycopg2.connect(self.database_url)

    def create_project(self, user_id: int, project_name: str,
                       description: Optional[str] = None) -> Optional[int]:
        """
        Create a new project for a user.

        Args:
            user_id: ID of the project owner
            project_name: Name of the project
            description: Optional project description

        Returns:
            Optional[int]: Project ID if successful, None if failed
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute("""
                        INSERT INTO projects (user_id, project_name, description)
                        VALUES (%s, %s, %s)
                        RETURNING project_id
                    """, (user_id, project_name, description))
                    return cur.fetchone()[0]
                except psycopg2.Error:
                    conn.rollback()
                    return None

    def get_user_projects(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all projects for a user.

        Args:
            user_id: ID of the user

        Returns:
            List[Dict[str, Any]]: List of project details including search counts
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("""
                    SELECT project_id, project_name, description, created_at, updated_at,
                        (SELECT COUNT(*) FROM searches WHERE searches.project_id = projects.project_id) as search_count
                    FROM projects
                    WHERE user_id = %s
                    ORDER BY updated_at DESC
                """, (user_id,))
                return [dict(row) for row in cur.fetchall()]

    def delete_project(self, project_id: int) -> bool:
        """
        Delete a project and all associated searches.

        Args:
            project_id: ID of the project to delete

        Returns:
            bool: True if successful, False if failed
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute("""
                        DELETE FROM projects
                        WHERE project_id = %s
                        RETURNING project_id
                    """, (project_id,))
                    return cur.fetchone() is not None
                except psycopg2.Error:
                    conn.rollback()
                    return False

    def save_search(self, user_id: int, table_name: str, year: int,
                    acs_type: str, geography: str, variables: List[str],
                    project_id: Optional[int] = None) -> Optional[int]:
        """
        Save a search to the database.

        Args:
            user_id: ID of the user performing the search
            table_name: Name of the ACS table being searched
            year: Year of the data
            acs_type: Type of ACS data
            geography: Geographic level of the data
            variables: List of variable codes being searched
            project_id: Optional ID of the project to associate with the search

        Returns:
            Optional[int]: Search ID if successful, None if failed
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute("""
                        INSERT INTO searches 
                        (user_id, project_id, table_name, year, acs_type, 
                         geography, variables, is_saved)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE)
                        RETURNING search_id
                    """, (user_id, project_id, table_name, year, acs_type,
                          geography, variables))
                    return cur.fetchone()[0]
                except psycopg2.Error as e:
                    self.logger.error(f"Error saving search: {str(e)}")
                    conn.rollback()
                    return None

        def get_user_searches(self, user_id: int) -> List[Dict[str, Any]]:
            """
            Get all searches for a user.

            Args:
                user_id: ID of the user

            Returns:
                List[Dict[str, Any]]: List of search details including project names
            """
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute("""
                        SELECT s.*, p.project_name
                        FROM searches s
                        LEFT JOIN projects p ON s.project_id = p.project_id
                        WHERE s.user_id = %s
                        ORDER BY s.search_timestamp DESC
                    """, (user_id,))
                    return [dict(row) for row in cur.fetchall()]

        def get_project_searches(self, project_id: int) -> List[Dict[str, Any]]:
            """
            Get all searches for a project.

            Args:
                project_id: ID of the project

            Returns:
                List[Dict[str, Any]]: List of search details for the project
            """
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute("""
                        SELECT *
                        FROM searches
                        WHERE project_id = %s
                        ORDER BY search_timestamp DESC
                    """, (project_id,))
                    return [dict(row) for row in cur.fetchall()]

        def get_search(self, search_id: int) -> Optional[Dict[str, Any]]:
            """
            Get a single search by ID.

            Args:
                search_id: ID of the search to retrieve

            Returns:
                Optional[Dict[str, Any]]: Search details if found, None if not
            """
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute("""
                        SELECT s.*, p.project_name
                        FROM searches s
                        LEFT JOIN projects p ON s.project_id = p.project_id
                        WHERE s.search_id = %s
                    """, (search_id,))
                    result = cur.fetchone()
                    return dict(result) if result else None

        def update_search_saved_status(self, search_id: int, is_saved: bool) -> bool:
            """
            Update the saved status of a search.

            Args:
                search_id: ID of the search to update
                is_saved: New saved status

            Returns:
                bool: True if successful, False if failed
            """
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    try:
                        cur.execute("""
                            UPDATE searches
                            SET is_saved = %s
                            WHERE search_id = %s
                            RETURNING search_id
                        """, (is_saved, search_id))
                        return cur.fetchone() is not None
                    except psycopg2.Error:
                        conn.rollback()
                        return False

        def delete_search(self, search_id: int) -> bool:
            """
            Delete a search.

            Args:
                search_id: ID of the search to delete

            Returns:
                bool: True if successful, False if failed
            """
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    try:
                        cur.execute("""
                            DELETE FROM searches
                            WHERE search_id = %s
                            RETURNING search_id
                        """, (search_id,))
                        return cur.fetchone() is not None
                    except psycopg2.Error:
                        conn.rollback()
                        return False

        def save_ai_interaction(self, project_id: int, user_id: int,
                                query_text: str, response_text: str) -> Optional[int]:
            """
            Save an AI interaction to the database.

            Args:
                project_id: ID of the associated project
                user_id: ID of the user making the query
                query_text: The user's query text
                response_text: The AI's response text

            Returns:
                Optional[int]: Interaction ID if successful, None if failed
            """
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    try:
                        cur.execute("""
                            INSERT INTO ai_interactions 
                            (project_id, user_id, query_text, response_text)
                            VALUES (%s, %s, %s, %s)
                            RETURNING interaction_id
                        """, (project_id, user_id, query_text, response_text))
                        return cur.fetchone()[0]
                    except psycopg2.Error:
                        conn.rollback()
                        return None

    def get_saved_searches(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all saved searches for a user.

        Args:
            user_id: ID of the user

        Returns:
            List[Dict[str, Any]]: List of saved search details including project names
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("""
                    SELECT s.*, p.project_name
                    FROM searches s
                    LEFT JOIN projects p ON s.project_id = p.project_id
                    WHERE s.user_id = %s AND s.is_saved = TRUE
                    ORDER BY s.search_timestamp DESC
                """, (user_id,))
                return [dict(row) for row in cur.fetchall()]

    def get_saved_searches_by_project(self, user_id: int, project_id: int) -> List[Dict[str, Any]]:
        """
        Get all saved searches for a user in a specific project.

        Args:
            user_id: ID of the user
            project_id: ID of the project

        Returns:
            List[Dict[str, Any]]: List of saved search details for the project
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("""
                    SELECT s.*, p.project_name
                    FROM searches s
                    LEFT JOIN projects p ON s.project_id = p.project_id
                    WHERE s.user_id = %s 
                    AND s.project_id = %s 
                    AND s.is_saved = TRUE
                    ORDER BY s.search_timestamp DESC
                """, (user_id, project_id))
                return [dict(row) for row in cur.fetchall()]

    def update_search_project(self, search_id: int, project_id: int) -> bool:
        """Update the project association of a search."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute("""
                        UPDATE searches
                        SET project_id = %s
                        WHERE search_id = %s
                        RETURNING search_id
                    """, (project_id, search_id))
                    return cur.fetchone() is not None
                except psycopg2.Error:
                    conn.rollback()
                    return False

