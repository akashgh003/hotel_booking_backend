import sys
import os

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.db_manager import init_db
from src.config import DATABASE_URL
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

def main():
    print(f"Initializing database at {DATABASE_URL}")
    
    # Create the database if it doesn't exist
    engine = create_engine(DATABASE_URL)
    if not database_exists(engine.url):
        create_database(engine.url)
        print(f"Created database {DATABASE_URL}")
    
    # Create tables
    init_db()
    print("Database schema initialized successfully")

if __name__ == "__main__":
    main()