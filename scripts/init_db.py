import sys
import os
from sqlalchemy_utils import database_exists, create_database

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.db_manager import init_db, engine
from src.config import DATABASE_URL

def main():
    print(f"Initializing database at {DATABASE_URL}")
    
    if not database_exists(engine.url):
        create_database(engine.url)
        print(f"Created database {DATABASE_URL}")
    else:
        print(f"Database already exists at {DATABASE_URL}")
    
    init_db()
    
    print("Database initialization complete")

if __name__ == "__main__":
    main()