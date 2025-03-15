# database_cog.py
import discord
from discord.ext import commands
import sqlite3
import logging

DATABASE_FILE = "media_library.db"

class DatabaseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.DATABASE_FILE = DATABASE_FILE

    def get_media_library(self):
        """
        Retrieves all media files from the database and returns them as a dictionary.
        The dictionary maps media names to their file paths.
        """
        try:
            conn = sqlite3.connect(self.DATABASE_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT name, file_path FROM media")
            return {name: file_path for name, file_path in cursor.fetchall()}
        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")
            return {}

    def media_exists(self, media_name):
        """
        Checks if a media file exists in the database.
        """
        try:
            conn = sqlite3.connect(self.DATABASE_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM media WHERE name = ?", (media_name,))
            return cursor.fetchone() is not None
        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")
            return False

    async def add_media_to_database(self, media_name, file_path):
        """
        Adds a media file to the database if it doesn't already exist.
        """
        try:
            conn = sqlite3.connect(self.DATABASE_FILE)
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO media (name, file_path) VALUES (?, ?)", (media_name, file_path))
            conn.commit()
            conn.close()
            logging.info(f"Added media to database: {media_name}")
        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")

    @commands.command(brief="Lists all media files in the library.")
    async def list(self, ctx):
        """
        Lists all media files in the library, splitting the output into multiple messages if necessary.
        """
        try:
            media_library = self.get_media_library()
            if not media_library:
                await ctx.send("The media library is empty.")
                return

            # Split the media list into chunks of 20 items each
            media_list = list(media_library.keys())
            chunk_size = 20  # Reduced chunk size to stay under 2,000 characters
            chunks = [media_list[i:i + chunk_size] for i in range(0, len(media_list), chunk_size)]

            # Send each chunk as a separate message
            for i, chunk in enumerate(chunks):
                media_list_str = "\n".join(chunk)
                await ctx.send(f"Media Library (Part {i + 1}):\n{media_list_str}")

        except Exception as e:
            logging.error(f"Error listing media: {e}")
            await ctx.send(f"Error listing media: {e}")