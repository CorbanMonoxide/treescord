import discord
from discord.ext import commands
import logging

class VolumeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _get_media_player(self):
        """Helper to get the media player from the PlaybackCog."""
        playback_cog = self.bot.get_cog("PlaybackCog")
        if playback_cog and playback_cog.media_player:
            return playback_cog.media_player
        return None

    @commands.command(brief="Sets the volume level by adding an integer after the command 🔈🔉🔊.")
    async def volume(self, ctx, level: int):
        media_player = self._get_media_player()
        if not media_player:
            await ctx.send("No media player is active.")
            return
        try:
            media_player.audio_set_volume(level)
            logging.info(f"Volume set to {level}")
            await ctx.send(f"Volume set to {level}")
        except Exception as e:
            logging.error(f"Error: {e}")
            await ctx.send(f"Error: {e}")

    @commands.command(brief="Mutes the audio 🔇.")
    async def mute(self, ctx):
        media_player = self._get_media_player()
        if not media_player:
            await ctx.send("No media player is active.")
            return
        try:
            media_player.audio_set_mute(1)
            logging.info("Muted.")
            await ctx.send("Muted🔇.")
        except Exception as e:
            logging.error(f"Error: {e}")
            await ctx.send(f"Error: {e}")

    @commands.command(brief="Unmutes the audio🔊.")
    async def unmute(self, ctx):
        media_player = self._get_media_player()
        if not media_player:
            await ctx.send("No media player is active.")
            return
        try:
            media_player.audio_set_mute(0)
            logging.info("Unmuted.")
            await ctx.send("Unmuted🔊.")
        except Exception as e:
            logging.error(f"Error: {e}")
            await ctx.send(f"Error: {e}")