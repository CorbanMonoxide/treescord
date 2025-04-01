# cogs/toke_cog.py
import discord
from discord.ext import commands, tasks
import asyncio
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TokeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.toke_active = False
        self.tokers = set()
        self.countdown_seconds = 60
        self.countdown_task = None
        self.cooldown_seconds = 360
        self.cooldown_active = False

    async def start_toke(self, ctx):
        self.toke_active = True
        self.tokers.add(ctx.author)
        await ctx.send(f"A group toke has been started by {ctx.author.mention}! We'll be taking a toke in {self.countdown_seconds} seconds - join in by typing !toke")
        self.countdown_task = self.bot.loop.create_task(self.countdown(ctx))

    async def countdown(self, ctx):
        while self.countdown_seconds > 0:
            if self.countdown_seconds <= 3:
                await ctx.send(f"Get ready to toke - {self.countdown_seconds}!")
            await asyncio.sleep(1)
            self.countdown_seconds -= 1

        if self.tokers:
            toker_names = ", ".join(toker.mention for toker in self.tokers)
            await ctx.send(f"Take a toke {toker_names}!")
            self.toke_active = False
            self.tokers.clear()
            self.countdown_seconds = 60
            self.countdown_task = None
            self.cooldown_active = True
            await asyncio.sleep(self.cooldown_seconds)
            self.cooldown_active = False

    @commands.command(brief="Starts or joins a group toke.")
    async def toke(self, ctx):
        """Starts or joins a group toke.

        Usage: !toke

        Starts a group toke with a 60-second countdown.
        If a toke is already active, this command joins the existing toke and resets the timer.
        """
        if self.cooldown_active:
            await ctx.send(f"Toke is on cooldown. Please wait {self.cooldown_seconds} seconds.")
            return

        if not self.toke_active:
            await self.start_toke(ctx)
        else:
            self.tokers.add(ctx.author)
            self.countdown_seconds = 60 # Reset the countdown.
            await ctx.send(f"{ctx.author.mention} has joined the toke!")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            logging.error(f'Command error: {error}')
            await ctx.send(f'An error occurred: {error}')

async def setup(bot):
    await bot.add_cog(TokeCog(bot))