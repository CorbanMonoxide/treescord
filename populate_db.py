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

    add_media("Adult Animation", "F:\\VLC PLaylists\\Adult Animation.xspf")
    add_media("American Dad and Family Guy", "F:\\VLC PLaylists\\American Dad and Family Guy.xspf")
    add_media("American Dad", "F:\\VLC PLaylists\\American Dad.xspf")
    add_media("Courage the Cowardly Dog", "F:\\VLC PLaylists\\Courage the Cowardly Dog.xspf")
    add_media("Saturday Morning Cartoons", "F:\\VLC PLaylists\\Saturday Morning Cartoons.xspf")