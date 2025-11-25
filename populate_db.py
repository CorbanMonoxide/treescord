import sqlite3
import logging
import os

DATABASE_FILE = "media_library.db"
PLAYLIST_DIR = "playlists"

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

    # Ensure playlist directory exists
    if not os.path.exists(PLAYLIST_DIR):
        os.makedirs(PLAYLIST_DIR)
        logging.warning(f"Created directory '{PLAYLIST_DIR}'. Please place your .xspf files there.")

    # Dictionary of Name -> Filename
    media_files = {
        "South Park Season 5": "South Park Season 5.xspf",
        "South Park Season 10": "South Park Season 10.xspf",
        "The Bear": "The Bear.xspf",
        "True Detective": "True Detective.xspf",
        "TTN Bumps": "TTN Bumps.xspf",
        "Twin Peaks": "Twin Peaks.xspf",
        "WWDITS": "WWDITS.xspf",
        "Adolescence": "Adolescence.xspf",
        "Adult Animation": "Adult Animation.xspf",
        "American Dad and Family Guy": "American Dad and Family Guy.xspf",
        "American Dad": "American Dad.xspf",
        "Archer": "Archer.xspf",
        "ATLA": "ATLA.xspf",
        "Bojack Horseman": "Bojack Horseman.xspf",
        "Chainsaw Man": "Chainsaw Man.xspf",
        "Comedy TV": "Comedy TV.xspf",
        "Courage the Cowardly Dog": "Courage the Cowardly Dog.xspf",
        "Cyberpunk": "Cyberpunk.xspf",
        "Family Guy Season 23": "Family Guy Season 23.xspf",
        "Futurama": "Futurama.xspf",
        "Gravity Falls": "Gravity Falls.xspf",
        "Hannibal": "Hannibal.xspf",
        "Horror": "Horror.xspf",
        "I Think You Should Leave": "I Think You Should Leave.xspf",
        "IASIP": "IASIP.xspf",
        "IASP Season 16": "IASP Season 16.xspf",
        "KOTH": "KOTH.xspf",
        "Movies": "Movies.xspf",
        "Mr. Robot": "Mr. Robot.xspf",
        "New Movies": "New Movies.xspf",
        "Rick and Morty Season 8": "Rick and Morty Season 8.xspf",
        "Saturday Morning Cartoons": "Saturday Morning Cartoons.xspf",
        "Scream": "Scream.xspf"
    }

    for name, filename in media_files.items():
        # Use absolute path based on current working directory
        full_path = os.path.abspath(os.path.join(PLAYLIST_DIR, filename))
        add_media(name, full_path)
    add_media("Serial Experiments Lain", "F:\\VLC PLaylists\\Serial Experiments Lain.xspf")
    add_media("Severance", "F:\\VLC PLaylists\\Severance.xspf")
    add_media("Smiling Friends", "F:\\VLC PLaylists\\Smiling Friends.xspf")
    add_media("Pluto", "F:\\VLC PLaylists\\Pluto.xspf")
    
    logging.info("Finished populating database.")