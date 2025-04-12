# database_cog.py
import discord
from discord.ext import commands
import sqlite3
import logging
import asyncio

DATABASE_FILE = "media_library.db"

class DatabaseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.DATABASE_FILE = DATABASE_FILE
        self.pagination_sessions = {}  # Stores active pagination sessions

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

    async def paginate_media_library(self, ctx, media_list, page=0):
        """
        Displays a paginated list of media files and allows navigation.
        """
        chunk_size = 10  # Number of items per page
        chunks = [media_list[i:i + chunk_size] for i in range(0, len(media_list), chunk_size)]
        total_pages = len(chunks)

        if page >= total_pages or page < 0:
            await ctx.send("Invalid page number.")
            return

        # Create the embed for the current page
        embed = discord.Embed(title="Media Library", description=f"Page {page + 1}/{total_pages}")
        start_index = page * chunk_size + 1  # Calculate the starting index for the current page
        for i, media_name in enumerate(chunks[page], start=start_index):
            embed.add_field(name=f"{i}. {media_name}", value="\u200b", inline=False)

        # Send the embed and add navigation reactions
        message = await ctx.send(embed=embed)
        await message.add_reaction("⬅️")  # Previous page
        await message.add_reaction("➡️")  # Next page
        await message.add_reaction("❌")  # Exit

        # Store the pagination session
        self.pagination_sessions[message.id] = {
            "ctx": ctx,
            "media_list": media_list,
            "page": page,
            "total_pages": total_pages,
        }

    @commands.command(brief="Lists all media files in the library with pagination📃.", aliases=['list'])
    async def media(self, ctx):
        """
        Lists all media files in the library with pagination.
        """
        try:
            media_library = self.get_media_library()
            if not media_library:
                await ctx.send("The media library is empty.")
                return

            # Convert media library keys to a list
            media_list = list(media_library.keys())

            # Start pagination
            await self.paginate_media_library(ctx, media_list)
        except Exception as e:
            logging.error(f"Error listing media: {e}")
            await ctx.send(f"Error listing media: {e}")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """
        Handles reaction-based pagination.
        """
        if user.bot:  # Ignore reactions from the bot itself
            return

        message_id = reaction.message.id
        if message_id not in self.pagination_sessions:
            return

        session = self.pagination_sessions[message_id]
        ctx = session["ctx"]
        media_list = session["media_list"]
        page = session["page"]
        total_pages = session["total_pages"]

        if str(reaction.emoji) == "⬅️":  # Previous page
            if page > 0:
                page -= 1
        elif str(reaction.emoji) == "➡️":  # Next page
            if page < total_pages - 1:
                page += 1
        elif str(reaction.emoji) == "❌":  # Exit
            await reaction.message.delete()
            del self.pagination_sessions[message_id]
            return

        # Update the session
        session["page"] = page

        # Update the embed
        await self.paginate_media_library(ctx, media_list, page)

        # Remove the user's reaction
        await reaction.remove(user)