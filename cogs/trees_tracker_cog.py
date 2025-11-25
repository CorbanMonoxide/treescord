# trees_tracker_cog.py
import discord
from discord.ext import commands
import aiosqlite
import logging
import os
import asyncio

DATABASE_FILE = "tokers.db"

# Define the stats that will have a leaderboard page
LEADERBOARD_STATS = [
    {"db_column": "toke_count", "display_name": "Group Tokes", "emoji": "💨"},
    {"db_column": "solo_toke_count", "display_name": "Solo Tokes", "emoji": "🍃"},
    {"db_column": "tokes_saved_count", "display_name": "Tokes Saved", "emoji": "⏳"},
    {"db_column": "four_twenty_tokes_count", "display_name": "4:20 Tokes", "emoji": "🍁"},
    {"db_column": "wake_and_bake_tokes_count", "display_name": "Wake and Bakes", "emoji": "☀️"},
    {"db_column": "toke_club_sessions_count", "display_name": "Toke Club Sessions", "emoji": "🧼"},
]

class LeaderboardView(discord.ui.View):
    def __init__(self, bot, stats_to_show, initial_stat_index=0):
        super().__init__(timeout=180.0)
        self.bot = bot
        self.stats_to_show = stats_to_show
        self.current_stat_index = initial_stat_index
        self.message: discord.Message = None

    async def on_timeout(self):
        if self.message:
            for item in self.children:
                item.disabled = True
            try:
                await self.message.edit(view=self)
            except discord.NotFound:
                pass # Message was deleted

    async def _create_leaderboard_embed(self) -> discord.Embed:
        tracker_cog = self.bot.get_cog("TreesTrackerCog")
        stat_info = self.stats_to_show[self.current_stat_index]
        leaderboard_data = await tracker_cog._get_leaderboard_data(stat_info["db_column"])

        embed = discord.Embed(title=f"🏆 {stat_info['display_name']} Leaderboard {stat_info['emoji']} 🏆", color=discord.Color.gold())
        
        if not leaderboard_data:
            embed.description = "This leaderboard is empty! 💨"
        else:
            description = []
            for i, (user_name, count) in enumerate(leaderboard_data[:10], 1): # Show top 10
                rank_emoji = {1: "🥇 ", 2: "🥈 ", 3: "🥉 "}.get(i, f"**{i}.** ")
                description.append(f"{rank_emoji}{user_name}: {count}")
            embed.description = "\n".join(description)

        embed.set_footer(text=f"Page {self.current_stat_index + 1}/{len(self.stats_to_show)}")
        return embed

    @discord.ui.button(emoji="⬅️", style=discord.ButtonStyle.secondary)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_stat_index = (self.current_stat_index - 1) % len(self.stats_to_show)
        embed = await self._create_leaderboard_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(emoji="➡️", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_stat_index = (self.current_stat_index + 1) % len(self.stats_to_show)
        embed = await self._create_leaderboard_embed()
        await interaction.response.edit_message(embed=embed, view=self)

class TreesTrackerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_file = DATABASE_FILE

    async def cog_load(self):
        await self._initialize_database()

    async def _initialize_database(self):
        """Initializes the database and ensures all necessary columns exist."""
        async with aiosqlite.connect(self.db_file) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('''
                    CREATE TABLE IF NOT EXISTS toke_stats (
                        user_id INTEGER PRIMARY KEY,
                        user_name TEXT
                    )
                ''')

                # A list of all stat columns that should be in the table.
                # To add a new stat, just add its column name here.
                columns_to_ensure = [
                    ("toke_count", "INTEGER NOT NULL DEFAULT 0"),
                    ("solo_toke_count", "INTEGER NOT NULL DEFAULT 0"),
                    ("tokes_saved_count", "INTEGER NOT NULL DEFAULT 0"),
                    ("four_twenty_tokes_count", "INTEGER NOT NULL DEFAULT 0"),
                    ("wake_and_bake_tokes_count", "INTEGER NOT NULL DEFAULT 0"),
                    ("toke_club_sessions_count", "INTEGER NOT NULL DEFAULT 0"),
                ]

                for column_name, column_type in columns_to_ensure:
                    try:
                        await cursor.execute(f"ALTER TABLE toke_stats ADD COLUMN {column_name} {column_type}")
                        logging.info(f"Added '{column_name}' column to 'toke_stats' table.")
                    except Exception as e:
                        if "duplicate column name" in str(e).lower():
                            logging.info(f"'{column_name}' column already exists in 'toke_stats' table.")
                        else:
                            logging.error(f"An unexpected error occurred when adding column '{column_name}': {e}")

                await conn.commit()
        logging.info(f"Database '{self.db_file}' initialized and 'toke_stats' table ensured.")

    async def _update_stat(self, user_id: int, user_name: str, stat_column: str, value: int = 1):
        """A generic function to update a user's stat in the database."""
        async with aiosqlite.connect(self.db_file) as conn:
            async with conn.cursor() as cursor:
                # Ensure the user exists in the table
                await cursor.execute("INSERT OR IGNORE INTO toke_stats (user_id, user_name) VALUES (?, ?)", (user_id, user_name))
                
                # Increment the specific stat column and update the username
                # It's safe to use an f-string for the column name because we control the input.
                query = f"UPDATE toke_stats SET {stat_column} = {stat_column} + ?, user_name = ? WHERE user_id = ?"
                await cursor.execute(query, (value, user_name, user_id))
                await conn.commit()
                logging.info(f"Updated stat '{stat_column}' for user {user_name} (ID: {user_id}) by {value}.")

    async def _increment_stat(self, user_id: int, user_name: str, stat_column: str, value: int = 1):
        """Asynchronously calls the generic stat update function."""
        await self._update_stat(user_id, user_name, stat_column, value)

    async def user_joined_toke(self, user: discord.User, ctx: commands.Context = None):
        if user.bot: # Don't track bots
            return
        await self._increment_stat(user.id, user.name, "toke_count")
        achievements_cog = self.bot.get_cog("AchievementsCog")
        if achievements_cog and ctx:
            await achievements_cog.check_and_award_achievements(user, ctx)

    async def user_solo_toked(self, user: discord.User, ctx: commands.Context = None):
        if user.bot: # Don't track bots
            return
        await self._increment_stat(user.id, user.name, "solo_toke_count")
        achievements_cog = self.bot.get_cog("AchievementsCog")
        if achievements_cog and ctx:
            await achievements_cog.check_and_award_achievements(user, ctx)

    async def user_saved_toke(self, user: discord.User, ctx: commands.Context = None):
        if user.bot: # Don't track bots
            return
        await self._increment_stat(user.id, user.name, "tokes_saved_count")
        achievements_cog = self.bot.get_cog("AchievementsCog")
        if achievements_cog and ctx:
            await achievements_cog.check_and_award_achievements(user, ctx)

    async def user_joined_at_420(self, user: discord.User, ctx: commands.Context = None):
        if user.bot: # Don't track bots
            return
        await self._increment_stat(user.id, user.name, "four_twenty_tokes_count")
        achievements_cog = self.bot.get_cog("AchievementsCog")
        if achievements_cog and ctx:
            await achievements_cog.check_and_award_achievements(user, ctx)

    async def user_joined_wake_and_bake(self, user: discord.User, ctx: commands.Context = None):
        if user.bot: # Don't track bots
            return
        await self._increment_stat(user.id, user.name, "wake_and_bake_tokes_count")
        achievements_cog = self.bot.get_cog("AchievementsCog")
        if achievements_cog and ctx:
            await achievements_cog.check_and_award_achievements(user, ctx)

    async def user_joined_toke_club(self, user: discord.User, ctx: commands.Context = None):
        if user.bot: # Don't track bots
            return
        await self._increment_stat(user.id, user.name, "toke_club_sessions_count")
        achievements_cog = self.bot.get_cog("AchievementsCog")
        if achievements_cog and ctx:
            await achievements_cog.check_and_award_achievements(user, ctx)

    async def _get_leaderboard_data(self, stat_column: str):
        try:
            async with aiosqlite.connect(self.db_file) as conn:
                async with conn.cursor() as cursor:
                    # It's safe to use an f-string for the column name because we control the input from LEADERBOARD_STATS
                    query = f"SELECT user_name, {stat_column} FROM toke_stats WHERE {stat_column} > 0 ORDER BY {stat_column} DESC"
                    await cursor.execute(query)
                    return await cursor.fetchall()
        except Exception as e:
            logging.error(f"Database error in _get_leaderboard_data for stat '{stat_column}': {e}")
            return None
 
    @commands.command(brief="Displays interactive leaderboards for all stats 🏆.")
    async def leaderboard(self, ctx, *, stat_name: str = None):
        """
        Displays paginated leaderboards for various toking statistics.
        You can jump to a specific stat by providing its name.
        Example: !leaderboard "solo tokes"
        """
        initial_stat_index = 0
        if stat_name:
            stat_name_lower = stat_name.lower()
            # Find the index of the first stat that matches the input name
            found_index = next((i for i, stat in enumerate(LEADERBOARD_STATS) if stat_name_lower in stat["display_name"].lower()), None)
            if found_index is not None:
                initial_stat_index = found_index
            else:
                await ctx.send(f"Stat '{stat_name}' not found. Showing the first leaderboard.")
 
        view = LeaderboardView(self.bot, LEADERBOARD_STATS, initial_stat_index)
        embed = await view._create_leaderboard_embed()
        message = await ctx.send(embed=embed, view=view)
        view.message = message
 
    @commands.command(brief="Deletes the toke tracker database (owner only) 💣.")
    @commands.is_owner()
    async def deletetoketracker(self, ctx):
        """Deletes the toker.db file. This action is irreversible."""
        try:
            if os.path.exists(self.db_file):
                await self.bot.loop.run_in_executor(None, os.remove, self.db_file)
                logging.info(f"Database file '{self.db_file}' deleted by {ctx.author.name}.")
                await ctx.send(f"Toke tracker database (`{self.db_file}`) has been deleted. It will be recreated on next use or bot restart.")
                await self._initialize_database()
            else:
                await ctx.send(f"Toke tracker database (`{self.db_file}`) does not exist.")
        except Exception as e:
            logging.error(f"Error deleting database file '{self.db_file}': {e}")
            await ctx.send(f"An error occurred while trying to delete the database: {e}")

    async def _get_user_stats_from_db(self, user_id: int):
        """Fetches user_name and toke_count for a given user_id from the database."""
        try:
            async with aiosqlite.connect(self.db_file) as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("SELECT user_name, toke_count, solo_toke_count, tokes_saved_count, four_twenty_tokes_count, wake_and_bake_tokes_count, toke_club_sessions_count FROM toke_stats WHERE user_id = ?", (user_id,))
                    return await cursor.fetchone()
        except Exception as e:
            logging.error(f"Database error in _get_user_stats_from_db for user_id {user_id}: {e}")
            return None

    @commands.command(brief="Displays your or another user's toke statistics 📊. Usage: !stats [@user]")
    async def stats(self, ctx, member: discord.Member = None):
        """Displays toke statistics for yourself or a mentioned user."""
        target_user = member or ctx.author

        achievements_cog = self.bot.get_cog("AchievementsCog")
        earlytoke_attempts = None
        if achievements_cog:
            # Show lifetime attempts only
            earlytoke_attempts = await achievements_cog.get_earlytoke_lifetime(target_user.id)

        user_data = await self._get_user_stats_from_db(target_user.id)

        if user_data:
            _db_user_name, toke_count, solo_toke_count, tokes_saved_count, four_twenty_tokes_count, wake_and_bake_tokes_count, toke_club_sessions_count = user_data
            embed = discord.Embed(
                title=f"🌿 Toke Stats for {target_user.display_name} 🌿",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=target_user.display_avatar.url)
            embed.add_field(name="Group Tokes Joined", value=f"{toke_count} 💨", inline=False)
            embed.add_field(name="Solo Tokes Completed", value=f"{solo_toke_count} 🍃", inline=False)
            embed.add_field(name="Tokes Saved", value=f"{tokes_saved_count} ⏳", inline=False)
            embed.add_field(name="4:20 Tokes Joined", value=f"{four_twenty_tokes_count} 🍁", inline=False)
            embed.add_field(name="Wake and Bake Tokes", value=f"{wake_and_bake_tokes_count} ☀️", inline=False)
            if earlytoke_attempts is not None:
                embed.add_field(name="Early Toke Attempts (Lifetime)", value=f"{earlytoke_attempts} 🚬", inline=False)
            embed.add_field(name="Toke Club Sessions", value=f"{toke_club_sessions_count} 🧼", inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"{target_user.display_name} hasn't participated in any tokes yet, or their stats couldn't be found. 🤷")

async def setup(bot):
    await bot.add_cog(TreesTrackerCog(bot))