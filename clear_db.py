# clear_db.py
import sqlite3
import logging

# Database file
DATABASE_FILE = "media_library.db"

def clear_database():
    """
    Clears all entries from the 'media' table in the database.
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        # Clear the 'media' table
        cursor.execute("DELETE FROM media")
        conn.commit()

        # Log success
        logging.info("Database cleared successfully.")

    except sqlite3.Error as e:
        # Log any errors
        logging.error(f"Database error: {e}")

    finally:
        # Close the database connection
        if conn:
            conn.close()

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Clear the database
    clear_database()