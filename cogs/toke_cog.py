import discord
from discord.ext import commands
import asyncio
import logging
import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TokeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.toke_active = False
        self.tokers = set()
        self.countdown_seconds = 60
        self.countdown_task = None
        self.cooldown_seconds = 240
        self.cooldown_active = False
        self.cooldown_end_time = None
        self.current_countdown = 60

    def _create_toke_view(self):
        view = discord.ui.View() # Buttons will use default timeout (180 seconds)
        join_button = discord.ui.Button(label="Join Toke 🍃", style=discord.ButtonStyle.primary, custom_id="join_toke")
        remote_button = discord.ui.Button(label="Show Remote 📱", style=discord.ButtonStyle.secondary, custom_id="show_remote")
        view.add_item(join_button)
        view.add_item(remote_button)
        return view

    async def start_toke(self, ctx):
        self.toke_active = True
        self.tokers.add(ctx.author)
        tracker_cog = self.bot.get_cog("TreesTrackerCog")
        if tracker_cog:
            await tracker_cog.user_joined_toke(ctx.author)
            
        self.current_countdown = self.countdown_seconds
        view = self._create_toke_view()
        
        await ctx.send(
            f"A group toke 🍃 has been started by {ctx.author.mention}! "
            f"We'll be taking a toke in {self.countdown_seconds} seconds - "
            "join in by clicking the button below or by typing !toke",
            view=view
        )
        self.countdown_task = self.bot.loop.create_task(self.countdown(ctx, self.countdown_seconds))

    async def countdown(self, ctx, initial_countdown):
        countdown = initial_countdown
        while countdown > 0:
            if countdown <= 3:
                logging.info(f"Toke countdown: {countdown} seconds remaining")
                await ctx.send(f"Get ready to toke 🍃 - {countdown}!")
            await asyncio.sleep(1)
            countdown -= 1
            self.current_countdown = countdown  # Update current countdown for other users to see

        if self.tokers:
            toker_names = ", ".join(toker.mention for toker in self.tokers)
            await ctx.send(f"Take a toke {toker_names}! 🌬️🍃😶‍🌫️")
            self.toke_active = False
            self.tokers.clear()
            self.countdown_task = None
            self.cooldown_active = True
            self.cooldown_end_time = datetime.datetime.now() + datetime.timedelta(seconds=self.cooldown_seconds)
            await asyncio.sleep(self.cooldown_seconds)
            self.cooldown_active = False
            self.cooldown_end_time = None

    @commands.command(brief="Starts or joins a group toke🌬️🍃😶‍🌫️.")
    async def toke(self, ctx):
        """Starts or joins a group toke.
        
        Starts a group toke with a 60-second countdown.
        If a toke is already active, joins and adds 5 seconds to the timer.
        """
        if self.cooldown_active:
            remaining_time = self.cooldown_end_time - datetime.datetime.now()
            remaining_seconds = int(remaining_time.total_seconds())
            await ctx.send(
                f"{ctx.author.mention}, Toke is on cooldown 🍃. Please wait {remaining_seconds} seconds."
            )
            return

        if not self.toke_active:
            await self.start_toke(ctx)
        else:
            if ctx.author in self.tokers:
                await ctx.send(f"You are already in this toke. {self.current_countdown} seconds remaining until toke time! 🍃")
                return
                
            self.tokers.add(ctx.author)
            tracker_cog = self.bot.get_cog("TreesTrackerCog")
            if tracker_cog:
                await tracker_cog.user_joined_toke(ctx.author)

            self.current_countdown += 5
            
            view = self._create_toke_view()
            
            await ctx.send(f"{ctx.author.mention} has joined the toke! 🍃", view=view)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if not interaction.data or not interaction.data.get('custom_id'):
            return

        custom_id = interaction.data.get('custom_id')

        if custom_id == "join_toke":
            ctx = await self.bot.get_context(interaction.message)
            ctx.author = interaction.user
            await self.toke(ctx)
            # self.toke command sends its own messages, so we just defer the interaction response.
            await interaction.response.defer()
        
        elif custom_id == "show_remote":
            ctx = await self.bot.get_context(interaction.message)
            ctx.author = interaction.user
            remote_cog = self.bot.get_cog("RemoteCog")
            if remote_cog:
                await remote_cog.create_controller(ctx)
                await interaction.response.defer() # Acknowledge the button click
            else:
                await interaction.response.send_message("Remote controller feature is not available.", ephemeral=True)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            logging.error(f'Command error: {error}')
            await ctx.send(f'An error occurred: {error}')

async def setup(bot):
    await bot.add_cog(TokeCog(bot))