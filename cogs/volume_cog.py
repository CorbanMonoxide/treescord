import discord
from discord.ext import commands
import logging

class VolumeCog(commands.Cog):
    def __init__(self, bot, instance):
        self.bot = bot
        self.instance = instance
        self.media_list_player = instance.media_list_player_new()

    @commands.command(brief="Sets the volume level by adding an integer after the command 🔈🔉🔊.")
    async def volume(self, ctx, level: int):
        try:
            self.media_list_player.get_media_player().audio_set_volume(level)
            logging.info(f"Volume set to {level}")
            await ctx.send(f"Volume set to {level}")
        except Exception as e:
            logging.error(f"Error: {e}")
            await ctx.send(f"Error: {e}")

    @commands.command(brief="Mutes the audio 🔇.")
    async def mute(self, ctx):
        try:
            self.media_list_player.get_media_player().audio_set_mute(1)
            logging.info("Muted.")
            await ctx.send("Muted🔇.")
        except Exception as e:
            logging.error(f"Error: {e}")
            await ctx.send(f"Error: {e}")

    @commands.command(brief="Unmutes the audio🔊.")
    async def unmute(self, ctx):
        try:
            self.media_list_player.get_media_player().audio_set_mute(0)
            logging.info("Unmuted.")
            await ctx.send("Unmuted🔊.")
        except Exception as e:
            logging.error(f"Error: {e}")
            await ctx.send(f"Error: {e}")