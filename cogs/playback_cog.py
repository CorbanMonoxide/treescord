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

def format_time(self, milliseconds):
    """Format milliseconds into HH:MM:SS format."""
    seconds = milliseconds // 1000
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"

class PlaybackCog(commands.Cog):
    def __init__(self, bot, instance):
        self.bot = bot
        self.instance = instance
        self.media_player = instance.media_player_new()
        self.media_player.set_fullscreen(1)

    async def play_media(self, ctx, title, file_path):
        try:
            if self.media_player.is_playing():
                self.media_player.stop()
            media = self.instance.media_new(file_path)
            self.media_player.set_media(media)
            self.media_player.play()
            await ctx.send(f'Playing: {title}')
        except Exception as e:
            logging.error(f"Playback Error: {e}")
            await ctx.send(f'Error playing: {e}')

    @commands.command(brief="Plays a media file or playlist.")
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
                                await ctx.send("No valid media files found in playlist.")
                                return
                            playlist_cog = self.bot.get_cog('PlaylistCog')
                            if playlist_cog:
                                for title, media_file in media_files:
                                    playlist_cog.shared_playlist.append((title, media_file))
                                await ctx.send(f"Added {len(media_files)} items to playlist.")
                                if playlist_cog.shared_playlist:
                                    title, file_path = playlist_cog.shared_playlist[0]
                                    await self.play_media(ctx, title, file_path)
                            else:
                                await ctx.send("Playlist cog not loaded.")
                        else:
                            await self.play_media(ctx, media_name, file_path)
                    else:
                        await ctx.send(f"Media '{media_name}' not found.")
                else:
                    await ctx.send("Database cog not loaded.")
            else:
                await ctx.send("Please specify a media file or playlist.")
        except Exception as e:
            logging.error(f"General Error: {e}")
            await ctx.send(f'Error: {e}')

    @commands.command(brief="Pauses the current playback.")
    async def pause(self, ctx):
        try:
            self.media_player.pause()
            await ctx.send("Playback paused." if self.media_player.is_playing() else "Playback resumed.")
        except Exception as e:
            logging.error(f'Error: {e}')
            await ctx.send(f'Error: {e}')

    @commands.command(brief="Stops the current playback.")
    async def stop(self, ctx):
        try:
            self.media_player.stop()
            await ctx.send("Playback stopped.")
        except Exception as e:
            logging.error(f'Error: {e}')
            await ctx.send(f'Error: {e}')

    @commands.command(brief="Skip forward by specified seconds.")
    async def forward(self, ctx, seconds: int = 10):
        try:
            if not self.media_player.is_playing():
                await ctx.send("Nothing is currently playing.")
                return
            
            current_time = self.media_player.get_time()  # Current time in ms
            new_time = current_time + (seconds * 1000)   # Convert seconds to ms
            self.media_player.set_time(new_time)
            await ctx.send(f"Skipped forward {seconds} seconds.")
        except Exception as e:
            logging.error(f"Error seeking forward: {e}")
            await ctx.send(f"Error seeking forward: {e}")

    @commands.command(brief="Skip backward by specified seconds.")
    async def backward(self, ctx, seconds: int = 10):
        try:
            if not self.media_player.is_playing():
                await ctx.send("Nothing is currently playing.")
                return
                
            current_time = self.media_player.get_time()  # Current time in ms
            new_time = max(0, current_time - (seconds * 1000))  # Ensure we don't go below 0
            self.media_player.set_time(new_time)
            await ctx.send(f"Skipped backward {seconds} seconds.")
        except Exception as e:
            logging.error(f"Error seeking backward: {e}")
            await ctx.send(f"Error seeking backward: {e}")


    @commands.command(brief="Jump to a specific timestamp (MM:SS or HH:MM:SS).")
    async def jump(self, ctx, timestamp: str):
        try:
            if not self.media_player.is_playing():
                await ctx.send("Nothing is currently playing.")
                return
            
            # Parse the timestamp
            parts = timestamp.split(':')
            total_seconds = 0
            
            if len(parts) == 2:  # MM:SS format
                total_seconds = int(parts[0]) * 60 + int(parts[1])
            elif len(parts) == 3:  # HH:MM:SS format
                total_seconds = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            else:
                await ctx.send("Invalid timestamp format. Use MM:SS or HH:MM:SS.")
                return
            
            # Set the time in milliseconds
            self.media_player.set_time(total_seconds * 1000)
            await ctx.send(f"Jumped to {timestamp}.")
        except ValueError:
            await ctx.send("Invalid timestamp format. Use numbers in MM:SS or HH:MM:SS format.")
        except Exception as e:
            logging.error(f"Error jumping to timestamp: {e}")
            await ctx.send(f"Error jumping to timestamp: {e}")

    @commands.command(brief="Show current playback status and progress.")
    async def status(self, ctx):
        try:
            if not self.media_player.is_playing() and not self.media_player.is_paused():
                await ctx.send("Nothing is currently playing.")
                return
            
            # Get current media information
            media = self.media_player.get_media()
            current_time_ms = self.media_player.get_time()
            total_time_ms = self.media_player.get_length()
            
            if total_time_ms <= 0:
                await ctx.send("Unable to determine media duration.")
                return
            
            # Calculate progress percentage
            progress_percent = (current_time_ms / total_time_ms) * 100
            
            # Create a progress bar (20 characters wide)
            bar_length = 20
            filled_length = int(bar_length * current_time_ms // total_time_ms)
            progress_bar = '█' * filled_length + '░' * (bar_length - filled_length)
            
            # Get the current playback state
            state = "Playing" if self.media_player.is_playing() else "Paused"
            
            # Get the current volume
            volume = self.media_player.audio_get_volume()
            
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

