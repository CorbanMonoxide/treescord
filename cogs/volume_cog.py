import discord
from discord.ext import commands
import logging

class VolumeCog(commands.Cog):
    def __init__(self, bot, instance):
        self.bot = bot
        # self.instance = instance # No longer needed for creating a player
        # self.media_list_player = instance.media_list_player_new() # This creates a separate player. Remove it.

    def _get_media_player(self):
        """Helper to get the media player from PlaybackCog."""
        playback_cog = self.bot.get_cog('PlaybackCog')
        if playback_cog and hasattr(playback_cog, 'media_player') and playback_cog.media_player:
            return playback_cog.media_player
        return None

    @commands.command(brief="Sets the volume level by adding an integer after the command 🔈🔉🔊.")
    async def volume(self, ctx, level: int):
        media_player = self._get_media_player()
        if not media_player:
            await ctx.send("Error: Media player is not available.")
            logging.warning("Volume command failed: media_player not found in PlaybackCog.")
            return
        try:
            # Clamp volume between 0 and 200 (VLC can go higher, but this is a safe range)
            level = max(0, min(200, level))
            media_player.audio_set_volume(level)
            logging.info(f"Volume set to {level}")
            await ctx.send(f"Volume set to {level}")
        except Exception as e:
            logging.error(f"Error setting volume: {e}", exc_info=True)
            await ctx.send(f"Error: {e}")

    @commands.command(brief="Mutes the audio 🔇.")
    async def mute(self, ctx):
        media_player = self._get_media_player()
        if not media_player:
            await ctx.send("Error: Media player is not available.")
            logging.warning("Mute command failed: media_player not found in PlaybackCog.")
            return
        try:
            media_player.audio_set_mute(1)
            logging.info("Muted.")
            await ctx.send("Muted🔇.")
        except Exception as e:
            logging.error(f"Error muting: {e}", exc_info=True)
            await ctx.send(f"Error: {e}")

    @commands.command(brief="Unmutes the audio🔊.")
    async def unmute(self, ctx):
        media_player = self._get_media_player()
        if not media_player:
            await ctx.send("Error: Media player is not available.")
            logging.warning("Unmute command failed: media_player not found in PlaybackCog.")
            return
        try:
            media_player.audio_set_mute(0)
            logging.info("Unmuted.")
            await ctx.send("Unmuted🔊.")
        except Exception as e:
            logging.error(f"Error unmuting: {e}", exc_info=True)
            await ctx.send(f"Error: {e}")