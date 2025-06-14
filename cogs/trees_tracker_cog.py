# trees_tracker_cog.py
import discord
from discord.ext import commands
import sqlite3
import logging
import os

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
                toke_count INTEGER NOT NULL DEFAULT 0
            )
        ''')
        conn.commit()
        conn.close()
        logging.info(f"Database '{self.db_file}' initialized and 'toke_stats' table ensured.")

    async def _increment_toke_count_in_db(self, user_id: int, user_name: str):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO toke_stats (user_id, user_name, toke_count) VALUES (?, ?, 0)", (user_id, user_name))
            cursor.execute("UPDATE toke_stats SET toke_count = toke_count + 1, user_name = ? WHERE user_id = ?", (user_name, user_id))
            conn.commit()
            logging.info(f"Incremented toke count for user {user_name} (ID: {user_id}).")
        except sqlite3.Error as e:
            logging.error(f"Database error in _increment_toke_count_in_db: {e}")
        finally:
            if conn:
                conn.close()

    async def user_joined_toke(self, user: discord.User):
        if user.bot: # Don't track bots
            return
        await self._increment_toke_count_in_db(user.id, user.name)

    @commands.command(brief="Displays the toke leaderboard 🏆.")
    async def leaderboard(self, ctx):
        """Displays the top tokers based on their toke count."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            # Fetch users ordered by toke_count descending
            cursor.execute("SELECT user_name, toke_count FROM toke_stats ORDER BY toke_count DESC")
            top_tokers = cursor.fetchall()
            conn.close()

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
                else: rank_emoji = "💨 " # Added fun emoji for other ranks
                
                description.append(f"{rank_emoji}**{i}. {user_name}**: {toke_count} tokes")
            
            embed.description = "\n".join(description)
            await ctx.send(embed=embed)

        except sqlite3.Error as e:
            logging.error(f"Database error in leaderboard command: {e}")
            await ctx.send("An error occurred while fetching the leaderboard.")

    @commands.command(brief="Deletes the toke tracker database (owner only) 💣.")
    @commands.is_owner()
    async def deletetoketracker(self, ctx):
        """Deletes the toker.db file. This action is irreversible."""
        try:
            if os.path.exists(self.db_file):
                os.remove(self.db_file)
                logging.info(f"Database file '{self.db_file}' deleted by {ctx.author.name}.")
                await ctx.send(f"Toke tracker database (`{self.db_file}`) has been deleted. It will be recreated on next use or bot restart.")
                # Re-initialize to create an empty database immediately
                self._initialize_database()
            else:
                await ctx.send(f"Toke tracker database (`{self.db_file}`) does not exist.")
        except Exception as e:
            logging.error(f"Error deleting database file '{self.db_file}': {e}")
            await ctx.send(f"An error occurred while trying to delete the database: {e}")

async def setup(bot):
    await bot.add_cog(TreesTrackerCog(bot))