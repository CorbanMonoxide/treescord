import discord
from discord.ext import commands
import logging
import random
from copy import deepcopy
import asyncio
import vlc # Required for vlc.State

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

    @commands.command(brief="Displays the current playlist📃.", aliases=['pl'])
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
                return discord.Embed(title="Now Playing 🍿", description="Playlist is empty")
            playlist_str = "\n".join(chunks[page])
            embed = discord.Embed(title="Now Playing 🍿", description=playlist_str)
            embed.set_footer(text=f"Page {page + 1}/{len(chunks)}")
            return embed

        embed = await update_message(current_page)
        message = await ctx.send(embed=embed)

        if len(chunks) > 1:
            await message.add_reaction("⬅️")
            await message.add_reaction("➡️")
            await message.add_reaction("❌")  # exit button.
            await message.add_reaction("📱") # Show Remote
            await message.add_reaction("🍃") # Join/Start Toke
        else:
            await message.add_reaction("❌")  # exit button if only one page.
            await message.add_reaction("📱") # Show Remote
            await message.add_reaction("🍃") # Join/Start Toke


        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["⬅️", "➡️", "❌", "📱", "🍃"] and reaction.message.id == message.id

        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
                if str(reaction.emoji) == "➡️":
                    current_page = (current_page + 1) % len(chunks)
                elif str(reaction.emoji) == "⬅️":
                    current_page = (current_page - 1) % len(chunks)
                elif str(reaction.emoji) == "❌":
                    try:
                        await message.delete()
                    except discord.NotFound:
                        logging.warning(f"Playlist message {message.id} already deleted or not found.")
                    return
                elif str(reaction.emoji) == "📱":
                    remote_cog = self.bot.get_cog("RemoteCog")
                    if remote_cog:
                        await remote_cog.create_controller(ctx)
                    else:
                        await ctx.send("Remote controller feature is not available.", delete_after=10)
                    await message.remove_reaction(reaction, user)
                    continue # Continue listening for other reactions on the playlist
                elif str(reaction.emoji) == "🍃":
                    toke_cog = self.bot.get_cog("TokeCog")
                    if toke_cog:
                        await toke_cog.toke(ctx) # TokeCog.toke sends its own messages
                    else:
                        await ctx.send("Toke feature is not available.", delete_after=10)
                    await message.remove_reaction(reaction, user)
                    continue # Continue listening for other reactions

                await message.edit(embed=await update_message(current_page))
                await message.remove_reaction(reaction, user)
            except asyncio.TimeoutError:
                await message.clear_reactions()
                break

    async def play_next(self, ctx):
        try:
            logging.info(f"play_next called. Current index: {self.current_index}, Playlist length: {len(self.shared_playlist)}")
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
            logging.error(f'Error in play_next: {e}')
            await ctx.send(f'Error in play_next: {e}')

    @commands.command(brief="Plays the next media file in the playlist⏭️.")
    async def next(self, ctx):
        await self.play_next(ctx)

    @commands.command(brief="Plays the previous media file in the playlist⏮️.")
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

    @commands.command(brief="Jump to any media file by inputting it's number from the playlist view🦘.")
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

    @commands.command(brief="Adds a YouTube video to the current playlist ➕.", aliases=['q', 'enqueue'])
    async def add(self, ctx, *, youtube_url: str = None):
        if not youtube_url:
            await ctx.send("Usage: `!add <YouTube_URL>`")
            return

        if not ("youtube.com/" in youtube_url or "youtu.be/" in youtube_url):
            await ctx.send("Error: Only YouTube URLs are supported for the `!add` command.")
            return

        playback_cog = self.bot.get_cog('PlaybackCog')
        if not playback_cog:
            await ctx.send("Error: Playback cog not loaded.")
            return
        if not playback_cog.media_player: # Ensure media_player is initialized
            await ctx.send("Error: Media player in PlaybackCog is not initialized.")
            return

        processing_msg = await ctx.send(f"⏳ Fetching YouTube video to add: <{youtube_url}>...")
        title, stream_url_or_error = await playback_cog.get_youtube_info(youtube_url)

        if title and stream_url_or_error and stream_url_or_error.startswith('http'): # Successfully got URL
            self.shared_playlist.append((title, stream_url_or_error))
            # If the original playlist is being used (not shuffled), also add there.
            if not self.shuffled:
                 self.original_playlist.append((title, stream_url_or_error))

            await processing_msg.edit(content=f"✅ Added '{title}' to the playlist.")

            # If nothing is currently playing, start playing the newly added song.
            is_player_idle = playback_cog.media_player.get_state() in [vlc.State.NothingSpecial, vlc.State.Stopped, vlc.State.Ended, vlc.State.Error]
            
            if not playback_cog.playing and is_player_idle:
                logging.info(f"Nothing was playing. Starting playback for newly added: {title}")
                self.current_index = len(self.shared_playlist) - 1 # Set index to the newly added item
                await playback_cog.play_media(ctx, title, stream_url_or_error)
            elif not self.shared_playlist: # If playlist was empty and something was added
                self.current_index = 0
                await playback_cog.play_media(ctx, title, stream_url_or_error)
        else: # stream_url_or_error contains the error message
            error_detail = stream_url_or_error if isinstance(stream_url_or_error, str) else "Could not process YouTube video. Check logs."
            await processing_msg.edit(content=f"❌ Error adding video: {error_detail}")

    @commands.command(brief="Shuffles the playlist🔀.")
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

    @commands.command(brief="Restores original playlist order 🔙.")
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

    @commands.command(brief="Clears the current playlist 🥊.", aliases = ["cl"])
    async def clear(self, ctx):
        """Clears the current playlist."""
        self.shared_playlist.clear()
        self.original_playlist.clear()
        self.current_index = 0
        self.shuffled = False
        playback_cog = self.bot.get_cog('PlaybackCog')
        if playback_cog and playback_cog.media_player:
            playback_cog.media_player.stop()  # Stop playback
        await ctx.send("Playlist cleared 🥊 and playback stopped 🛑.")