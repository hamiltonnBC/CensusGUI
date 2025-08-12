"""
Main routes for the application.
Handles data processing, projects, and search functionality.
"""

from flask import Blueprint, request, jsonify, redirect, url_for, render_template, session
import pandas as pd
from .. import db
#from .auth import login_required
from .auth.login import login_required
#from ..services.census import fetch_and_save_data, get_variable_names, generate_census_api_url
import requests
from functools import wraps
import logging
from ..services.census import CensusAPIService

#for emailing feedback
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


bp = Blueprint('main', __name__)
bp.logger = logging.getLogger(__name__)
census_service = CensusAPIService()

@bp.route('/')
def index():
    """Render the main application page."""
    return render_template('index.html')

@bp.route('/request_data')
def request_data():
    """Render the request data page."""
    return render_template('request_data.html')

@bp.route('/instructions')
def instructions():
    """Render the instructions page."""
    return render_template('instructions.html')

@bp.route('/about')
def about():
    """
    Render the About page containing detailed system information and feedback form.

    Returns:
        rendered template: The about.html template with any necessary context
    """
    return render_template('about.html')

"""
Main route handlers for Census data processing.
"""


@bp.route('/api/submit', methods=['POST'])
@login_required
def submit_data():
    """
    Handle data submission requests for multiple tables and years.

    Expected request format:
    {
        "tables": [
            {
                "id": "DP02",
                "variables": ["DP02_0001E", "DP02_0002E"]
            },
            ...
        ],
        "years": ["2019", "2020"],
        "acs_type": "acs1",
        "geography": "state:*",
        "include_metadata": false,
        "api_key": "optional-api-key",
        "project_id": "optional-project-id"
    }
    """
    try:
        data = request.json
        search_ids = []

        # Save searches for each table-year combination
        for table in data['tables']:
            for year in data['years']:
                search_id = db.save_search(
                    user_id=session['user_id'],
                    project_id=data.get('project_id'),
                    table_name=table['id'],
                    year=year,
                    acs_type=data['acs_type'],
                    geography=data['geography'],
                    variables=table['variables'] if table.get('variables') else []
                )
                search_ids.append(search_id)

        # Process all data requests
        result = census_service.process_multiple_requests(
            tables=data['tables'],
            years=data['years'],
            geography=data['geography'],
            acs_type=data['acs_type'],
            api_key=data['api_key'].strip('"') if data.get('api_key') else None
        )

        if 'error' in result:
            return jsonify(result), 400

        result['search_ids'] = search_ids
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/generate_url', methods=['POST'])
def generate_url():
    """
    Generate Census API URLs for multiple tables and years.

    Expected request format:
    {
        "tables": [
            {
                "id": "DP02",
                "variables": ["DP02_0001E", "DP02_0002E"]
            },
            ...
        ],
        "years": ["2019", "2020"],
        "acs_type": "acs1",
        "geography": "state:*",
        "api_key": "optional-api-key"
    }
    """
    try:
        data = request.json
        urls = []

        for table in data['tables']:
            for year in data['years']:
                # Determine if it's a profile table
                is_profile = table['id'].startswith('DP')
                base_url = f'https://api.census.gov/data/{year}/acs/{data["acs_type"]}'

                # Construct URL based on table type
                if is_profile:
                    url = f'{base_url}/profile?get=NAME,{",".join(table["variables"])}&for={data["geography"]}'
                else:
                    url = f'{base_url}?get=NAME,{",".join(table["variables"])}&for={data["geography"]}'

                # Add API key if provided
                if data.get('api_key'):
                    url += f'&key={data["api_key"].strip('"')}'

                urls.append({
                    'table': table['id'],
                    'year': year,
                    'url': url
                })

        return jsonify({"urls": urls})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/debug_url', methods=['POST'])
def debug_url():
    """
    Debug endpoint to test API URL generation and responses for multiple requests.

    Expected request format: Same as generate_url
    """
    try:
        data = request.json
        debug_results = []

        for table in data['tables']:
            for year in data['years']:
                # Determine if it's a profile table
                is_profile = table['id'].startswith('DP')
                base_url = f'https://api.census.gov/data/{year}/acs/{data["acs_type"]}'

                # Construct URL based on table type
                if is_profile:
                    url = f'{base_url}/profile?get=NAME,{",".join(table["variables"])}&for={data["geography"]}'
                else:
                    url = f'{base_url}?get=NAME,{",".join(table["variables"])}&for={data["geography"]}'

                # Add API key if provided
                if data.get('api_key'):
                    url += f'&key={data["api_key"].strip('"')}'

                # Test the URL
                response = requests.get(url)

                debug_results.append({
                    'table': table['id'],
                    'year': year,
                    'api_url': url,
                    'status_code': response.status_code,
                    'response_text': response.text if response.status_code != 200 else 'Success',
                    'headers': dict(response.headers)
                })

        return jsonify({'results': debug_results})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Helper function to validate request data
def validate_request_data(data):
    """
    Validate the request data format.

    Args:
        data: Request JSON data

    Returns:
        tuple: (is_valid: bool, error_message: str)
    """
    required_fields = ['tables', 'years', 'acs_type', 'geography']

    # Check required fields
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"

    # Validate tables format
    if not isinstance(data['tables'], list) or not data['tables']:
        return False, "Tables must be a non-empty list"

    for table in data['tables']:
        if not isinstance(table, dict) or 'id' not in table:
            return False, "Each table must have an 'id' field"
        if 'variables' in table and not isinstance(table['variables'], list):
            return False, "Table variables must be a list"

    # Validate years format
    if not isinstance(data['years'], list) or not data['years']:
        return False, "Years must be a non-empty list"

    return True, ""

@bp.route('/process_data', methods=['GET', 'POST'])
@login_required
def process_data():
    """
    Process Census data and render visualization.
    Handles both single search display and multiple table/year processing.
    """
    try:
        census_service = CensusAPIService()
        projects = db.get_user_projects(session['user_id'])
        available_years = range(2009, 2023)

        if request.method == 'POST':
            data = request.json
            logging.info(f"Received data request: {data}")

            # Process data using CensusAPIService
            result = census_service.process_multiple_requests(
                tables=data['tables'],
                years=data['years'],
                geography=data['geography'],
                acs_type=data['acs_type'],
                api_key=data.get('api_key')
            )

            logging.info(f"Census API result: {result}")

            if "error" in result:
                return jsonify({"error": result["error"]}), 400

            # Create DataFrame from the result
            try:
                # Check if we have data
                if result.get('success') and result.get('datasets') > 0:
                    # Get the most recently created CSV file in the census_data directory
                    import glob
                    import os

                    census_data_dir = 'census_data'
                    list_of_files = glob.glob(f'{census_data_dir}/*.csv')
                    if not list_of_files:
                        raise FileNotFoundError("No CSV files found in census_data directory")

                    latest_file = max(list_of_files, key=os.path.getctime)
                    df = pd.read_csv(latest_file)

                    # Generate table HTML with proper classes
                    table_html = df.to_html(
                        index=False,
                        classes=['data-table', 'display', 'compact'],
                        table_id='census-data-table'
                    )

                    # Save search history
                    for table in data['tables']:
                        db.save_search(
                            user_id=session['user_id'],
                            project_id=data.get('project_id'),
                            table_name=table['id'],
                            year=data['years'][0],
                            acs_type=data['acs_type'],
                            geography=data['geography'],
                            variables=table['variables']
                        )

                    return render_template('data_display.html',
                                           table_html=table_html,
                                           table_names=[t['id'] for t in data['tables']],
                                           years=data['years'],
                                           geography=data['geography'],
                                           available_years=available_years,
                                           acs_type=data['acs_type'],
                                           projects=projects
                                           )
                else:
                    raise ValueError("No data received from Census API")

            except Exception as e:
                logging.error(f"Error processing CSV: {str(e)}")
                return jsonify({
                    "error": f"Error processing data: {str(e)}"
                }), 500

        # Handle GET request or other scenarios if needed

    except Exception as e:
        logging.error(f"Process data error: {str(e)}")
        return jsonify({
            "error": f"Error processing request: {str(e)}"
        }), 500



@bp.route('/update_data', methods=['POST'])
def update_data():
    """Handle requests to update data with additional variables or years."""
    more_variables = request.form.get('moreVariables')
    more_years = request.form.getlist('moreYears')
    return jsonify({'status': 'success'})

@bp.route('/saved_searches')
@login_required
def saved_searches():
    """Display user's saved searches with optional project filter."""
    project_id = request.args.get('project')
    if project_id:
        searches = db.get_project_searches(project_id)
    else:
        searches = db.get_saved_searches(session['user_id'])

    projects = db.get_user_projects(session['user_id'])
    return render_template('saved_searches.html', searches=searches, projects=projects)

@bp.route('/api/rerun_search/<int:search_id>', methods=['POST'])
@login_required
def rerun_search(search_id):
    """Rerun a saved search."""
    search = db.get_search(search_id)
    if search and search['user_id'] == session['user_id']:
        return jsonify({'success': True, 'search': search})
    return jsonify({'success': False, 'error': 'Search not found'}), 404

@bp.route('/api/save_search/<int:search_id>', methods=['POST'])
@login_required
def save_search(search_id):
    """Update an existing search's saved status."""
    data = request.json
    project_id = data.get('projectId')

    try:
        if project_id:
            # Update project association and saved status
            success = db.update_search_project(search_id, project_id) and \
                      db.update_search_saved_status(search_id, True)
        else:
            # Just update saved status
            success = db.update_search_saved_status(search_id, True)

        if success:
            return jsonify({'success': True})
        return jsonify({
            'success': False,
            'error': 'Failed to save search'
        }), 400

    except Exception as e:
        bp.logger.error(f"Error updating search: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Server error occurred'
        }), 500

@bp.route('/api/delete_search/<int:search_id>', methods=['DELETE'])
@login_required
def delete_search(search_id):
    """Delete a search."""
    if db.delete_search(search_id):
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Failed to delete search'}), 400

@bp.route('/projects')
@login_required
def projects():
    """Handle project listing and creation."""
    projects = db.get_user_projects(session['user_id'])
    return render_template('projects.html', projects=projects)

@bp.route('/api/projects', methods=['POST'])
@login_required
def create_project():
    """Create a new project."""
    data = request.json
    project_id = db.create_project(
        user_id=session['user_id'],
        project_name=data['project_name'],
        description=data.get('description', '')
    )
    if project_id:
        return jsonify({'success': True, 'project_id': project_id})
    return jsonify({'success': False, 'error': 'Failed to create project'}), 400

@bp.route('/api/projects/<int:project_id>', methods=['DELETE'])
@login_required
def delete_project(project_id):
    """Delete a project."""
    if db.delete_project(project_id):
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Failed to delete project'}), 400

@bp.route('/api/save_current_search', methods=['POST'])
@login_required
def save_current_search():
    """Save the current search either generally or to a project."""
    try:
        data = request.json
        save_type = data.get('saveType')
        project_id = data.get('projectId') if save_type == 'project' else None

        current_search = session.get('current_search')
        if not current_search:
            return jsonify({
                'success': False,
                'error': 'No active search found'
            }), 400

        # Save the search
        search_id = db.save_search(
            user_id=session['user_id'],
            table_name=current_search['table_name'],
            year=current_search['year'],
            acs_type=current_search['acs_type'],
            geography=current_search['geography'],
            variables=current_search['variables'],
            project_id=project_id
        )

        if search_id:
            return jsonify({
                'success': True,
                'search_id': search_id
            })

        return jsonify({
            'success': False,
            'error': 'Failed to save search'
        }), 400

    except Exception as e:
        bp.logger.error(f"Error saving search: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Server error occurred'
        }), 500

@bp.route('/api/saved_searches/filtered')
@login_required
def get_filtered_searches():
    """Get saved searches with optional project filter."""
    try:
        project_id = request.args.get('project_id')

        if project_id:
            searches = db.get_saved_searches_by_project(
                session['user_id'],
                int(project_id)
            )
        else:
            searches = db.get_saved_searches(session['user_id'])

        return jsonify({
            'success': True,
            'searches': searches
        })

    except Exception as e:
        bp.logger.error(f"Error retrieving searches: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Server error occurred'
        }), 500


#TODO NEEDS FIXED
# for emailing feedback
    @bp.route('/api/feedback', methods=['POST'])
    def submit_feedback():
        """
        Handle feedback submission from the About page and send it via email.

        Returns:
            JSON response indicating success or failure
        """
        if not session.get('user_id'):
            return jsonify({'error': 'Must be logged in to submit feedback'}), 401

        try:
            data = request.get_json()
            category = data.get('category')
            feedback = data.get('feedback')
            user_id = session.get('user_id')

            # Get user email from database
            user = db.get_user(user_id)
            user_email = user.get('email', 'No email provided')

            # Create email content
            msg = MIMEMultipart()
            msg['From'] = app.config['MAIL_USERNAME']
            msg['To'] = 'censusconnectacs@gmail.com'
            msg['Subject'] = f"CensusConnect Feedback - {category}"

            body = f"""
            Feedback Category: {category}
            User ID: {user_id}
            User Email: {user_email}
            
            Feedback:
            {feedback}
            """

            msg.attach(MIMEText(body, 'plain'))

            # Send email
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
                server.send_message(msg)

            return jsonify({'message': 'Feedback received successfully'}), 200
        except Exception as e:
            app.logger.error(f"Error sending feedback email: {str(e)}")
            return jsonify({'error': 'Error processing feedback'}), 500

