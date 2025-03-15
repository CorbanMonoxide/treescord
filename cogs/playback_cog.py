# playback_cog.py
import discord
from discord.ext import commands
import vlc
import logging
import asyncio
import xml.etree.ElementTree as ET  # For parsing .xspf files
from urllib.parse import unquote  # For decoding URL-encoded file paths

# Function to parse .xspf files
def parse_xspf(file_path):
    """
    Parses a .xspf file and returns a list of tuples containing (title, file_path).
    If the <title> tag is missing, the file name is used as the title.
    """
    tree = ET.parse(file_path)
    root = tree.getroot()
    namespace = {'xspf': 'http://xspf.org/ns/0/'}
    media_files = []

    for track in root.findall('.//xspf:track', namespace):
        # Extract the file path from the <location> tag
        location = track.find('xspf:location', namespace)
        file_path = unquote(location.text) if location is not None and location.text else None

        # Extract the title from the <title> tag
        title = track.find('xspf:title', namespace)
        title = title.text if title is not None else file_path.split('/')[-1]  # Use file name if title is missing

        if file_path:
            media_files.append((title, file_path))

    return media_files

class PlaybackCog(commands.Cog):
    def __init__(self, bot, instance):
        self.bot = bot
        self.instance = instance
        self.media_player = instance.media_player_new()  # Single media player instance
        self.media_player.set_fullscreen(1)

    async def play_media(self, ctx, title, file_path):
        """
        Plays a media file using the existing VLC media player instance.
        """
        try:
            # Stop any currently playing media
            if self.media_player.is_playing():
                self.media_player.stop()

            # Load the new media file
            media = self.instance.media_new(file_path)
            self.media_player.set_media(media)

            # Play the media
            self.media_player.play()
            await ctx.send(f'Playing: {title}')
        except Exception as e:
            logging.error(f"Playback Error: {e}")
            await ctx.send(f'Error playing: {e}')

    @commands.command(brief="Plays a media file or playlist.")
    async def play(self, ctx, *, media_name: str = None, file_path: str = None):
        try:
            if file_path:
                # Play media directly using the file path
                await self.play_media(ctx, file_path.split('/')[-1], file_path)
            elif media_name:
                database_cog = self.bot.get_cog('DatabaseCog')
                if database_cog:
                    media_library = database_cog.get_media_library()
                    file_path = media_library.get(media_name)
                    if file_path:
                        if file_path.endswith('.xspf'):
                            # Parse the .xspf file and add media files to the shared playlist
                            media_files = parse_xspf(file_path)
                            if not media_files:
                                await ctx.send("No valid media files found in the playlist.")
                                return

                            # Add media files to the shared playlist
                            playlist_cog = self.bot.get_cog('PlaylistCog')
                            if playlist_cog:
                                for title, media_file in media_files:
                                    # Add the media file to the shared playlist (no normalization)
                                    playlist_cog.shared_playlist.append((title, media_file))
                                await ctx.send(f"Added {len(media_files)} items to the shared playlist.")
                            else:
                                await ctx.send("Playlist cog not loaded.")
                                return

                            # Play the first item in the playlist
                            if playlist_cog.shared_playlist:
                                title, file_path = playlist_cog.shared_playlist[0]
                                await self.play_media(ctx, title, file_path)
                        else:
                            # Handle single media file
                            await self.play_media(ctx, media_name, file_path)
                    else:
                        await ctx.send(f"Media '{media_name}' not found.")
                else:
                    await ctx.send("Database cog not loaded.")
            else:
                await ctx.send("Please specify a media file or playlist.")
        except Exception as e:
            logging.error(f"General Error: {e}")
            await ctx.send(f'Error playing: {e}')

    @commands.command(brief="Pauses the current playback.")
    async def pause(self, ctx):
        try:
            self.media_player.pause()
            logging.info("Playback Paused.")
            await ctx.send("Playback Paused.")
        except Exception as e:
            logging.error(f'Error: {e}')
            await ctx.send(f'Error: {e}')

    @commands.command(brief="Stops the current playback.")
    async def stop(self, ctx):
        try:
            self.media_player.stop()
            logging.info("Playback Stopped.")
            await ctx.send("Playback Stopped.")
        except Exception as e:
            logging.error(f'Error: {e}')
            await ctx.send(f'Error: {e}')