# database_cog.py
import discord
from discord.ext import commands
import aiosqlite
import logging
import asyncio
import config

DATABASE_FILE = config.MEDIA_DB

class DatabaseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.DATABASE_FILE = DATABASE_FILE
        self.pagination_sessions = {}  # Stores active pagination sessions

    async def get_media_library(self):
        """
        Retrieves all media files from the database and returns them as a dictionary.
        The dictionary maps media names to their file paths.
        """
        try:
            async with aiosqlite.connect(self.DATABASE_FILE) as db:
                async with db.execute("SELECT name, file_path FROM media") as cursor:
                    rows = await cursor.fetchall()
                    return {name: file_path for name, file_path in rows}
        except Exception as e:
            logging.error(f"Database error: {e}")
            return {}

    def _create_media_embed(self, media_list_chunk, page_num, total_pages):
        """
        Helper function to create an embed for a media library page.
        """
        description_lines = []
        start_index = page_num * 10 + 1 # Assuming chunk_size is 10
        for i, media_name in enumerate(media_list_chunk, start=start_index):
            description_lines.append(f"{i}. {media_name}")
        
        embed = discord.Embed(title="Media Library", description="\n".join(description_lines) if description_lines else "No media on this page.")
        embed.set_footer(text=f"Page {page_num + 1}/{total_pages}")
        return embed

    async def _send_initial_media_page(self, ctx, media_list):
        """
        Sends the initial media library page and sets up pagination.
        """
        chunk_size = 10
        total_pages = (len(media_list) + chunk_size - 1) // chunk_size
        current_page = 0

        current_chunk = media_list[current_page * chunk_size : (current_page + 1) * chunk_size]
        embed = self._create_media_embed(current_chunk, current_page, total_pages)

        message = await ctx.send(embed=embed)

        reactions_to_add = []
        if total_pages > 1:
            reactions_to_add.extend(["⬅️", "➡️"])
        reactions_to_add.extend(["❌", "📱", "🍃"])

        for reaction_emoji in reactions_to_add:
            await message.add_reaction(reaction_emoji)

        self.pagination_sessions[message.id] = {
            "ctx": ctx,
            "message_object": message, # Store the message object
            "media_list": media_list,
            "current_page": current_page,
            "total_pages": total_pages,
            "chunk_size": chunk_size,
        }
    @commands.command(brief="Lists all media files in the library with pagination📃.", aliases=['list'])
    async def media(self, ctx):
        """
        Lists all media files in the library with pagination.
        """
        try:
            media_library = await self.get_media_library()
            if not media_library:
                await ctx.send("The media library is empty.")
                return

            # Convert media library keys to a list
            media_list = list(media_library.keys())

            # Start pagination
            await self._send_initial_media_page(ctx, media_list)
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
        message_object = session["message_object"]
        media_list = session["media_list"]
        current_page = session["current_page"]
        total_pages = session["total_pages"]
        chunk_size = session["chunk_size"]
        emoji_str = str(reaction.emoji)

        new_page = current_page

        if emoji_str == "⬅️":
            if current_page > 0:
                new_page = current_page - 1
            else: # Wrap to last page
                new_page = total_pages - 1
        elif emoji_str == "➡️":
            if current_page < total_pages - 1:
                new_page = current_page + 1
            else: # Wrap to first page
                new_page = 0
        elif emoji_str == "❌":
            try:
                await message_object.delete()
            except discord.NotFound:
                logging.warning(f"Media list message {message_object.id} already deleted.")
            if message_id in self.pagination_sessions:
                del self.pagination_sessions[message_id]
            return
        elif emoji_str == "📱":
            remote_cog = self.bot.get_cog("RemoteCog")
            if remote_cog:
                await remote_cog.create_controller(ctx)
            else:
                await ctx.send("Remote controller feature is not available.", delete_after=10)
            try: await reaction.remove(user)
            except (discord.Forbidden, discord.NotFound): pass
            return
        elif emoji_str == "🍃":
            toke_cog = self.bot.get_cog("TokeCog")
            if toke_cog:
                await toke_cog.toke(ctx) # TokeCog.toke sends its own messages
            else:
                await ctx.send("Toke feature is not available.", delete_after=10)
            try: await reaction.remove(user)
            except (discord.Forbidden, discord.NotFound): pass
            return
        else: # Not a relevant reaction for this menu
            return

        if new_page != current_page:
            session["current_page"] = new_page
            new_chunk = media_list[new_page * chunk_size : (new_page + 1) * chunk_size]
            new_embed = self._create_media_embed(new_chunk, new_page, total_pages)
            try:
                await message_object.edit(embed=new_embed)
            except discord.NotFound:
                logging.warning(f"Failed to edit media list message {message_object.id}, it might have been deleted.")
                if message_id in self.pagination_sessions:
                    del self.pagination_sessions[message_id]
                return
            except discord.Forbidden:
                logging.error(f"Bot lacks permissions to edit media list message {message_object.id}.")
                return

        try:
            await reaction.remove(user)
        except (discord.Forbidden, discord.NotFound):
            logging.warning(f"Could not remove reaction for user {user.id} on media list message {message_id}.")
            pass