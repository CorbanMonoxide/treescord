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
        try:
            conn = sqlite3.connect(self.DATABASE_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT name, file_path FROM media")
            return {name: file_path for name, file_path in cursor.fetchall()}
        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")
            return {}

    @commands.command(brief="Lists all media files in the library.")
    async def list(self, ctx):
        try:
            media_library = self.get_media_library()
            media_list_str = "\n".join(media_library.keys())
            await ctx.send(f"Media Library:\n{media_list_str}")
        except Exception as e:
            logging.error(f"Error listing media: {e}")
            await ctx.send(f"Error listing media: {e}")