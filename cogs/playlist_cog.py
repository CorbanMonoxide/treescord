# playlist_cog.py
import discord
from discord.ext import commands
import logging
import random
from copy import deepcopy
import asyncio

def normalize_media_name(media_name):
    return media_name.lower().strip()

class PlaylistCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.shared_playlist = []
        self.original_playlist = []
        self.current_index = -1

    @commands.command(brief="Views the current playlist.")
    async def view(self, ctx):
        """
        Displays the current playlist with pagination and an exit button.
        """
        if not self.shared_playlist:
            await ctx.send("The shared playlist is empty.")
            return

        chunk_size = 10  # Number of items per page
        chunks = [self.shared_playlist[i:i + chunk_size] for i in range(0, len(self.shared_playlist), chunk_size)]
        current_page = 0

        async def update_message(page):
            start = page * chunk_size
            end = start + chunk_size
            page_items = self.shared_playlist[start:end]
            playlist_str = "\n".join([f"{i + 1 + start}. {name}" for i, (name, _) in enumerate(page_items)])
            embed = discord.Embed(title="Shared Playlist", description=playlist_str)
            embed.set_footer(text=f"Page {page + 1}/{len(chunks)}")
            return embed

        embed = await update_message(current_page)
        message = await ctx.send(embed=embed)

        if len(chunks) > 1:
            await message.add_reaction("⬅️")
            await message.add_reaction("➡️")
            await message.add_reaction("❌") #exit button.
        else:
            await message.add_reaction("❌") #exit button if only one page.

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["⬅️", "➡️", "❌"] and reaction.message.id == message.id

        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)

                if str(reaction.emoji) == "➡️":
                    current_page = (current_page + 1) % len(chunks)
                elif str(reaction.emoji) == "⬅️":
                    current_page = (current_page - 1) % len(chunks)
                elif str(reaction.emoji) == "❌":
                    await message.clear_reactions()
                    return

                await message.edit(embed=await update_message(current_page))
                await message.remove_reaction(reaction, user)
            except asyncio.TimeoutError:
                await message.clear_reactions()
                break

    @commands.command(brief="Plays the next media file in the playlist.")
    async def next(self, ctx):
        try:
            logging.info(f"Next command called. Current index: {self.current_index}, Playlist length: {len(self.shared_playlist)}")
            if self.shared_playlist:
                self.current_index += 1
                if self.current_index < len(self.shared_playlist):
                    playback_cog = self.bot.get_cog('PlaybackCog')
                    if playback_cog:
                        title, file_path = self.shared_playlist[self.current_index]
                        logging.info(f"Playing next file: {file_path}")
                        await playback_cog.play_media(ctx, title, file_path) #use play_media.
                    else:
                        await ctx.send("Playback cog not loaded.")
                else:
                    self.current_index = -1; #reset current index.
                    await ctx.send("End of playlist.")
                    logging.info("End of playlist reached.")

            else:
                await ctx.send("The shared playlist is empty.")
                logging.info("Playlist is empty.")
        except Exception as e:
            logging.error(f'Error in next command: {e}')
            await ctx.send(f'Error in next command: {e}')

    @commands.command(brief="Shuffles the playlist")
    async def shuffle(self, ctx):
        """Shuffles the shared playlist"""
        if not self.shared_playlist:
            await ctx.send("Playlist is empty!")
            return
            
        # Backup original order before first shuffle
        if not self.original_playlist:
            self.original_playlist = deepcopy(self.shared_playlist)
            
        random.shuffle(self.shared_playlist)
        self.current_index = -1
        await ctx.send("🔀 Playlist shuffled!")