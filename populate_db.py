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

    add_media("South Park Season 5", "F:\\VLC PLaylists\\South Park Season 5.xspf")
    add_media("South Park Season 10", "F:\\VLC PLaylists\\South Park Season 10.xspf")
    add_media("The Bear", "F:\\VLC PLaylists\\The Bear.xspf")
    add_media("True Detective", "F:\\VLC PLaylists\\True Detective.xspf")
    add_media("TTN Bumps", "F:\\VLC PLaylists\\TTN Bumps.xspf")
    add_media("Twin Peaks", "F:\\VLC PLaylists\\Twin Peaks.xspf")
    add_media("WWDITS", "F:\\VLC PLaylists\\WWDITS.xspf")
    add_media("Adolescence", "F:\\VLC PLaylists\\Adolescence.xspf")
    add_media("Adult Animation", "F:\\VLC PLaylists\\Adult Animation.xspf")
    add_media("American Dad and Family Guy", "F:\\VLC PLaylists\\American Dad and Family Guy.xspf")
    add_media("American Dad", "F:\\VLC PLaylists\\American Dad.xspf")
    add_media("Archer", "F:\\VLC PLaylists\\Archer.xspf")
    add_media("ATLA", "F:\\VLC PLaylists\\ATLA.xspf")
    add_media("Bojack Horseman", "F:\\VLC PLaylists\\Bojack Horseman.xspf")
    add_media("Chainsaw Man", "F:\\VLC PLaylists\\Chainsaw Man.xspf")
    add_media("Comedy TV", "F:\\VLC PLaylists\\Comedy TV.xspf")
    add_media("Courage the Cowardly Dog", "F:\\VLC PLaylists\\Courage the Cowardly Dog.xspf")
    add_media("Cyberpunk", "F:\\VLC PLaylists\\Cyberpunk.xspf")
    add_media("Family Guy Season 23", "F:\\VLC PLaylists\\Family Guy Season 23.xspf")
    add_media("Futurama", "F:\\VLC PLaylists\\Futurama.xspf")
    add_media("Gravity Falls", "F:\\VLC PLaylists\\Gravity Falls.xspf")
    add_media("Hannibal", "F:\\VLC PLaylists\\Hannibal.xspf")
    add_media("Horror", "F:\\VLC PLaylists\\Horror.xspf")
    add_media("I Think You Should Leave", "F:\\VLC PLaylists\\I Think You Should Leave.xspf")
    add_media("IASIP", "F:\\VLC PLaylists\\IASIP.xspf")
    add_media("IASP Season 16", "F:\\VLC PLaylists\\IASP Season 16.xspf")
    add_media("KOTH", "F:\\VLC PLaylists\\KOTH.xspf")
    add_media("Movies", "F:\\VLC PLaylists\\Movies.xspf")
    add_media("Mr. Robot", "F:\\VLC PLaylists\\Mr. Robot.xspf")
    add_media("New Movies", "F:\\VLC PLaylists\\New Movies.xspf")
    add_media("Rick and Morty Season 8", "F:\\VLC PLaylists\\Rick and Morty Season 8.xspf")
    add_media("Saturday Morning Cartoons", "F:\\VLC PLaylists\\Saturday Morning Cartoons.xspf")
    add_media("Scream", "F:\\VLC PLaylists\\Scream.xspf")
    add_media("Serial Experiments Lain", "F:\\VLC PLaylists\\Serial Experiments Lain.xspf")
    add_media("Severance", "F:\\VLC PLaylists\\Severance.xspf")
    add_media("Smiling Friends", "F:\\VLC PLaylists\\Smiling Friends.xspf")
    add_media("Pluto", "F:\\VLC PLaylists\\Pluto.xspf")
    
    logging.info("Finished populating database.")