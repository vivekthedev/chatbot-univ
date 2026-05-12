import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    """Returns a fresh MySQL connection using .env credentials."""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "university_chatbot")
    )
