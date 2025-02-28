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

    add_media("Hellsing - Ep. 03 - Sword Dancer", "C:\\Users\\Corban\\Downloads\\HELLSING (2001-2018) - Complete Original, ULTIMATE, Abridged TV Series - 480p-1080p x264\\1a. Original (2001-02)\\Hellsing - Ep. 03 - Sword Dancer (480p DVDRip - DUAL Audio).mkv")
    add_media("Hellsing - Ep. 02 - Club M", "C:\\Users\\Corban\\Downloads\\HELLSING (2001-2018) - Complete Original, ULTIMATE, Abridged TV Series - 480p-1080p x264\\1a. Original (2001-02)\\Hellsing - Ep. 02 - Club M (480p DVDRip - DUAL Audio).mkv")
    add_media("Hellsing - Ep. 07 - Duel", "C:\\Users\\Corban\\Downloads\\HELLSING (2001-2018) - Complete Original, ULTIMATE, Abridged TV Series - 480p-1080p x264\\1a. Original (2001-02)\\Hellsing - Ep. 07 - Duel (480p DVDRip - DUAL Audio).mkv")
    add_media("Hellsing - Ep. 13 - Hellfire", "C:\\Users\\Corban\\Downloads\\HELLSING (2001-2018) - Complete Original, ULTIMATE, Abridged TV Series - 480p-1080p x264\\1a. Original (2001-02)\\Hellsing - Ep. 13 - Hellfire (480p DVDRip - DUAL Audio).mkv")
    add_media("Hellsing - Ep. 11 - Transcend Force", "C:\\Users\\Corban\\Downloads\\HELLSING (2001-2018) - Complete Original, ULTIMATE, Abridged TV Series - 480p-1080p x264\\1a. Original (2001-02)\\Hellsing - Ep. 11 - Transcend Force (480p DVDRip - DUAL Audio).mkv")
    add_media("Hellsing - Ep. 12 - Total Destruction", "C:\\Users\\Corban\\Downloads\\HELLSING (2001-2018) - Complete Original, ULTIMATE, Abridged TV Series - 480p-1080p x264\\1a. Original (2001-02)\\Hellsing - Ep. 12 - Total Destruction (480p DVDRip - DUAL Audio).mkv")
    add_media("Hellsing - Ep. 10 - Master of Monster", "C:\\Users\\Corban\\Downloads\\HELLSING (2001-2018) - Complete Original, ULTIMATE, Abridged TV Series - 480p-1080p x264\\1a. Original (2001-02)\\Hellsing - Ep. 10 - Master of Monster (480p DVDRip - DUAL Audio).mkv")
    add_media("Hellsing - Ep. 01 - The Undead", "C:\\Users\\Corban\\Downloads\\HELLSING (2001-2018) - Complete Original, ULTIMATE, Abridged TV Series - 480p-1080p x264\\1a. Original (2001-02)\\Hellsing - Ep. 01 - The Undead (480p DVDRip - DUAL Audio).mkv")
    add_media("Hellsing - Ep. 09 - Red Rose Vertigo", "C:\\Users\\Corban\\Downloads\\HELLSING (2001-2018) - Complete Original, ULTIMATE, Abridged TV Series - 480p-1080p x264\\1a. Original (2001-02)\\Hellsing - Ep. 09 - Red Rose Vertigo (480p DVDRip - DUAL Audio).mkv")
    add_media("Hellsing - Ep. 04 - Innocent as a Human", "C:\\Users\\Corban\\Downloads\\HELLSING (2001-2018) - Complete Original, ULTIMATE, Abridged TV Series - 480p-1080p x264\\1a. Original (2001-02)\\Hellsing - Ep. 04 - Innocent as a Human (480p DVDRip - DUAL Audio).mkv")
    add_media("Hellsing - Ep. 05 - Brotherhood", "C:\\Users\\Corban\\Downloads\\HELLSING (2001-2018) - Complete Original, ULTIMATE, Abridged TV Series - 480p-1080p x264\\1a. Original (2001-02)\\Hellsing - Ep. 05 - Brotherhood (480p DVDRip - DUAL Audio).mkv")
    add_media("Hellsing - Ep. 06 - Dead Zone", "C:\\Users\\Corban\\Downloads\\HELLSING (2001-2018) - Complete Original, ULTIMATE, Abridged TV Series - 480p-1080p x264\\1a. Original (2001-02)\\Hellsing - Ep. 06 - Dead Zone (480p DVDRip - DUAL Audio).mkv")
    add_media("Hellsing - Ep. 08 - Kill House", "C:\\Users\\Corban\\Downloads\\HELLSING (2001-2018) - Complete Original, ULTIMATE, Abridged TV Series - 480p-1080p x264\\1a. Original (2001-02)\\Hellsing - Ep. 08 - Kill House (480p DVDRip - DUAL Audio).mkv")