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
        self.current_index = 0
        self.shuffled = False
        self.first_next = False  # flag to track first next call.

    @commands.command(brief="Displays the current playlist.", aliases=['pl'])
    async def playlist(self, ctx):
        """
        Displays the current playlist with pagination and an exit button.
        The currently playing video is shown first.
        """
        if not self.shared_playlist:
            await ctx.send("The shared playlist is empty.")
            return

        playlist_display = []
        if 0 <= self.current_index < len(self.shared_playlist):
            current_title, _ = self.shared_playlist[self.current_index]
            playlist_display.append(f"**Currently Playing:** {current_title}")

            # Display the rest of the playlist starting from the next item
            for i in range(self.current_index + 1, len(self.shared_playlist)):
                title, _ = self.shared_playlist[i]
                playlist_display.append(f"{i + 1}. {title}")

            # Display the items before the currently playing item
            for i in range(0, self.current_index):
                title, _ = self.shared_playlist[i]
                playlist_display.append(f"{i + 1}. {title}")

        chunk_size = 10  # Number of items per page
        chunks = [playlist_display[i:i + chunk_size] for i in range(0, len(playlist_display), chunk_size)]
        current_page = 0

        if not chunks:  # Check if chunks is empty.
            await ctx.send("The playlist is empty or could not be displayed.")
            return

        async def update_message(page):
            if not chunks:
                return discord.Embed(title="Shared Playlist", description="Playlist is empty")
            playlist_str = "\n".join(chunks[page])
            embed = discord.Embed(title="Shared Playlist", description=playlist_str)
            embed.set_footer(text=f"Page {page + 1}/{len(chunks)}")
            return embed

        embed = await update_message(current_page)
        message = await ctx.send(embed=embed)

        if len(chunks) > 1:
            await message.add_reaction("⬅️")
            await message.add_reaction("➡️")
            await message.add_reaction("❌")  # exit button.
        else:
            await message.add_reaction("❌")  # exit button if only one page.

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
                self.current_index += 1  # Increment the index.

                if self.current_index < len(self.shared_playlist):
                    playback_cog = self.bot.get_cog('PlaybackCog')
                    if playback_cog:
                        title, file_path = self.shared_playlist[self.current_index]
                        logging.info(f"Playing next file: {file_path}")
                        await playback_cog.play_media(ctx, title, file_path)  # use play_media.
                    else:
                        await ctx.send("Playback cog not loaded.")
                else:
                    self.current_index = 0  # reset current index to 0.
                    await ctx.send("End of playlist, starting from the beginning.")
                    logging.info("End of playlist reached, starting from the beginning.")

            else:
                await ctx.send("The shared playlist is empty.")
                logging.info("Playlist is empty.")
        except Exception as e:
            logging.error(f'Error in next command: {e}')
            await ctx.send(f'Error in next command: {e}')

    @commands.command(brief="Plays the previous media file in the playlist.")
    async def previous(self, ctx):
        try:
            logging.info(f"Previous command called. Current index: {self.current_index}, Playlist length: {len(self.shared_playlist)}")
            if self.shared_playlist:
                self.current_index -= 1  # Decrement the index.

                if self.current_index >= 0:
                    playback_cog = self.bot.get_cog('PlaybackCog')
                    if playback_cog:
                        title, file_path = self.shared_playlist[self.current_index]
                        logging.info(f"Playing previous file: {file_path}")
                        await playback_cog.play_media(ctx, title, file_path)  # use play_media.
                    else:
                        await ctx.send("Playback cog not loaded.")
                else:
                    self.current_index = len(self.shared_playlist) - 1  # loop to the end of the playlist.
                    await ctx.send("Beginning of playlist, looping to the end.")
                    logging.info("Beginning of playlist reached, looping to the end.")

            else:
                await ctx.send("The shared playlist is empty.")
                logging.info("Playlist is empty.")
        except Exception as e:
            logging.error(f'Error in previous command: {e}')
            await ctx.send(f'Error in previous command: {e}')

    @commands.command(brief="Pick a number, any number.")
    async def jump(self, ctx, index: int = None):
        if index is None:
            await ctx.send(self.jump.brief)
            return

        try:
            if 1 <= index <= len(self.shared_playlist):
                self.current_index = index - 1
                playback_cog = self.bot.get_cog('PlaybackCog')
                if playback_cog:
                    title, file_path = self.shared_playlist[self.current_index]
                    logging.info(f"Jumping to file at index {index}: {file_path}")
                    await playback_cog.play_media(ctx, title, file_path)
                else:
                    await ctx.send("Playback cog not loaded.")
            else:
                await ctx.send(f"Invalid index. Please provide a number between 1 and {len(self.shared_playlist)}.")
        except ValueError:
            await ctx.send("Invalid input. Please provide a valid integer index.")
        except Exception as e:
            logging.error(f'Error in jump command: {e}')
            await ctx.send(f'Error in jump command: {e}')

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
        self.current_index = 0 # change to 0 from -1.
        self.shuffled = True
        await ctx.send("🔀 Playlist shuffled!")

    @commands.command(brief="Restores original playlist order")
    async def unshuffle(self, ctx):
        """Restores the playlist to its pre-shuffle order, maintaining current playback position"""
        if not self.original_playlist:
            await ctx.send("No original order to restore!")
            return

        if self.shuffled:
            # Find current item in original playlist
            if 0 <= self.current_index < len(self.shared_playlist):
                current_item = self.shared_playlist[self.current_index]
                try:
                    self.current_index = self.original_playlist.index(current_item)
                except ValueError:
                    self.current_index = -1  # if current item is not found.
            else:
                self.current_index = -1

            self.shared_playlist = deepcopy(self.original_playlist)
            self.shuffled = False
            await ctx.send("⏮️ Original playlist restored!")
        else:
            await ctx.send("Playlist is not currently shuffled.")