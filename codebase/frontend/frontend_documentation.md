# Component Documentation and System Flow

## Frontend Components

### Layout Components

1. **base.html** (templates/components/layout/base.html)
- Purpose: Main template that provides the basic HTML structure for all pages
- Interactions:
    - Includes header.html, footer.html
    - Provides blocks for content, scripts, and CSS
    - Used by: All other template files extend this base
- User Flow: Provides consistent layout and navigation across the application

2. **header.html** (templates/components/layout/header.html)
- Purpose: Navigation bar and user menu
- Interactions:
    - Includes user_menu.html
    - Connects to auth system via session data
    - Links to main sections of the application
- User Flow: Main navigation and access to user-related functions

3. **user_menu.html** (templates/components/auth/user_menu.html)
- Purpose: Displays user-specific navigation options
- Interactions:
    - Uses session data from backend
    - Links to profile_settings.html and logout functionality
- User Flow: Provides user account management access

### Form Components

1. **data_selection_form.html** (templates/components/forms/data_selection_form.html)
- Purpose: Main form for ACS data selection
- Interactions:
    - Works with data_selection.js
    - Sends requests to /api/generate_url and /process_data endpoints
    - Uses confirm.html for confirmations
- User Flow: Primary interface for data selection and query building

2. **password_form.html** (templates/components/forms/password_form.html)
- Purpose: Reusable password input component
- Interactions:
    - Works with password_validation.js
    - Used by change_password.html and reset_password.html
- User Flow: Consistent password entry experience across the application

### Account Management

1. **profile_settings.html** (templates/account/profile_settings.html)
- Purpose: Combined profile and settings management page
- Interactions:
    - Uses profile_settings.js
    - Connects to multiple backend endpoints (update_profile, update_settings)
    - Uses delete.html modal for account deletion
- User Flow: Central hub for user account management

2. **change_password.html** (templates/account/change_password.html)
- Purpose: Password change functionality
- Interactions:
    - Uses password_validation.js
    - Connects to change_password backend endpoint
    - Uses password_form.html component
- User Flow: Secure password update process

### Modal Components

1. **confirm.html** (templates/components/modals/confirm.html)
- Purpose: Generic confirmation dialog
- Interactions:
    - Used by data_selection_form.html
    - Controlled by data_selection.js
- User Flow: Confirms user actions before processing

2. **delete.html** (templates/components/modals/delete.html)
- Purpose: Account deletion confirmation
- Interactions:
    - Used by profile_settings.html
    - Controlled by profile_settings.js
    - Connects to delete_account backend endpoint
- User Flow: Secure account deletion process

### Alert Components

1. **error.html**, **info.html**, **success.html** (templates/components/alerts/)
- Purpose: Consistent message display system
- Interactions:
    - Used by all pages
    - Controlled by script.js for dismissal
    - Displays backend flash messages
- User Flow: User feedback for actions and system status

### Loading Components

1. **spinner.html** (templates/components/loaders/spinner.html)
- Purpose: Loading animation
- Interactions:
    - Used during AJAX requests
    - Controlled by various JavaScript files
- User Flow: Visual feedback during data processing

2. **progress.html** (templates/components/loaders/progress.html)
- Purpose: Progress bar for longer operations
- Interactions:
    - Used during data processing
    - Updates via WebSocket or polling
- User Flow: Progress feedback for longer operations

### Email Templates

1. **activation_email.html**, **notification_email.html**, **reset_password_email.html** (templates/email/)
- Purpose: Email communication templates
- Interactions:
    - Used by backend email system
    - Receives context data from backend
- User Flow: User communication for account actions

## JavaScript Files

1. **data_selection.js** (static/js/data_selection.js)
- Purpose: Handles data selection form functionality
- Interactions:
    - Controls data_selection_form.html
    - Makes API calls to backend
    - Updates confirmation dialogs
- User Flow: Interactive data selection process

2. **password_validation.js** (static/js/password_validation.js)
- Purpose: Real-time password validation
- Interactions:
    - Works with password forms
    - Validates against backend requirements
- User Flow: Immediate feedback on password strength

3. **profile_settings.js** (static/js/profile_settings.js)
- Purpose: Profile and settings page functionality
- Interactions:
    - Manages forms in profile_settings.html
    - Handles unsaved changes
    - Controls delete account modal
- User Flow: Interactive settings management

4. **script.js** (static/js/script.js)
- Purpose: Global utility functions
- Interactions:
    - Used across all pages
    - Handles common functionality like alerts
- User Flow: Consistent behavior across application

## Backend Interactions

### API Endpoints Used:
1. Authentication:
    - /login
    - /register
    - /logout
    - /reset-password
    - /change-password

2. Profile Management:
    - /update_profile
    - /update_settings
    - /delete_account

3. Data Operations:
    - /api/generate_url
    - /process_data

### Data Flow:
1. User Authentication:
    - Frontend forms → Backend validation
    - Session management
    - Email notifications

2. Data Selection:
    - Form submission → URL generation
    - Confirmation → Data processing
    - Results display

3. Profile Management:
    - Settings updates → Database updates
    - Password changes → Security validation
    - Account deletion → Cleanup processes

This structure provides a modular, maintainable system with clear separation of concerns and robust user interaction handling.