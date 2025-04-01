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
    playing = False

    def __init__(self, bot, instance):
        self.bot = bot
        self.instance = instance
        self.media_player = None
        self.last_ctx = None # store the last context.

    async def cog_load(self):
        self.media_player = self.instance.media_player_new()
        self.media_player.set_fullscreen(1)

    async def cog_unload(self):
        if self.media_player:
            self.media_player.stop()

    async def play_media(self, ctx, title, file_path):
        if not self.media_player:
            await ctx.send("Error: Media player is not initialized.")
            return

        try:
            logging.info(f"Playing media: {title}, {file_path}")
            if self.media_player.is_playing():
                self.media_player.stop()

            media = self.instance.media_new(file_path)
            if not media:
                await ctx.send(f"Error: Failed to load media file: {file_path}")
                return

            self.media_player.set_media(media)
            self.media_player.play()
            PlaybackCog.playing = True
            await ctx.send(f'Playing: {title}')
            self.last_ctx = ctx # store the context.

            audio_track_id = -1
            subtitle_track_id = -1

            logging.info(f"Audio track count: {self.media_player.audio_get_track_count()}")
            for track in range(self.media_player.audio_get_track_count()):
                try:
                    description = self.media_player.audio_get_track_description(track)
                    logging.info(f"Audio track {track} description: {description}")
                    if description and description[1] and "english" in description[1].lower():
                        audio_track_id = description[0]
                        break
                except Exception as e:
                    logging.error(f"Error getting audio track description: {e}")

            logging.info(f"Subtitle track count: {self.media_player.video_get_spu_count()}")
            for track in range(self.media_player.video_get_spu_count()):
                try:
                    description = self.media_player.video_get_spu_description(track)
                    logging.info(f"Subtitle track {track} description: {description}")
                    if description and description[1] and "english" in description[1].lower():
                        subtitle_track_id = description[0]
                        break
                except Exception as e:
                    logging.error(f"Error getting subtitle track description: {e}")

            if audio_track_id != -1:
                self.media_player.audio_set_track(audio_track_id)
                logging.info(f"Audio track set to {audio_track_id}")

            if subtitle_track_id != -1:
                self.media_player.video_set_spu(subtitle_track_id)
                logging.info(f"Subtitle track set to {subtitle_track_id}")

            while self.media_player.is_playing():
                await asyncio.sleep(1)

            # Check if playback ended naturally
            if self.media_player.get_state() == vlc.State.Ended:
                playlist_cog = self.bot.get_cog('PlaylistCog')
                if playlist_cog:
                    await playlist_cog.play_next(ctx)

        except Exception as e:
            logging.error(f"Playback Error: {e}")
            await ctx.send(f'Error playing: {e}')
        finally:
            PlaybackCog.playing = False

    def format_time(self, milliseconds):
        seconds = milliseconds // 1000
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}" if hours else f"{minutes:02d}:{seconds:02d}"

    async def _handle_playback_command(self, ctx, action, message):
        if not self.media_player:
            await ctx.send("Error: Media player is not initialized.")
            return

        try:
            action()
            await ctx.send(message)
        except Exception as e:
            logging.error(f"Playback Command Error: {e}")
            await ctx.send(f'Error: {e}')

    async def get_playlist_from_input(self, ctx, playlist_input):
        database_cog = self.bot.get_cog('DatabaseCog')
        if not database_cog:
            await ctx.send("Error: Database cog not loaded.")
            return None

        media_library = database_cog.get_media_library()
        keys = list(media_library.keys())

        try:
            index = int(playlist_input) - 1
            if 0 <= index < len(keys):
                return media_library[keys[index]]
            else:
                await ctx.send(f"Invalid playlist number. Please provide a number between 1 and {len(keys)}.")
                return None
        except ValueError:
            if playlist_input in media_library:
                return media_library[playlist_input]
            else:
                await ctx.send(f"Playlist '{playlist_input}' not found.")
                return None

    @commands.command(brief="Plays a media playlist file.", aliases=['p'])
    async def play(self, ctx, *, playlist_input: str = None):
        try:
            if not playlist_input:
                await ctx.send("Error: Please specify a playlist name or number.")
                return

            file_path = await self.get_playlist_from_input(ctx, playlist_input)
            if not file_path:
                return

            if not file_path.endswith('.xspf'):
                await ctx.send("Error: Only playlist files (.xspf) are supported.")
                return

            media_files = parse_xspf(file_path)
            if not media_files:
                await ctx.send("Error: No valid media files found in playlist.")
                return

            playlist_cog = self.bot.get_cog('PlaylistCog')
            if not playlist_cog:
                await ctx.send("Error: Playlist cog not loaded.")
                return

            # Clear the current playlist before adding new items.
            playlist_cog.shared_playlist.clear()
            playlist_cog.original_playlist.clear()
            playlist_cog.current_index = 0
            playlist_cog.shuffled = False
            self.last_ctx = ctx # store the context.

            for title, media_file in media_files:
                playlist_cog.shared_playlist.append((title, media_file))
            await ctx.send(f"Added {len(media_files)} items to playlist.")

            if playlist_cog.shared_playlist:
                title, file_path = playlist_cog.shared_playlist[0]
                await self.play_media(ctx, title, file_path)
                playlist_cog.current_index = 0

        except Exception as e:
            logging.error(f"General Error: {e}")
            await ctx.send(f'Error: {e}')

    @commands.command(brief="Pauses the current playback ⏸️.", aliases=['pa'])
    async def pause(self, ctx):
        await self._handle_playback_command(ctx, self.media_player.pause, "Playback paused ⏸️." if self.media_player.is_playing() else "Playback resumed.")

    @commands.command(brief="Stops the current playback 🛑.", aliases=['s'])
    async def stop(self, ctx):
        await self._handle_playback_command(ctx, self.media_player.stop, "Playback stopped 🛑.")

    @commands.command(brief="Show current playback status and progress.")
    async def status(self, ctx):
        if not self.media_player or not self.media_player.get_media() or (not self.media_player.is_playing() and not self.media_player.is_paused()):
            await ctx.send("Error: Nothing is currently playing.")
            return

        try:
            media = self.media_player.get_media()
            current_time_ms = self.media_player.get_time()
            total_time_ms = self.media_player.get_length()

            if total_time_ms <= 0:
                await ctx.send("Error: Hmm very difficult to determine.")
                return

            progress_percent = (current_time_ms / total_time_ms) * 100
            bar_length = 20
            filled_length = int(bar_length * current_time_ms // total_time_ms)
            progress_bar = '▓' * filled_length + '░' * (bar_length - filled_length)
            state = "Playing" if self.media_player.is_playing() else "Paused"
            volume = self.media_player.audio_get_volume()
            title = media.get_meta(vlc.Meta.Title) or "Unknown"

            embed = discord.Embed(title="Playback Status", color=0x3498db)
            embed.add_field(name="Media", value=title, inline=False)
            embed.add_field(name="Status", value=state, inline=True)
            embed.add_field(name="Volume", value=f"{volume}%", inline=True)
            embed.add_field(name="Progress", value=f"{self.format_time(current_time_ms)} / {self.format_time(total_time_ms)} ({progress_percent:.1f}%)", inline=False)
            embed.add_field(name="Progress Bar", value=f"`{progress_bar}`", inline=False)
            await ctx.send(embed=embed)
        except Exception as e:
            logging.error(f"Error displaying status: {e}")
            await ctx.send(f"Error displaying status: {e}")