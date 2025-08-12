"""
Flask application factory.
"""

from datetime import timedelta
from flask import Flask
import logging
import os
from dotenv import load_dotenv
from pathlib import Path
from .database.db_manager import DatabaseManager
from .services.email import init_mail

# Get the path to the .env file (one directory up from this file)
env_path = Path(__file__).parent.parent / '.env'

# Load environment variables from .env file
load_dotenv(dotenv_path=env_path)

# Get configuration from environment variables
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://acs_user:Nick_ACS_DB_Password@localhost:5432/acs_db')
SECRET_KEY = os.getenv('SECRET_KEY')

# Initialize database manager
db = DatabaseManager(DATABASE_URL)

def create_app():
    """Initialize and configure the Flask application."""
    app = Flask(__name__,
                static_folder="../../frontend/static",
                template_folder="../../frontend/templates")

    # Configure app
    if not SECRET_KEY:
        raise ValueError("No SECRET_KEY set in environment variables")
    app.secret_key = SECRET_KEY
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

    # Initialize Flask-Mail
    init_mail(app)

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Register blueprints
    from .routes import auth, main
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)

    return app