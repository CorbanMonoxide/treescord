import sqlite3
import logging

DATABASE_FILE = "media_library.db"

def add_media(name, file_path):
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO media (name, file_path) VALUES (?, ?)", (name, file_path))
        conn.commit()
        conn.close()
        logging.info(f"Added media: {name} - {file_path}")
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    add_media("AS Bumps", "C:\\Users\\corba\\Videos\\AS bumps\\AS Bumps.xspf")
    add_media("1", "C:\\Users\\corba\\Videos\\Short Videos\\1.xspf")