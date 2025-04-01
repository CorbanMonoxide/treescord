# playback_cog.py
import discord
from discord.ext import commands
import vlc
import logging
import asyncio
import xml.etree.ElementTree as ET
from urllib.parse import unquote
import os

def parse_xspf(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    namespace = {'xspf': 'http://xspf.org/ns/0/'}
    media_files = []

    for track in root.findall('.//xspf:track', namespace):
        location = track.find('xspf:location', namespace)
        file_path = unquote(location.text) if location is not None and location.text else None
        title = track.find('xspf:title', namespace)
        title = title.text if title is not None else os.path.basename(file_path)
        if file_path:
            media_files.append((title, file_path))
    return media_files

class PlaybackCog(commands.Cog):
    media_player = None  # Class-level attribute for the VLC media player
    playing = False # class level flag to track playing state.

    def __init__(self, bot, instance):
        self.bot = bot
        self.instance = instance
        if PlaybackCog.media_player is None:  # Create the VLC instance only once
            PlaybackCog.media_player = instance.media_player_new()
            PlaybackCog.media_player.set_fullscreen(1)

    async def play_media(self, ctx, title, file_path):
        try:
            if PlaybackCog.media_player is None:
                await ctx.send("Error: Media player is not initialized.")
                return

            if PlaybackCog.media_player.is_playing():
                PlaybackCog.media_player.stop()

            media = self.instance.media_new(file_path)
            if media is None:
                await ctx.send(f"Error: Failed to load media file: {file_path}")
                return

            PlaybackCog.media_player.set_media(media)
            PlaybackCog.media_player.play()
            PlaybackCog.playing = True
            await ctx.send(f'Playing: {title}')

            # Wait for media to finish playing
            while PlaybackCog.media_player.is_playing():
                await asyncio.sleep(1)

            PlaybackCog.playing = False

        except Exception as e:
            logging.error(f"Playback Error: {e}")
            await ctx.send(f'Error playing: {e}')
            PlaybackCog.playing = False

    def format_time(self, milliseconds):
        seconds = milliseconds // 1000
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"

    @commands.command(brief="Plays a media file or playlist.", aliases=['p'])
    async def play(self, ctx, *, media_name: str = None, file_path: str = None):
        try:
            if file_path:
                await self.play_media(ctx, os.path.basename(file_path), file_path)
            elif media_name:
                database_cog = self.bot.get_cog('DatabaseCog')
                if database_cog:
                    media_library = database_cog.get_media_library()
                    file_path = media_library.get(media_name)
                    if file_path:
                        if file_path.endswith('.xspf'):
                            media_files = parse_xspf(file_path)
                            if not media_files:
                                await ctx.send("Error: No valid media files found in playlist.")
                                return
                            playlist_cog = self.bot.get_cog('PlaylistCog')
                            if playlist_cog:
                                for title, media_file in media_files:
                                    playlist_cog.shared_playlist.append((title, media_file))
                                await ctx.send(f"Added {len(media_files)} items to playlist.")
                                if playlist_cog.shared_playlist:
                                    title, file_path = playlist_cog.shared_playlist[0]
                                    await self.play_media(ctx, title, file_path)
                                    await ctx.invoke(self.bot.get_command('next')) #call next command.
                            else:
                                await ctx.send("Error: Playlist cog not loaded.")
                        else:
                            await self.play_media(ctx, media_name, file_path)
                    else:
                        await ctx.send(f"Error: Media '{media_name}' not found.")
                else:
                    await ctx.send("Error: Database cog not loaded.")
            else:
                await ctx.send("Error: Please specify a media file or playlist.")
        except Exception as e:
            logging.error(f"General Error: {e}")
            await ctx.send(f'Error: {e}')

    @commands.command(brief="Pauses the current playback.", aliases=['pa'])
    async def pause(self, ctx):
        try:
            if PlaybackCog.media_player is None:
                await ctx.send("Error: Media player is not initialized.")
                return
            PlaybackCog.media_player.pause()
            await ctx.send("Playback paused." if PlaybackCog.media_player.is_playing() else "Playback resumed.")
        except Exception as e:
            logging.error(f'Error: {e}')
            await ctx.send(f'Error: {e}')

    @commands.command(brief="Stops the current playback.", aliases=['s'])
    async def stop(self, ctx):
        try:
            if PlaybackCog.media_player is None:
                await ctx.send("Error: Media player is not initialized.")
                return
            PlaybackCog.media_player.stop()
            await ctx.send("Playback stopped.")
        except Exception as e:
            logging.error(f'Error: {e}')
            await ctx.send(f'Error: {e}')

    @commands.command(brief="Show current playback status and progress.")
    async def status(self, ctx):
        try:
            if PlaybackCog.media_player is None or not PlaybackCog.media_player.get_media():
                await ctx.send("Error: Nothing is currently playing.")
                return

            if not PlaybackCog.media_player.is_playing() and not PlaybackCog.media_player.is_paused():
                await ctx.send("Error: Nothing is currently playing.")
                return
            
            # Get current media information
            media = PlaybackCog.media_player.get_media()
            current_time_ms = PlaybackCog.media_player.get_time()
            total_time_ms = PlaybackCog.media_player.get_length()
            
            if total_time_ms <= 0:
                await ctx.send("Error: Unable to determine media duration.")
                return
            
            # Calculate progress percentage
            progress_percent = (current_time_ms / total_time_ms) * 100
            
            # Create a progress bar (20 characters wide)
            bar_length = 20
            filled_length = int(bar_length * current_time_ms // total_time_ms)
            filled_char = '▓' # Using a different filled character.
            empty_char = '░'
            progress_bar = filled_char * filled_length + empty_char * (bar_length - filled_length)
            
            # Get the current playback state
            state = "Playing" if PlaybackCog.media_player.is_playing() else "Paused"
            
            # Get the current volume
            volume = PlaybackCog.media_player.audio_get_volume()
            
            # Get media title if available
            title = media.get_meta(vlc.Meta.Title) or "Unknown"
            
            # Create and send the embed
            embed = discord.Embed(title="Playback Status", color=0x3498db)
            embed.add_field(name="Media", value=title, inline=False)
            embed.add_field(name="Status", value=state, inline=True)
            embed.add_field(name="Volume", value=f"{volume}%", inline=True)
            embed.add_field(name="Progress", 
                            value=f"{self.format_time(current_time_ms)} / {self.format_time(total_time_ms)} ({progress_percent:.1f}%)", 
                            inline=False)
            embed.add_field(name="Progress Bar", value=f"`{progress_bar}`", inline=False)
            
            await ctx.send(embed=embed)
        except Exception as e:
            logging.error(f"Error displaying status: {e}")
            await ctx.send(f"Error displaying status: {e}")