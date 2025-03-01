# playback_cog.py
import discord
from discord.ext import commands
import vlc
import logging
import asyncio

class PlaybackCog(commands.Cog):
    def __init__(self, bot, instance):
        self.bot = bot
        self.instance = instance
        self.media_list = instance.media_list_new()
        self.media_list_player = instance.media_list_player_new()
        self.media_list_player.set_media_list(self.media_list)
        self.media_list_player.get_media_player().set_fullscreen(1)

    @commands.command(brief="Plays a media file.")
    async def play(self, ctx, *, media_name: str):
        try:
            database_cog = self.bot.get_cog('DatabaseCog')
            if database_cog:
                media_library = database_cog.get_media_library()
                file_path = media_library.get(media_name)
                if file_path:
                    if self.media_list_player and self.media_list_player.is_playing() == 1:
                        self.media_list_player.stop()
                        await asyncio.sleep(1)

                    self.media_list = self.instance.media_list_new()
                    self.media_list_player.set_media_list(self.media_list)

                    media = self.instance.media_new(file_path)
                    self.media_list.add_media(media)

                    try:
                        self.media_list_player.play()
                    except Exception as play_error:
                        logging.error(f"Play Error: {play_error}")
                        await ctx.send("Play Error.")
                        return

                    logging.info(f"VLC state: {self.media_list_player.get_state()}")
                    await ctx.send(f'Playing: {media_name}')
                else:
                    await ctx.send(f"Media '{media_name}' not found.")
            else:
                await ctx.send("Database cog not loaded.")

        except Exception as e:
            logging.error(f"General Error: {e}")
            await ctx.send(f'Error playing: {e}')

    @commands.command(brief="Pauses the current playback.")
    async def pause(self, ctx):
        try:
            self.media_list_player.pause()
            logging.info("Playback Paused.")
            await ctx.send("Playback Paused.")
        except Exception as e:
            logging.error(f'Error: {e}')
            await ctx.send(f'Error: {e}')

    @commands.command(brief="Stops the current playback.")
    async def stop(self, ctx):
        try:
            self.media_list_player.stop()
            logging.info("Playback Stopped.")
            await ctx.send("Playback Stopped.")
        except Exception as e:
            logging.error(f'Error: {e}')
            await ctx.send(f'Error: {e}')