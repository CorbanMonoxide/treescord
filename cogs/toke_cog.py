import discord
from discord.ext import commands, tasks
import asyncio
import logging
import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message.s)')

class TokeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.toke_active = False
        self.tokers = set()
        self.countdown_seconds = 10
        self.countdown_task = None
        self.cooldown_seconds = 10
        self.cooldown_active = False
        self.toke_message = None
        self.cooldown_end_time = None

    async def start_toke(self, ctx_or_interaction):
        self.toke_active = True
        if isinstance(ctx_or_interaction, commands.Context):
            user = ctx_or_interaction.author
        else:
            user = ctx_or_interaction.user
        self.tokers.add(user)
        view = discord.ui.View()
        join_button = discord.ui.Button(label="Join Toke 🍃", style=discord.ButtonStyle.primary, custom_id="join_toke")
        remote_button = discord.ui.Button(label="Remote 📺", style=discord.ButtonStyle.secondary, custom_id="remote_button")
        view.add_item(join_button)
        view.add_item(remote_button)
        if isinstance(ctx_or_interaction, commands.Context):
            await ctx_or_interaction.send(f"A group toke 🍃 has been started by {user.mention}! We'll be taking a toke in {self.countdown_seconds} seconds - join in by clicking the button below or by typing !toke", view=view)
            self.countdown_task = self.bot.loop.create_task(self.countdown(ctx_or_interaction, self.countdown_seconds))
        else:
            await ctx_or_interaction.response.send_message(f"A group toke 🍃 has been started by {user.mention}! We'll be taking a toke in {self.countdown_seconds} seconds - join in by clicking the button below.", view=view)
            self.countdown_task = self.bot.loop.create_task(self.countdown(ctx_or_interaction, self.countdown_seconds))

    async def countdown(self, ctx_or_interaction, initial_countdown):
        countdown = initial_countdown
        while countdown > 0:
            if countdown <= 3:
                await ctx_or_interaction.send(f"Get ready to toke 🍃 - {countdown}!")
            await asyncio.sleep(1)
            countdown -= 1

        if self.tokers:
            toker_names = ", ".join(toker.mention for toker in self.tokers)
            await ctx_or_interaction.send(f"Take a toke {toker_names}! 🌬️🍃😶‍🌫️")
            self.toke_active = False
            self.tokers.clear()
            self.countdown_task = None
            self.cooldown_active = True
            self.cooldown_end_time = datetime.datetime.now() + datetime.timedelta(seconds=self.cooldown_seconds)
            await asyncio.sleep(self.cooldown_seconds)
            self.cooldown_active = False
            self.cooldown_end_time = None
            self.toke_message = None

    @commands.command(brief="Starts or joins a group toke🌬️🍃😶‍🌫️.")
    async def toke(self, ctx):
        """Starts or joins a group toke.

        Usage: !toke

        Starts a group toke with a 60-second countdown.
        If a toke is already active, this command joins the existing toke and resets the timer.
        """
        if self.cooldown_active:
            remaining_time = self.cooldown_end_time - datetime.datetime.now()
            remaining_seconds = int(remaining_time.total_seconds())
            await ctx.send(f"*Only you can see this.*\n*{ctx.author.mention}, Toke is on cooldown 🍃. Please wait {remaining_seconds} seconds.*", ephemeral=True)
            return

        if not self.toke_active:
            await self.start_toke(ctx)
        else:
            if ctx.author in self.tokers:
                await ctx.send(f"*Only you can see this.*\n*You are already in this toke.*", ephemeral=True)
                return
            self.tokers.add(ctx.author)
            view = discord.ui.View()
            join_button = discord.ui.Button(label="Join Toke 🍃", style=discord.ButtonStyle.primary, custom_id="join_toke")
            remote_button = discord.ui.Button(label="Remote 📺", style=discord.ButtonStyle.secondary, custom_id="remote_button")
            view.add_item(join_button)
            view.add_item(remote_button)
            await ctx.send(f"{ctx.author.mention} has joined the toke! 🍃", view=view)
            if self.toke_message:
                await self.toke_message.edit(view=view)

    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        if interaction.data and interaction.data.get('custom_id') == "join_toke":
            ctx = await self.bot.get_context(interaction.message)
            ctx.author = interaction.user
            await self.toke(ctx)
            await interaction.response.defer()
        elif interaction.data and interaction.data.get('custom_id') == "remote_button":
            await interaction.response.defer()
            ctx = await self.bot.get_context(interaction.message)
            ctx.author = interaction.user
            remote_command = self.bot.get_command("remote")
            if remote_command:
                await ctx.invoke(remote_command)
            else:
                await interaction.followup.send("Remote command not found.", ephemeral=True)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            logging.error(f'Command error: {error}')
            await ctx.send(f'An error occurred: {error}')

async def setup(bot):
    await bot.add_cog(TokeCog(bot))