#!/usr/bin/env python3
"""
Database setup script for CensusConnect application.
This script initializes the PostgreSQL database with the required schema.
"""

import psycopg2
import os
from pathlib import Path

def setup_database():
    """Initialize the database with the required schema."""
    
    # Database connection parameters
    db_params = {
        'host': 'localhost',
        'port': '5432',
        'database': 'acs_db',
        'user': 'acs_user',
        'password': 'Nick_ACS_DB_Password'
    }
    
    try:
        # Connect to the database
        print("Connecting to database...")
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        
        # Read and execute the SQL schema
        sql_file_path = Path('codebase/backend/app/database/migrations/init_db.sql')
        
        if not sql_file_path.exists():
            print(f"Error: SQL file not found at {sql_file_path}")
            return False
            
        with open(sql_file_path, 'r') as sql_file:
            sql_content = sql_file.read()
            
        print("Executing database schema...")
        cursor.execute(sql_content)
        conn.commit()
        
        print("✅ Database schema initialized successfully!")
        
        # Verify tables were created
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print(f"Created {len(tables)} tables:")
        for table in tables:
            print(f"  - {table[0]}")
            
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("CensusConnect Database Setup")
    print("=" * 30)
    
    success = setup_database()
    
    if success:
        print("\n🎉 Database setup complete!")
        print("You can now run the application with: python codebase/backend/app.py")
    else:
        print("\n❌ Database setup failed. Please check the error messages above.")