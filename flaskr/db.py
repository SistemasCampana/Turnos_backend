# flaskr/db.py
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        dbname=os.getenv("DB_NAME", "turnero"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "1206"),
        port=os.getenv("DB_PORT", 3306)
    )
