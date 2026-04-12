import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Fetch variables
DATABASE_URL = os.getenv("DATABASE_URL")

print(f"Connecting to: {DATABASE_URL}")

try:
    # Connect to the database
    connection = psycopg2.connect(DATABASE_URL)
    
    # Create a cursor
    cursor = connection.cursor()
    
    # Execute a simple query
    cursor.execute("SELECT version();")
    
    # Fetch the result
    db_version = cursor.fetchone()
    print("Successfully connected to Supabase!")
    print(f"Database version: {db_version}")
    
    # Close cursor and connection
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"Connection failed: {e}")
