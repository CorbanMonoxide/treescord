import sqlite3
import logging

DATABASE_FILE = "media_library.db"

def create_database():
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS media (
                name TEXT PRIMARY KEY,
                file_path TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
        logging.info(f"Database '{DATABASE_FILE}' and table 'media' created successfully.")
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    create_database()