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


