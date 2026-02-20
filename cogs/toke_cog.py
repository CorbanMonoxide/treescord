import discord
from discord.ext import commands
import asyncio
import logging
import datetime
import random
import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TokeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.toke_active = False
        self.tokers = set()
        self.countdown_seconds = config.TOKE_COUNTDOWN_SECONDS
        self.countdown_task = None
        self.cooldown_seconds = config.TOKE_COOLDOWN_SECONDS
        self.cooldown_active = False
        self.cooldown_end_time = None
        self.current_countdown = config.TOKE_COUNTDOWN_SECONDS
        self.toke_start_time = None

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
            await tracker_cog.user_joined_toke(ctx.author, ctx) # This increments the general toke count
            # Check for 4:20 join time
            now = datetime.datetime.now()
            if (now.hour == 4 or now.hour == 16) and (now.minute == 19 or now.minute == 20):
                await tracker_cog.user_joined_at_420(ctx.author, ctx)
            # Check for Wake and Bake time
            if 5 <= now.hour < 9: # 5 AM to 8:59 AM
                await tracker_cog.user_joined_wake_and_bake(ctx.author, ctx)
        
        self.toke_start_time = datetime.datetime.now()
        self.current_countdown = self.countdown_seconds
        view = self._create_toke_view()

        # Check for 4:21 achievement (You're Too Slow!)
        # The achievement description says "Joined a toke that started at 4:21!"
        # This checks if the toke *started* at 4:21
        start_time = self.toke_start_time
        if (start_time.hour == 4 or start_time.hour == 16) and start_time.minute == 21:
            achievements_cog = self.bot.get_cog("AchievementsCog")
            if achievements_cog:
                await achievements_cog.user_joined_421_toke_late(ctx.author, ctx)
        
        await ctx.send(
            f"A group toke 🍃 has been started by {ctx.author.mention}! "
            f"We'll be taking a toke in {self.countdown_seconds} seconds - "
            "join in by clicking the button below or by typing !toke",
            view=view
        )
        self.countdown_task = self.bot.loop.create_task(self.countdown(ctx))

    async def countdown(self, ctx):
        while self.current_countdown > 0:
            if self.current_countdown <= 3:
                logging.info(f"Toke countdown: {self.current_countdown} seconds remaining")
                await ctx.send(f"Get ready to toke 🍃 - {self.current_countdown}!")
            await asyncio.sleep(1)
            self.current_countdown -= 1

        if self.tokers:
            # Check if it was a solo toke when the countdown finishes
            if len(self.tokers) == 1:
                solo_toker = list(self.tokers)[0] # Get the single user
                tracker_cog = self.bot.get_cog("TreesTrackerCog")
                if tracker_cog:
                    await tracker_cog.user_solo_toked(solo_toker, ctx) # Pass ctx here
                    logging.info(f"User {solo_toker.name} (ID: {solo_toker.id}) completed a solo toke.")
                await ctx.send(f"Solo Toke! {solo_toker.mention} take a toke! 🌬️🍃😶‍🌫️")
            else:
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
                await ctx.send(f"{ctx.author.mention} is already in this toke. {self.current_countdown} seconds remaining until toke time! 🍃")
                return

            self.tokers.add(ctx.author)
            tracker_cog = self.bot.get_cog("TreesTrackerCog")
            if tracker_cog:
                await tracker_cog.user_joined_toke(ctx.author, ctx)
                # Check for 4:20 join time
                now = datetime.datetime.now()
                if (now.hour == 4 or now.hour == 16) and (now.minute == 19 or now.minute == 20):
                    await tracker_cog.user_joined_at_420(ctx.author, ctx) # This increments the 4:20 count
                # Check for Wake and Bake time
                if 5 <= now.hour < 9: # 5 AM to 8:59 AM
                    await tracker_cog.user_joined_wake_and_bake(ctx.author, ctx)
            
            # Check for 4:21 achievement (You're Too Slow!)
            # The achievement description says "Joined a toke that started at 4:21!"
            if self.toke_start_time:
                start_time = self.toke_start_time
                if (start_time.hour == 4 or start_time.hour == 16) and start_time.minute == 21:
                    achievements_cog = self.bot.get_cog("AchievementsCog")
                    if achievements_cog:
                        await achievements_cog.user_joined_421_toke_late(ctx.author, ctx)


            if self.current_countdown <= 10:
                self.current_countdown += 5
                if tracker_cog: # Increment tokes_saved_count
                    await tracker_cog.user_saved_toke(ctx.author, ctx)
                await ctx.send(f"{ctx.author.mention} joined with little time left! Added 5 seconds to the toke timer. ⏳")
            view = self._create_toke_view()
            
            await ctx.send(f"{ctx.author.mention} has joined the toke! {self.current_countdown} seconds remaining. 🍃", view=view)

    @commands.command(brief="Checks if you're late to the toke.")
    async def l8toke(self, ctx):
        """Displays a message if a toke is on cooldown and you missed it."""
        if not self.toke_active and self.cooldown_active:
            await ctx.send(f"{ctx.author.mention}, You're too slow! <a:Sonic:1382135439649149069>")
        elif self.toke_active:
            await ctx.send(f"{ctx.author.mention}, A toke is happening now! Type `!toke` to join. ({self.current_countdown}s left)")
        else:
            await ctx.send(f"{ctx.author.mention}, No toke is active or on cooldown. Type `!toke` to start one! ✨")

    @commands.command(brief="Try to start a toke during cooldown... maybe.")
    async def earlytoke(self, ctx):
        """Checks if a toke is on cooldown and might just start one anyway."""
        achievements_cog = self.bot.get_cog("AchievementsCog")
        if achievements_cog:
            # Increment attempts on every call
            await achievements_cog.increment_earlytoke_attempts(ctx.author.id)
            await achievements_cog.increment_earlytoke_lifetime(ctx.author.id)

        if self.toke_active:
            await ctx.send("A toke is already active! Join in!")
            return

        if self.cooldown_active:
            # Random chance to allow early toke (your logic here)
            import random
            if random.random() < 0.1:  # 10% chance, adjust as needed
                # Early toke activated!
                attempts = 0
                if achievements_cog:
                    attempts = await achievements_cog.get_earlytoke_attempts(ctx.author.id)
                    await achievements_cog.reset_earlytoke_attempts(ctx.author.id)

                # Reset the cooldown to allow others to join
                self.cooldown_active = False
                self.cooldown_end_time = None

                await ctx.send(f"🧼 Early toke activated! Welcome to Toke Club. It took you {attempts} attempt(s) to trigger an early toke!")
                
                tracker_cog = self.bot.get_cog("TreesTrackerCog")
                if tracker_cog:
                    await tracker_cog.user_joined_toke_club(ctx.author, ctx)

                # Award the 'early_riser' and 'secret_society' achievements here
                if achievements_cog:
                    await achievements_cog.user_triggered_early_toke(ctx.author, ctx)
                    await achievements_cog.user_joined_secret_society(ctx.author, ctx)
                await self.start_toke(ctx)
            else:
                # Add variety to the failure message
                fail_msgs = [
                    "You are not your early toke. 🧼 If you !earlytoke, you have to toke irl.",
                    "I am jack's earliest toker. 🧼 If you !earlytoke, you have to toke irl.",
                    "You are not a beautiful and unique early toker. 🧼 If you !earlytoke, you have to toke irl.",
                    "Sticking feathers up your butt does not make you an early toker. 🧼 If you !earlytoke, you have to toke irl.",
                    "Sometimes you just can't get in early. 🧼 If you !earlytoke, you have to toke irl.",
                    "This is your life and it's ending one toke at a time. 🧼 If you !earlytoke, you have to toke irl.",
                    "You met me at a very strange time to try to toke. 🧼 If you !earlytoke, you have to toke irl.",
                    "On a long enough timeline, everyone misses a toke. 🧼 If you !earlytoke, you have to toke irl.",
                    "The doinks you toke end up toking you. 🧼 If you !earlytoke, you have to toke irl.",
                    "You decide your own level of toke-age. 🧼 If you !earlytoke, you have to toke irl.",
                ]
                await ctx.send(random.choice(fail_msgs))
        else:
            await ctx.send("No cooldown active. Just use !toke to start a session.")
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if not interaction.data or not interaction.data.get('custom_id'):
            return

        custom_id = interaction.data.get('custom_id')

        if custom_id == "join_toke":
            # Acknowledge the interaction immediately to prevent "Interaction failed"
            await interaction.response.defer()
            
            ctx = await self.bot.get_context(interaction.message)
            ctx.author = interaction.user
            await self.toke(ctx)
        
        elif custom_id == "show_remote":
            # Acknowledge the interaction immediately
            await interaction.response.defer()

            ctx = await self.bot.get_context(interaction.message)
            ctx.author = interaction.user
            remote_cog = self.bot.get_cog("RemoteCog")
            if remote_cog:
                await remote_cog.create_controller(ctx)
            else:
                # Since we've deferred, use followup.send for any messages related to this interaction
                await interaction.followup.send("Remote controller feature is not available.", ephemeral=True)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            logging.error(f'Command error: {error}')
            await ctx.send(f'An error occurred: {error}')

async def setup(bot):
    await bot.add_cog(TokeCog(bot))