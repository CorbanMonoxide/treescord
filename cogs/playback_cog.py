# playback_cog.py
import discord
from discord.ext import commands
import vlc
import logging
import asyncio
import defusedxml.ElementTree as ET
from urllib.parse import unquote
import os
import yt_dlp

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

    async def play_media(self, ctx, title, file_or_url_path):
        if not self.media_player:
            await ctx.send("Error: Media player is not initialized.")
            return

        try:
            logging.info(f"Attempting to play media: {title}, Path/URL: {file_or_url_path}")
            if self.media_player.is_playing() or self.media_player.get_state() == vlc.State.Paused:
                self.media_player.stop()
                logging.info("Stopped previous media.")

            media = self.instance.media_new(file_or_url_path)
            if not media:
                await ctx.send(f"Error: Failed to load media: {file_or_url_path}")
                logging.error(f"VLC media_new failed for: {file_or_url_path}")
                return

            self.media_player.set_media(media)
            media.release() # Release media object after setting it to player

            # Re-asserting fullscreen can cause flashes. It's set once in cog_load.
            # self.media_player.set_fullscreen(1)

            play_success = self.media_player.play()
            if play_success == -1:
                await ctx.send(f"Error: Failed to start playback for: {title}")
                logging.error(f"media_player.play() failed for {title} - {file_or_url_path}")
                PlaybackCog.playing = False
                return
            PlaybackCog.playing = True
            await ctx.send(f'Playing: {title}')
            self.last_ctx = ctx # store the context.
            
            # Start monitoring playback in the background
            self.bot.loop.create_task(self.monitor_playback(ctx, title))

        except Exception as e:
            logging.error(f"Error playing media {title}: {e}", exc_info=True)
            await ctx.send(f"Error playing media: {e}")

    async def monitor_playback(self, ctx, title):
        """Background task to wait for media to finish."""
        try:
            # Wait for VLC to actually start playing (sometimes takes a split second)
            await asyncio.sleep(1) 
            
            # Audio track selection
            audio_track_id = -1
            selected_audio_track_name = "Default"
            try:
                descriptions = self.media_player.audio_get_track_description() # Call without arguments
                logging.info(f"Available audio tracks: {descriptions}")
                if descriptions:
                    for track_id_val, track_name_bytes in descriptions:
                        track_name_str = track_name_bytes.decode('utf-8', errors='ignore') if track_name_bytes else ""
                        if track_name_str and "english" in track_name_str.lower():
                            audio_track_id = track_id_val
                            selected_audio_track_name = track_name_str
                            logging.info(f"Selected English audio track: ID {track_id_val}, Name {track_name_str}")
                            break
                    # Fallback: if no English track, and tracks are available, select the first one (excluding 'Disable' if present)
                    if audio_track_id == -1 and descriptions:
                        for track_id_val, track_name_bytes in descriptions:
                            if track_id_val != -1: # -1 is often 'Disable'
                                audio_track_id = track_id_val
                                selected_audio_track_name = track_name_bytes.decode('utf-8', errors='ignore') if track_name_bytes else "Unknown"
                                logging.info(f"No English audio track. Selected first available: ID {audio_track_id}, Name {selected_audio_track_name}")
                                break
            except Exception as e:
                logging.error(f"Error processing audio track descriptions: {e}", exc_info=True)

            # Subtitle track selection
            subtitle_track_id = -1
            selected_subtitle_track_name = "None"
            forced_english_track_id = -1
            forced_english_track_name = ""
            try:
                descriptions = self.media_player.video_get_spu_description() # Call without arguments
                logging.info(f"Available subtitle tracks: {descriptions}")
                if descriptions:
                    for track_id_val, track_name_bytes in descriptions:
                        track_name_str = track_name_bytes.decode('utf-8', errors='ignore') if track_name_bytes else ""
                        if track_name_str:
                            track_name_lower = track_name_str.lower()
                            if "english" in track_name_lower:
                                if "forced" in track_name_lower:
                                    # Store forced English track in case no other English track is found
                                    if forced_english_track_id == -1: # Only take the first forced one
                                        forced_english_track_id = track_id_val
                                        forced_english_track_name = track_name_str
                                        logging.info(f"Found Forced English subtitle track: ID {track_id_val}, Name {track_name_str}")
                                else:
                                    # Prefer non-forced English track
                                    subtitle_track_id = track_id_val
                                    selected_subtitle_track_name = track_name_str
                                    logging.info(f"Selected non-Forced English subtitle track: ID {track_id_val}, Name {track_name_str}")
                                    break # Found a preferred English track
                    if subtitle_track_id == -1 and forced_english_track_id != -1:
                        # If no non-forced English track was found, use the forced one
                        subtitle_track_id = forced_english_track_id
                        selected_subtitle_track_name = forced_english_track_name
                        logging.info(f"Using Forced English subtitle track as fallback: ID {subtitle_track_id}, Name {selected_subtitle_track_name}")
            except Exception as e:
                logging.error(f"Error processing subtitle track descriptions: {e}", exc_info=True)

            if audio_track_id != -1:
                self.media_player.audio_set_track(audio_track_id)
                logging.info(f"Audio track set to {audio_track_id}")

            if subtitle_track_id != -1:
                self.media_player.video_set_spu(subtitle_track_id)
                logging.info(f"Subtitle track set to {subtitle_track_id}")

            while self.media_player.get_state() not in [vlc.State.Ended, vlc.State.Error, vlc.State.Stopped]:
                await asyncio.sleep(1)
            
            logging.info(f"Playback loop finished. State: {self.media_player.get_state()}")

            if self.media_player.get_state() == vlc.State.Ended:
                playlist_cog = self.bot.get_cog('PlaylistCog')
                if playlist_cog:
                    # This is now safe because we are in a separate task, not the recursion stack
                    await playlist_cog.play_next(ctx)
                    
        except Exception as e:
            logging.error(f"Error in monitor_playback for {title}: {e}")
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

        media_library = await database_cog.get_media_library()
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

    async def get_youtube_info(self, url):
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
        }
        try:
            logging.info(f"yt-dlp: Attempting to extract info for {url}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = await asyncio.to_thread(ydl.extract_info, url, download=False)
                video_url = info.get('url')
                title = info.get('title', 'Unknown YouTube Video')

                if not video_url:
                    logging.error(f"yt-dlp: Could not extract 'url' directly from info for {url} using primary format. Checking 'formats' list as fallback.")
                    
                    selected_format_info = None
                    if 'formats' in info:
                        # Priority 1: MP4 with video and audio
                        for f_info in reversed(info['formats']):
                            if f_info.get('url','').startswith('http') and \
                               f_info.get('vcodec') != 'none' and f_info.get('vcodec') is not None and \
                               f_info.get('acodec') != 'none' and f_info.get('acodec') is not None and \
                               f_info.get('ext') == 'mp4':
                                selected_format_info = f_info
                                break
                        
                        # Priority 2: Any format with video and audio
                        if not selected_format_info:
                            for f_info in reversed(info['formats']):
                                if f_info.get('url','').startswith('http') and \
                                   f_info.get('vcodec') != 'none' and f_info.get('vcodec') is not None and \
                                   f_info.get('acodec') != 'none' and f_info.get('acodec') is not None:
                                    selected_format_info = f_info
                                    break
                        
                        # Priority 3: As a last resort for audio, pick any format with audio, even if audio-only.
                        # This might be less desirable if video is expected, but ensures audio if the above fail.
                        if not selected_format_info:
                            for f_info in reversed(info['formats']):
                                if f_info.get('url','').startswith('http') and \
                                   f_info.get('acodec') != 'none' and f_info.get('acodec') is not None:
                                    selected_format_info = f_info
                                    logging.warning(f"yt-dlp: Fallback selected a format that might be audio-only to ensure audio presence: {f_info.get('format_id')}")
                                    break
                    
                    if selected_format_info:
                        video_url = selected_format_info.get('url')
                        title = info.get('title', selected_format_info.get('title', 'Unknown YouTube Video')) # Keep original title if possible
                        logging.info(f"yt-dlp: Using fallback format. URL: {video_url} (Format ID: {selected_format_info.get('format_id')}, vcodec: {selected_format_info.get('vcodec')}, acodec: {selected_format_info.get('acodec')})")
                
                if not video_url:
                    logging.error(f"yt-dlp: Failed to get a streamable URL for {url}.")
                    return None, "Failed to get a streamable URL from YouTube."

                logging.info(f"yt-dlp: Extracted title='{title}', url='{video_url}'")
                return title, video_url
        except yt_dlp.utils.DownloadError as e:
            logging.error(f"yt-dlp DownloadError for {url}: {e}")
            error_message = str(e)
            user_friendly_error = "Could not process YouTube link (video may be unavailable, private, or region-locked)."
            if "is not available" in error_message or "Private video" in error_message or "Video unavailable" in error_message:
                pass # Default message is good
            return None, user_friendly_error
        except Exception as e:
            logging.error(f"yt-dlp: Unexpected error for {url}: {e}", exc_info=True)
            return None, "An unexpected error occurred while fetching YouTube video information."

    @commands.command(brief="Plays a media playlist file or YouTube URL ▶️.", aliases=['p'])
    async def play(self, ctx, *, media_input: str = None):
        try:
            if not media_input:
                await ctx.send("Usage: `!play <XSPF_playlist_name_or_number | YouTube_URL>`")
                return

            playlist_cog = self.bot.get_cog('PlaylistCog')
            if not playlist_cog:
                await ctx.send("Error: Playlist cog not loaded.")
                return

            # Stop any current playback before clearing playlist and loading new media.
            if self.media_player and (self.media_player.is_playing() or self.media_player.get_state() == vlc.State.Paused):
                self.media_player.stop()
                logging.info("Stopped current playback due to new !play command.")

            playlist_cog.shared_playlist.clear()
            playlist_cog.original_playlist.clear()
            playlist_cog.current_index = 0 # Reset index for the new playlist
            playlist_cog.shuffled = False
            self.last_ctx = ctx # store the context.

            # Check if input is a YouTube URL
            if "youtube.com/" in media_input or "youtu.be/" in media_input:
                processing_msg = await ctx.send(f"⏳ Fetching YouTube video: <{media_input}>...")
                title, stream_url_or_error = await self.get_youtube_info(media_input)
                
                if title and stream_url_or_error and stream_url_or_error.startswith('http'): # Successfully got URL
                    playlist_cog.shared_playlist.append((title, stream_url_or_error))
                    await processing_msg.edit(content=f"✅ Added '{title}' to playlist from YouTube.")
                    await self.play_media(ctx, title, stream_url_or_error) # current_index is 0
                else: # stream_url_or_error contains the error message
                    error_detail = stream_url_or_error if isinstance(stream_url_or_error, str) else "Could not play YouTube video. Check logs."
                    await processing_msg.edit(content=f"❌ Error: {error_detail}")
                return
            else: # Existing XSPF playlist logic
                file_path = await self.get_playlist_from_input(ctx, media_input)
                if not file_path: # get_playlist_from_input sends its own message
                    return

                media_files = parse_xspf(file_path)
                if not media_files:
                    await ctx.send(f"Error: No valid media files found in XSPF playlist: {media_input}")
                    return

                for title, media_file_path_item in media_files:
                    playlist_cog.shared_playlist.append((title, media_file_path_item))
                
                if not playlist_cog.shared_playlist:
                    await ctx.send(f"Playlist '{media_input}' is empty or could not be loaded.")
                    return
                
                await ctx.send(f"Added {len(media_files)} items to playlist from '{media_input}'.")
                first_title, first_file_path = playlist_cog.shared_playlist[0] # current_index is 0
                await self.play_media(ctx, first_title, first_file_path)

        except Exception as e:
            logging.error(f"General Error in play command: {e}", exc_info=True)
            await ctx.send(f'Error in play command: {e}')

    @commands.command(brief="Pauses and unpauses the current playback ⏯️.", aliases=['pa'])
    async def pause(self, ctx):
        await self._handle_playback_command(ctx, self.media_player.pause, "Playback paused ⏸️." if self.media_player.is_playing() else "Playback resumed▶️.")

    @commands.command(brief="Stops the current playback 🛑.", aliases=['s'])
    async def stop(self, ctx):
        await self._handle_playback_command(ctx, self.media_player.stop, "Playback stopped 🛑.")

    @commands.command(brief="Skips forward by a specified number of seconds (default 5) ⏩.", aliases=['ff', 'fwd'])
    async def forward(self, ctx, seconds: int = 5):
        if not self.media_player:
             await ctx.send("Media player not initialized.")
             return
        
        current_time = self.media_player.get_time()
        if current_time == -1:
             await ctx.send("Nothing is playing right now.")
             return
        
        new_time = current_time + (seconds * 1000)
        length = self.media_player.get_length()
        
        if length > 0 and new_time > length:
            new_time = length - 1000 # Cap at 1 second before end
        
        self.media_player.set_time(new_time)
        await ctx.send(f"Skipped forward {seconds} seconds ⏩.")

    @commands.command(brief="Rewinds by a specified number of seconds (default 5) ⏪.", aliases=['rw', 'rew'])
    async def rewind(self, ctx, seconds: int = 5):
        if not self.media_player:
             await ctx.send("Media player not initialized.")
             return

        current_time = self.media_player.get_time()
        if current_time == -1:
             await ctx.send("Nothing is playing right now.")
             return

        new_time = current_time - (seconds * 1000)
        
        if new_time < 0:
            new_time = 0
            
        self.media_player.set_time(new_time)
        await ctx.send(f"Rewound {seconds} seconds ⏪.")

    @commands.command(brief="Show current playback status and progress 🎮.")
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