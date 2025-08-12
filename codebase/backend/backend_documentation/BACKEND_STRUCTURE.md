# Backend Structure Documentation

This document explains the purpose and responsibility of each component in the backend structure.

## Directory Structure Overview

```
backend/
├── __init__.py
├── app/
│   ├── __init__.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── login.py            # Login-related routes
│   │   │   ├── password.py         # Password reset functionality
│   │   │   ├── register.py         # Registration routes
│   │   │   └── validators.py       # Input validation utilities #TODO NEED TO ADD PROFILE.PY
│   │   └── main.py                 # Main application routes
│   ├── services/
│   │   ├── __init__.py
│   │   ├── census.py               # Census API interactions
│   │   └── email.py                # Email service functionality
│   └── database/
│       ├── __init__.py
│       ├── db_manager.py           # Main database manager
│       ├── managers/               # Specialized database managers
│       │   ├── __init__.py
│       │   ├── base_manager.py     # Base database functionality
│       │   ├── project_manager.py  # Project operations
│       │   ├── security_manager.py # Security measures
│       │   ├── session_manager.py  # Session handling
│       │   └── user_manager.py     # User operations
│       └── migrations/
│           └── init_db.sql         # Database schema
└── app.py                          # Application entry point
```


## File Purposes

### Main Files

#### `backend/app.py`
- Entry point of the application
- Imports and creates the Flask application instance
- Minimal file that only initializes the app
- Allows usage of `flask run` command

### App Package (`app/`)

#### `app/__init__.py`
- Application factory
- Initializes Flask application
- Configures the app (loads config, sets up database)
- Registers all blueprints (routes)
- Sets up logging and error handling

### Routes Package (`app/routes/`)

#### `app/routes/__init__.py`
- Initializes the routes package

### Services Package (`app/services/`)

#### `app/services/__init__.py`
- Initializes the services package

#### `app/services/census.py`
Handles all Census API interactions:
- ACS data retrieval functions
- Variable name fetching
- Data formatting and processing
- API URL construction
- Response parsing
- Error handling for Census API calls

#### `app/services/email.py`
Manages email functionality and interactions:
- Email verification for new accounts
- Password reset emails
- Template rendering for emails
- SMTP configuration handling
- Email sending error handling
- Connection management with email service
- Security measures for email tokens

### Routes Package (`app/routes/`)

#### `app/routes/auth/`
Authentication and authorization related routes organized by functionality:

##### `auth/__init__.py`
- Initializes the auth package
- Exports the blueprint and shared decorators
- Registers all auth-related routes

##### `auth/login.py`
Handles user login functionality:
- Login route handling
- Session creation
- Rate limiting checks
- Failed attempt tracking
- Login security measures
- `login_required` decorator

##### `auth/register.py`
Manages new user registration:
- Registration form handling
- Input validation
- Account creation
- Email verification initiation
- Account activation
- Rate limiting for registrations

##### `auth/password.py`
Password management functionality:
- Password reset requests
- Token validation
- Password updates
- Security measures for resets
- Rate limiting for reset attempts

##### `auth/validators.py`
Input validation utilities:
- Password strength checking
- Email format validation
- Username format validation
- Security requirement checks
- Common validation functions

#### `app/routes/main.py`
Contains all main application routes:
- Home page (`/`)
- Data submission (`/api/submit`)
- Data processing (`/process_data`)
- URL generation (`/api/generate_url`)
- Project management routes
- Search management routes
- Other API endpoints

### Services Package (`app/services/`)

#### `app/services/__init__.py`
- Initializes the services package

#### `app/services/census.py`
Handles all Census API interactions:
- ACS data retrieval functions
- Variable name fetching
- Data formatting and processing
- API URL construction
- Response parsing
- Error handling for Census API calls
]
#### `app/services/email.py`
Manages email functionality and interactions:

- Email verification for new accounts
- Password reset emails
- Template rendering for emails
- SMTP configuration handling
- Email sending error handling
- Connection management with email service
- Security measures for email tokens

### Database Package (`app/database/`)

#### `app/database/__init__.py`
- Initializes the database package

#### `app/database/db_manager.py`
Main database manager that inherits from all specialized managers:
- Combines functionality from all manager classes
- Serves as the main entry point for database operations
- Provides a unified interface to the application

#### `app/database/managers/`
Directory containing specialized database managers:

##### `managers/base_manager.py`
Base manager class with common functionality:
- Database connection management
- Basic logging setup
- Common utility methods

##### `managers/user_manager.py`
Handles user-related operations:
- User creation and verification
- Account activation
- Password management and reset
- User authentication

##### `managers/session_manager.py`
Manages user sessions:
- Session creation and validation
- Session token management
- Session expiration handling

##### `managers/security_manager.py`
Implements security measures:
- Rate limiting
- Login attempt tracking
- Security audit logging
- IP blocking and monitoring

##### `managers/project_manager.py`
Manages project and search operations:
- Project CRUD operations
- Search history tracking
- AI interaction logging
- Data persistence for project-related data

#### `app/database/migrations/`
Contains database schema and migration files:
- `init.sql`: Initial database schema creation
   - Defines all table structures
   - Creates necessary indexes
   - Sets up triggers and functions
   - Establishes relationships between tables
   - Essential for setting up new database instances

## Package Responsibilities

### Routes (`app/routes/`)
- Handle HTTP requests
- Process form data and query parameters
- Manage user sessions
- Call appropriate services
- Return responses (HTML or JSON)
- Handle route-specific errors

### Services (`app/services/`)
- Contain business logic
- Process data
- Make external API calls
- Format responses
- Handle service-specific errors
- Provide reusable functionality

### Database (`app/database/`)
- Manage database connections
- Handle all SQL queries
- Provide data access layer
- Manage transactions
- Handle database errors
- Implement security measures

## Design Principles

1. **Separation of Concerns**
    - Routes only handle request/response
    - Services contain business logic
    - Database handles data persistence

2. **Modularity**
    - Each package can be modified independently
    - Clear interfaces between components
    - Easy to test individual components

3. **Single Responsibility**
    - Each file has a specific purpose
    - Functions are focused and maintainable
    - Clear dependencies between modules

4. **Security**
    - Authentication handled in dedicated module
    - Database access controlled and sanitized
    - API keys and sensitive data properly managed

## Usage

To add new functionality:
1. Add routes in appropriate route file
2. Add business logic in services
3. Add database operations in db_manager
4. Register new routes in `app/__init__.py`

This structure allows for easy maintenance, testing, and scaling of the application while maintaining clean separation of concerns.

