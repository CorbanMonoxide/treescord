# trees_tracker_cog.py
import discord
from discord.ext import commands
import sqlite3
import logging
import os
import asyncio

DATABASE_FILE = "tokers.db"

class TreesTrackerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_file = DATABASE_FILE
        self._initialize_database()

    def _initialize_database(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS toke_stats (
                user_id INTEGER PRIMARY KEY,
                user_name TEXT,
                toke_count INTEGER NOT NULL DEFAULT 0,
                solo_toke_count INTEGER NOT NULL DEFAULT 0,
                tokes_saved_count INTEGER NOT NULL DEFAULT 0,
                four_twenty_tokes_count INTEGER NOT NULL DEFAULT 0,
                wake_and_bake_tokes_count INTEGER NOT NULL DEFAULT 0
            )
        ''')
        conn.commit()
        # For existing databases, try to add the new column if it doesn't exist
        try:
            cursor.execute("ALTER TABLE toke_stats ADD COLUMN solo_toke_count INTEGER NOT NULL DEFAULT 0")
            conn.commit()
            logging.info("Added 'solo_toke_count' column to 'toke_stats' table.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                logging.info("'solo_toke_count' column already exists in 'toke_stats' table.")
            # Not raising other errors to avoid interruption if DB is fine
        try:
            cursor.execute("ALTER TABLE toke_stats ADD COLUMN tokes_saved_count INTEGER NOT NULL DEFAULT 0")
            conn.commit()
            logging.info("Added 'tokes_saved_count' column to 'toke_stats' table.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                logging.info("'tokes_saved_count' column already exists in 'toke_stats' table.")
            # Not raising other errors to avoid interruption if DB is fine
        try:
            cursor.execute("ALTER TABLE toke_stats ADD COLUMN four_twenty_tokes_count INTEGER NOT NULL DEFAULT 0")
            conn.commit()
            logging.info("Added 'four_twenty_tokes_count' column to 'toke_stats' table.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                logging.info("'four_twenty_tokes_count' column already exists in 'toke_stats' table.")
            # Not raising other errors to avoid interruption if DB is fine
        try:
            cursor.execute("ALTER TABLE toke_stats ADD COLUMN wake_and_bake_tokes_count INTEGER NOT NULL DEFAULT 0")
            conn.commit()
            logging.info("Added 'wake_and_bake_tokes_count' column to 'toke_stats' table.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                logging.info("'wake_and_bake_tokes_count' column already exists in 'toke_stats' table.")
        conn.close()
        logging.info(f"Database '{self.db_file}' initialized and 'toke_stats' table ensured.")

    def _sync_increment_toke_count_in_db(self, user_id: int, user_name: str):
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO toke_stats (user_id, user_name, toke_count, solo_toke_count, tokes_saved_count, four_twenty_tokes_count, wake_and_bake_tokes_count) VALUES (?, ?, 0, 0, 0, 0, 0)", (user_id, user_name))
            cursor.execute("UPDATE toke_stats SET toke_count = toke_count + 1, user_name = ? WHERE user_id = ?", (user_name, user_id))
            conn.commit()
            logging.info(f"Incremented toke count for user {user_name} (ID: {user_id}).")
        except sqlite3.Error as e:
            logging.error(f"Database error in _sync_increment_toke_count_in_db: {e}")
        finally:
            if conn:
                conn.close()

    async def _increment_toke_count_in_db(self, user_id: int, user_name: str):
        await self.bot.loop.run_in_executor(None, self._sync_increment_toke_count_in_db, user_id, user_name)

    async def user_joined_toke(self, user: discord.User, ctx: commands.Context = None):
        if user.bot: # Don't track bots
            return
        await self._increment_toke_count_in_db(user.id, user.name)
        achievements_cog = self.bot.get_cog("AchievementsCog")
        if achievements_cog and ctx:
            await achievements_cog.check_and_award_achievements(user, ctx)


    def _sync_increment_solo_toke_count_in_db(self, user_id: int, user_name: str):
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO toke_stats (user_id, user_name, toke_count, solo_toke_count, tokes_saved_count, four_twenty_tokes_count, wake_and_bake_tokes_count) VALUES (?, ?, 0, 0, 0, 0, 0)", (user_id, user_name))
            cursor.execute("UPDATE toke_stats SET solo_toke_count = solo_toke_count + 1, user_name = ? WHERE user_id = ?", (user_name, user_id))
            conn.commit()
            logging.info(f"Incremented solo toke count for user {user_name} (ID: {user_id}).")
        except sqlite3.Error as e:
            logging.error(f"Database error in _sync_increment_solo_toke_count_in_db: {e}")
        finally:
            if conn:
                conn.close()

    async def _increment_solo_toke_count_in_db(self, user_id: int, user_name: str):
        await self.bot.loop.run_in_executor(None, self._sync_increment_solo_toke_count_in_db, user_id, user_name)

    async def user_solo_toked(self, user: discord.User, ctx: commands.Context = None):
        if user.bot: # Don't track bots
            return
        await self._increment_solo_toke_count_in_db(user.id, user.name)
        achievements_cog = self.bot.get_cog("AchievementsCog")
        if achievements_cog and ctx:
            await achievements_cog.check_and_award_achievements(user, ctx)

    def _sync_increment_tokes_saved_count_in_db(self, user_id: int, user_name: str):
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO toke_stats (user_id, user_name, toke_count, solo_toke_count, tokes_saved_count, four_twenty_tokes_count, wake_and_bake_tokes_count) VALUES (?, ?, 0, 0, 0, 0, 0)", (user_id, user_name))
            cursor.execute("UPDATE toke_stats SET tokes_saved_count = tokes_saved_count + 1, user_name = ? WHERE user_id = ?", (user_name, user_id))
            conn.commit()
            logging.info(f"Incremented tokes saved count for user {user_name} (ID: {user_id}).")
        except sqlite3.Error as e:
            logging.error(f"Database error in _sync_increment_tokes_saved_count_in_db: {e}")
        finally:
            if conn:
                conn.close()
    async def user_saved_toke(self, user: discord.User, ctx: commands.Context = None):
        if user.bot: # Don't track bots
            return
        await self.bot.loop.run_in_executor(None, self._sync_increment_tokes_saved_count_in_db, user.id, user.name)
        achievements_cog = self.bot.get_cog("AchievementsCog")
        if achievements_cog and ctx:
            await achievements_cog.check_and_award_achievements(user, ctx)

    def _sync_increment_four_twenty_tokes_count_in_db(self, user_id: int, user_name: str):
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO toke_stats (user_id, user_name, toke_count, solo_toke_count, tokes_saved_count, four_twenty_tokes_count, wake_and_bake_tokes_count) VALUES (?, ?, 0, 0, 0, 0, 0)", (user_id, user_name))
            cursor.execute("UPDATE toke_stats SET four_twenty_tokes_count = four_twenty_tokes_count + 1, user_name = ? WHERE user_id = ?", (user_name, user_id))
            conn.commit()
            logging.info(f"Incremented 4:20 tokes count for user {user_name} (ID: {user_id}).")
        except sqlite3.Error as e:
            logging.error(f"Database error in _sync_increment_four_twenty_tokes_count_in_db: {e}")
        finally:
            if conn:
                conn.close()

    async def user_joined_at_420(self, user: discord.User, ctx: commands.Context = None):
        if user.bot: # Don't track bots
            return
        await self.bot.loop.run_in_executor(None, self._sync_increment_four_twenty_tokes_count_in_db, user.id, user.name)
        achievements_cog = self.bot.get_cog("AchievementsCog")
        if achievements_cog and ctx:
            await achievements_cog.check_and_award_achievements(user, ctx)

    def _sync_increment_wake_and_bake_tokes_count_in_db(self, user_id: int, user_name: str):
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO toke_stats (user_id, user_name, toke_count, solo_toke_count, tokes_saved_count, four_twenty_tokes_count, wake_and_bake_tokes_count) VALUES (?, ?, 0, 0, 0, 0, 0)", (user_id, user_name))
            cursor.execute("UPDATE toke_stats SET wake_and_bake_tokes_count = wake_and_bake_tokes_count + 1, user_name = ? WHERE user_id = ?", (user_name, user_id))
            conn.commit()
            logging.info(f"Incremented Wake and Bake tokes count for user {user_name} (ID: {user_id}).")
        except sqlite3.Error as e:
            logging.error(f"Database error in _sync_increment_wake_and_bake_tokes_count_in_db: {e}")
        finally:
            if conn:
                conn.close()

    async def user_joined_wake_and_bake(self, user: discord.User, ctx: commands.Context = None):
        if user.bot: # Don't track bots
            return
        await self.bot.loop.run_in_executor(None, self._sync_increment_wake_and_bake_tokes_count_in_db, user.id, user.name)
        achievements_cog = self.bot.get_cog("AchievementsCog")
        if achievements_cog and ctx:
            await achievements_cog.check_and_award_achievements(user, ctx)

    def _sync_get_leaderboard_data(self):
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT user_name, toke_count FROM toke_stats ORDER BY toke_count DESC")
            return cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Database error in _sync_get_leaderboard_data: {e}")
            return None
        finally:
            if conn:
                conn.close()

    @commands.command(brief="Displays the toke leaderboard 🏆.")
    async def leaderboard(self, ctx):
        """Displays the top tokers based on their toke count."""
        top_tokers = await self.bot.loop.run_in_executor(None, self._sync_get_leaderboard_data)

        if top_tokers is None: # Error occurred
            await ctx.send("An error occurred while fetching the leaderboard.")
            return
        if not top_tokers:
            await ctx.send("The toke leaderboard is currently empty! 💨")
            return

        embed = discord.Embed(title="🏆 Toke Leaderboard 🏆", color=discord.Color.gold())
        description = []
        for i, (user_name, toke_count) in enumerate(top_tokers, 1):
            rank_emoji = ""
            if i == 1: rank_emoji = "🥇 "
            elif i == 2: rank_emoji = "🥈 "
            elif i == 3: rank_emoji = "🥉 "
            else: rank_emoji = "💨 "
            
            description.append(f"{rank_emoji}**{i}. {user_name}**: {toke_count} tokes")
        
        embed.description = "\n".join(description)
        await ctx.send(embed=embed)

    @commands.command(brief="Deletes the toke tracker database (owner only) 💣.")
    @commands.is_owner()
    async def deletetoketracker(self, ctx):
        """Deletes the toker.db file. This action is irreversible."""
        try:
            if os.path.exists(self.db_file):
                await self.bot.loop.run_in_executor(None, os.remove, self.db_file)
                logging.info(f"Database file '{self.db_file}' deleted by {ctx.author.name}.")
                await ctx.send(f"Toke tracker database (`{self.db_file}`) has been deleted. It will be recreated on next use or bot restart.")
                self._initialize_database()
            else:
                await ctx.send(f"Toke tracker database (`{self.db_file}`) does not exist.")
        except Exception as e:
            logging.error(f"Error deleting database file '{self.db_file}': {e}")
            await ctx.send(f"An error occurred while trying to delete the database: {e}")

    def _sync_get_user_stats_from_db(self, user_id: int):
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT user_name, toke_count, solo_toke_count, tokes_saved_count, four_twenty_tokes_count, wake_and_bake_tokes_count FROM toke_stats WHERE user_id = ?", (user_id,))
            return cursor.fetchone()
        except sqlite3.Error as e:
            logging.error(f"Database error in _sync_get_user_stats_from_db for user_id {user_id}: {e}")
            return None
        finally:
            if conn:
                conn.close()

    async def _get_user_stats_from_db(self, user_id: int):
        """Fetches user_name and toke_count for a given user_id from the database."""
        return await self.bot.loop.run_in_executor(None, self._sync_get_user_stats_from_db, user_id)

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
            _db_user_name, toke_count, solo_toke_count, tokes_saved_count, four_twenty_tokes_count, wake_and_bake_tokes_count = user_data
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
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"{target_user.display_name} hasn't participated in any tokes yet, or their stats couldn't be found. 🤷")

async def setup(bot):
    await bot.add_cog(TreesTrackerCog(bot))