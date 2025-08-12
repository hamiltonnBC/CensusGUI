"""
Census API interaction services with enhanced debugging.
"""

import requests
import pandas as pd
from typing import Dict, Any, Optional, List, Tuple
import logging
import os
import json
from datetime import datetime

class CensusAPIService:
    def __init__(self):
        """Initialize the Census API Service with detailed logging."""
        # Set up logging with more detailed format
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'census_api_{datetime.now().strftime("%Y%m%d")}.log'),
                logging.StreamHandler()
            ]
        )
        self.output_directory = 'census_data'
        os.makedirs(self.output_directory, exist_ok=True)

    def fetch_data(self, year: str, table: str, variables: List[str],
                   geography: str, acs_type: str, api_key: Optional[str]) -> pd.DataFrame:
        """
        Fetch data with enhanced error checking and debugging.
        """
        try:
            # Log the full request details
            request_details = {
                'year': year,
                'table': table,
                'variables': variables,
                'geography': geography,
                'acs_type': acs_type,
                'has_api_key': bool(api_key)
            }
            self.logger.debug(f"Starting fetch_data with parameters: {json.dumps(request_details)}")

            # Validate input parameters
            if not all([year, table, variables, geography, acs_type]):
                self.logger.error("Missing required parameters")
                self.logger.debug(f"Parameters received: {request_details}")
                return pd.DataFrame()

            # Construct API URL
            base_url = f'https://api.census.gov/data/{year}/acs/{acs_type}'
            if table.startswith('DP'):
                base_url += '/profile'

            # Build query parameters
            params = {
                'get': f'NAME,{",".join(variables)}',
                'for': geography
            }
            if api_key:
                params['key'] = api_key

            # Log the full URL and parameters (excluding API key)
            debug_params = params.copy()
            if 'key' in debug_params:
                debug_params['key'] = '[REDACTED]'
            self.logger.debug(f"API URL: {base_url}")
            self.logger.debug(f"Parameters: {debug_params}")

            # Make the request with explicit timeout
            response = requests.get(base_url, params=params, timeout=30)

            # Log response details
            self.logger.debug(f"Response status code: {response.status_code}")
            self.logger.debug(f"Response headers: {dict(response.headers)}")

            if response.status_code != 200:
                self.logger.error(f"API request failed: {response.status_code}")
                self.logger.error(f"Error response: {response.text}")
                return pd.DataFrame()

            # Parse JSON response with explicit error handling
            try:
                data = response.json()
                self.logger.debug(f"Successfully parsed JSON response. Row count: {len(data) if data else 0}")
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse JSON response: {str(e)}")
                self.logger.debug(f"Raw response content: {response.text[:500]}...")  # Log first 500 chars
                return pd.DataFrame()

            # Validate data structure
            if not data or len(data) < 2:
                self.logger.error("Invalid data structure received")
                self.logger.debug(f"Data received: {data}")
                return pd.DataFrame()

            # Create DataFrame
            df = pd.DataFrame(data[1:], columns=data[0])
            self.logger.info(f"Successfully created DataFrame with shape: {df.shape}")

            return df

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {str(e)}")
            return pd.DataFrame()
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return pd.DataFrame()

    def process_multiple_requests(self, tables: List[Dict], years: List[str],
                                  geography: str, acs_type: str,
                                  api_key: Optional[str]) -> Dict[str, Any]:
        """Process multiple requests with enhanced debugging."""
        try:
            self.logger.info("Starting multiple request processing")

            # Validate and log request details
            request_info = {
                'table_count': len(tables),
                'year_count': len(years),
                'geography': geography,
                'acs_type': acs_type
            }
            self.logger.info(f"Processing request: {json.dumps(request_info)}")

            # Process each request individually and track results
            results = []
            for table in tables:
                for year in years:
                    self.logger.info(f"Processing table {table['id']} for year {year}")

                    df = self.fetch_data(
                        year=year,
                        table=table['id'],
                        variables=table['variables'],
                        geography=geography,
                        acs_type=acs_type,
                        api_key=api_key
                    )

                    if not df.empty:
                        self.logger.info(f"Successfully fetched data: {df.shape}")
                        results.append(df)
                    else:
                        self.logger.error(f"Failed to fetch data for table {table['id']} year {year}")

            if not results:
                self.logger.error("No data retrieved from any request")
                return {"error": "No data retrieved", "details": "All requests failed"}


            # Unsure if the below code is working, this logging info section
            logging.info(f"Saving data to CSV. DataFrame shape: {df.shape}")
            output_file = os.path.join(self.output_directory, f"combined_data_{'-'.join(years)}_{acs_type}.csv")
            df.to_csv(output_file, index=False)
            logging.info(f"Data saved to: {output_file}")
            #####


            return {
                "success": True,
                "datasets": len(results),
                "total_rows": sum(len(df) for df in results)
            }

        except Exception as e:
            self.logger.error(f"Error in process_multiple_requests: {str(e)}")
            return {"error": str(e)}