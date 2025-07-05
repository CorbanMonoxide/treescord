# d:\Projects\Vibes\treescord\cogs\achievements_cog.py
import discord
from discord.ext import commands
import sqlite3
import logging
import datetime
import os

ACHIEVEMENTS_DB_FILE = "achievements.db"

# Define Achievements
# Each achievement has an id, name, description, emoji,
# the stat it depends on from TreesTrackerCog, and the threshold for that stat.
ACHIEVEMENTS_LIST = [
    # CS:GO + Stoner Themed Group Toke Achievements
    {"id": "cs_group_silver_smoker", "name": "Silver Smoker", "description": "Smoked your way to Silver by joining 1 group toke!", "emoji": "🎉", "criteria_stat": "toke_count", "threshold": 1, "source_cog": "TreesTrackerCog"},
    {"id": "cs_group_silver_elite_toker", "name": "Silver Elite Toker", "description": "Reached Silver Elite Toker status with 5 group tokes!", "emoji": "🥈", "criteria_stat": "toke_count", "threshold": 5, "source_cog": "TreesTrackerCog"},
    {"id": "cs_group_silver_master_blazer", "name": "Silver Master Blazer", "description": "Blazed to Silver Master after 10 group tokes!", "emoji": "🔥", "criteria_stat": "toke_count", "threshold": 10, "source_cog": "TreesTrackerCog"},
    {"id": "cs_group_gold_nova_ganjalord", "name": "Gold Nova Ganjalord", "description": "Crowned Gold Nova Ganjalord for 25 group tokes!", "emoji": "🏆", "criteria_stat": "toke_count", "threshold": 25, "source_cog": "TreesTrackerCog"},
    {"id": "cs_group_gold_master_chief", "name": "Gold Master Chief", "description": "Became a Gold Master Chief with 50 group tokes!", "emoji": "🍁", "criteria_stat": "toke_count", "threshold": 50, "source_cog": "TreesTrackerCog"},
    {"id": "cs_group_distinguished_ganja_guardian", "name": "Distinguished Ganja Guardian", "description": "Guarding the ganja as Distinguished Master, 100 group tokes strong!", "emoji": "🛡️", "criteria_stat": "toke_count", "threshold": 100, "source_cog": "TreesTrackerCog"},
    {"id": "cs_group_legendary_eagle_herbmaster", "name": "Legendary Eagle Herbmaster", "description": "Soared to Legendary Eagle Herbmaster with 200 group tokes!", "emoji": "🦅", "criteria_stat": "toke_count", "threshold": 200, "source_cog": "TreesTrackerCog"},
    {"id": "cs_group_supreme_master_chronicler", "name": "Supreme Master Chronicler", "description": "Chronicling 500 supreme group tokes!", "emoji": "📜", "criteria_stat": "toke_count", "threshold": 500, "source_cog": "TreesTrackerCog"},
    {"id": "cs_group_global_elite_kushlord", "name": "Global Elite Kushlord", "description": "Ascended to Global Elite Kushlord, a legend of 1000 group tokes!", "emoji": "💚", "criteria_stat": "toke_count", "threshold": 1000, "source_cog": "TreesTrackerCog"},

    # Concentrate/Dabbing Themed Solo Toke Achievements
    {"id": "solo_first_dab", "name": "First Dab", "description": "Completed your first solo toke!", "emoji": "🍯", "criteria_stat": "solo_toke_count", "threshold": 1, "source_cog": "TreesTrackerCog"},
    {"id": "solo_extractor", "name": "Extractor", "description": "Reached 5 solo tokes!", "emoji": "⚗️", "criteria_stat": "solo_toke_count", "threshold": 5, "source_cog": "TreesTrackerCog"},
    {"id": "solo_shatter_slinger", "name": "Shatter Slinger", "description": "Completed 10 solo tokes!", "emoji": "💥", "criteria_stat": "solo_toke_count", "threshold": 10, "source_cog": "TreesTrackerCog"},
    {"id": "solo_globetrotter", "name": "Globtrotter", "description": "Completed 25 solo tokes!", "emoji": "🌟", "criteria_stat": "solo_toke_count", "threshold": 25, "source_cog": "TreesTrackerCog"},
    {"id": "solo_terp_technician", "name": "Terp Technician", "description": "Became a Terp Technician after 50 solo tokes!", "emoji": "🌿", "criteria_stat": "solo_toke_count", "threshold": 50, "source_cog": "TreesTrackerCog"},
    {"id": "solo_diamond_dabber", "name": "Diamond Dabber", "description": "Became a Diamond Dabber after 100 solo tokes!", "emoji": "💍", "criteria_stat": "solo_toke_count", "threshold": 100, "source_cog": "TreesTrackerCog"},
    {"id": "solo_live_resin_lord", "name": "Live Resin Lord", "description": "Became a Live Resin Lord after 200 solo tokes!", "emoji": "✨", "criteria_stat": "solo_toke_count", "threshold": 200, "source_cog": "TreesTrackerCog"},
    {"id": "solo_rosin_runner", "name": "Rosin Runner", "description": "Became a Rosin Runner after 500 solo tokes!", "emoji": "💎", "criteria_stat": "solo_toke_count", "threshold": 500, "source_cog": "TreesTrackerCog"},
    {"id": "solo_concentrate_connoisseur", "name": "Concentrate Connoisseur", "description": "Ascended to Concentrate Connoisseur, a legend of 1000 solo tokes!", "emoji": "🌌", "criteria_stat": "solo_toke_count", "threshold": 1000, "source_cog": "TreesTrackerCog"},
    
    # General Achievements
    {"id": "session_saver", "name": "Session Saver", "description": "Saved a toke by joining late!", "emoji": "🦸", "criteria_stat": "tokes_saved_count", "threshold": 1, "source_cog": "TreesTrackerCog"},
    {"id": "four_twenty_enthusiast", "name": "Do you have the time?", "description": "Joined a toke at 4:20!", "emoji": "🍁", "criteria_stat": "four_twenty_tokes_count", "threshold": 1, "source_cog": "TreesTrackerCog"},
    {"id": "wake_and_bake", "name": "Wake and Bake", "description": "Joined a toke between 5 AM and 9 AM!", "emoji": "☀️", "criteria_stat": "wake_and_bake_tokes_count", "threshold": 1, "source_cog": "TreesTrackerCog"},

    #Hidden Achievements
    {"id": "early_riser", "name": "I'm a Joker!", "description": "Successfully started a toke during cooldown!", "emoji": "🌅", "hidden": True, "source_cog": "TokeCogEvent"}, # Hidden Achievement
    {"id": "too_slow_421", "name": "You're Too Slow!", "description": "Joined a toke that started at 4:21!", "emoji": "💨", "hidden": True, "source_cog": "TokeCogEvent"},
    {"id": "secret_society", "name": "His Name was Robert Paulson", "description": "Joined Toke Club! Regain your humanity after the dehumanization caused by the consumerist society.", "emoji": "🏢", "hidden": True, "source_cog": "TokeCogEvent"},
]

class AchievementsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_file = ACHIEVEMENTS_DB_FILE
        self._initialize_database()

    def _initialize_database(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_achievements (
                user_id INTEGER NOT NULL,
                achievement_id TEXT NOT NULL,
                timestamp_earned DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, achievement_id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS earlytoke_attempts (
                user_id INTEGER PRIMARY KEY,
                attempts INTEGER DEFAULT 0
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS earlytoke_lifetime (
                user_id INTEGER PRIMARY KEY,
                count INTEGER DEFAULT 0
            )
        ''')
        conn.commit()
        conn.close()
        logging.info(f"Database '{self.db_file}' initialized and tables ensured.")

    def _sync_has_achievement(self, user_id: int, achievement_id: str):
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM user_achievements WHERE user_id = ? AND achievement_id = ?", (user_id, achievement_id))
            return cursor.fetchone() is not None
        except sqlite3.Error as e:
            logging.error(f"DB error in _sync_has_achievement for user {user_id}, achievement {achievement_id}: {e}")
            return False # Assume not earned on error to prevent re-awarding issues
        finally:
            if conn:
                conn.close()

    async def _has_achievement(self, user_id: int, achievement_id: str):
        return await self.bot.loop.run_in_executor(None, self._sync_has_achievement, user_id, achievement_id)

    def _sync_award_achievement(self, user_id: int, achievement_id: str):
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO user_achievements (user_id, achievement_id) VALUES (?, ?)", (user_id, achievement_id))
            conn.commit()
            return cursor.rowcount > 0 # Returns true if a row was inserted
        except sqlite3.Error as e:
            logging.error(f"DB error in _sync_award_achievement for user {user_id}, achievement {achievement_id}: {e}")
            return False
        finally:
            if conn:
                conn.close()

    async def _award_achievement(self, user_id: int, achievement_id: str):
        return await self.bot.loop.run_in_executor(None, self._sync_award_achievement, user_id, achievement_id)

    async def check_and_award_achievements(self, user: discord.User, ctx_to_notify: commands.Context = None):
        if user.bot:
            return

        trees_tracker_cog = self.bot.get_cog("TreesTrackerCog")
        if not trees_tracker_cog:
            logging.warning("TreesTrackerCog not found, cannot check achievements.")
            return

        user_stats_tuple = await trees_tracker_cog._get_user_stats_from_db(user.id)
        if not user_stats_tuple:
            return # No stats for this user yet

        # Unpack stats based on the known order from TreesTrackerCog
        # _db_user_name, toke_count, solo_toke_count, tokes_saved_count, four_twenty_tokes_count, wake_and_bake_tokes_count
        user_stats_map = {
            "toke_count": user_stats_tuple[1],
            "solo_toke_count": user_stats_tuple[2],
            "tokes_saved_count": user_stats_tuple[3],
            "four_twenty_tokes_count": user_stats_tuple[4],
            "wake_and_bake_tokes_count": user_stats_tuple[5] if len(user_stats_tuple) > 5 else 0,
        }

        for ach in ACHIEVEMENTS_LIST:
            if ach["source_cog"] == "TreesTrackerCog": # For now, all are from here
                user_stat_value = user_stats_map.get(ach["criteria_stat"], 0)
                
                if user_stat_value >= ach["threshold"]:
                    if not await self._has_achievement(user.id, ach["id"]):
                        awarded = await self._award_achievement(user.id, ach["id"])
                        if awarded and ctx_to_notify:
                            try:
                                await ctx_to_notify.send(
                                    f"🏆 Achievement Unlocked! {user.mention} earned **{ach['name']}**! {ach['emoji']}\n"
                                    f"> *{ach['description']}*"
                                )
                                logging.info(f"User {user.name} (ID: {user.id}) earned achievement: {ach['name']}")
                            except discord.HTTPException as e:
                                logging.error(f"Failed to send achievement notification for {user.name}: {e}")
                        elif awarded: # Awarded but no context to notify (e.g. background check)
                             logging.info(f"User {user.name} (ID: {user.id}) earned achievement (no ctx): {ach['name']}")

    async def user_triggered_early_toke(self, user: discord.User, ctx_to_notify: commands.Context):
        """Awards the 'Early Riser!' achievement if not already earned."""
        if user.bot:
            return
        
        achievement_id = "early_riser"
        ach_details = next((ach for ach in ACHIEVEMENTS_LIST if ach["id"] == achievement_id), None)

        if not ach_details:
            logging.error(f"Achievement details for '{achievement_id}' not found in ACHIEVEMENTS_LIST.")
            return

        already_has = await self._has_achievement(user.id, achievement_id)
        logging.info(f"Checking if user {user.id} already has 'early_riser': {already_has}")
        if not already_has:
            awarded = await self._award_achievement(user.id, achievement_id)
            logging.info(f"Awarded 'early_riser' to user {user.id}: {awarded}")
            if awarded and ctx_to_notify:
                try:
                    await ctx_to_notify.send(
                        f"🏆 Hidden Achievement Unlocked! {user.mention} earned **{ach_details['name']}**! {ach_details['emoji']}\n"
                        f"> *{ach_details['description']}*"
                    )
                    logging.info(f"User {user.name} (ID: {user.id}) earned hidden achievement: {ach_details['name']}")
                except Exception as e:
                    logging.error(f"Failed to send hidden achievement notification for {user.name}: {e}")
            elif awarded:
                logging.info(f"User {user.name} (ID: {user.id}) earned hidden achievement (no ctx): {ach_details['name']}")
        else:
            logging.info(f"User {user.id} already has 'early_riser', no notification sent.")

    async def user_joined_421_toke_late(self, user: discord.User, ctx_to_notify: commands.Context):
        """Awards the 'You're Too Slow!' achievement if not already earned."""
        if user.bot:
            return

        achievement_id = "too_slow_421"
        ach_details = next((ach for ach in ACHIEVEMENTS_LIST if ach["id"] == achievement_id), None)

        if not ach_details:
            logging.error(f"Achievement details for '{achievement_id}' not found in ACHIEVEMENTS_LIST.")
            return

        if not await self._has_achievement(user.id, achievement_id):
            awarded = await self._award_achievement(user.id, achievement_id)
            if awarded and ctx_to_notify:
                try:
                    await ctx_to_notify.send(
                        f"🏆 Hidden Achievement Unlocked! {user.mention} earned **{ach_details['name']}**! {ach_details['emoji']}\n"
                        f"> *{ach_details['description']}*"
                    )
                    logging.info(f"User {user.name} (ID: {user.id}) earned hidden achievement: {ach_details['name']}")
                except discord.HTTPException as e:
                    logging.error(f"Failed to send hidden achievement notification for {user.name}: {e}")

    async def user_joined_secret_society(self, user: discord.User, ctx_to_notify: commands.Context):
        """Awards the 'Secret Society' achievement if not already earned."""
        if user.bot:
            return
        achievement_id = "secret_society"
        ach_details = next((ach for ach in ACHIEVEMENTS_LIST if ach["id"] == achievement_id), None)
        if not ach_details:
            logging.error(f"Achievement details for '{achievement_id}' not found in ACHIEVEMENTS_LIST.")
            return
        if not await self._has_achievement(user.id, achievement_id):
            awarded = await self._award_achievement(user.id, achievement_id)
            if awarded and ctx_to_notify:
                try:
                    await ctx_to_notify.send(
                        f"🏆 Hidden Achievement Unlocked! {user.mention} earned **{ach_details['name']}**! {ach_details['emoji']}\n"
                        f"> *{ach_details['description']}*"
                    )
                    logging.info(f"User {user.name} (ID: {user.id}) earned hidden achievement: {ach_details['name']}")
                except discord.HTTPException as e:
                    logging.error(f"Failed to send hidden achievement notification for {user.name}: {e}")

    def _sync_get_user_earned_achievements(self, user_id: int):
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            # Order by timestamp to show them in earned order, or by name if preferred
            cursor.execute("SELECT achievement_id FROM user_achievements WHERE user_id = ? ORDER BY timestamp_earned ASC", (user_id,))
            return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logging.error(f"DB error in _sync_get_user_earned_achievements for user {user_id}: {e}")
            return []
        finally:
            if conn:
                conn.close()

    async def _get_user_earned_achievements(self, user_id: int):
        return await self.bot.loop.run_in_executor(None, self._sync_get_user_earned_achievements, user_id)

    def _sync_get_earlytoke_attempts(self, user_id: int):
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS earlytoke_attempts (
                    user_id INTEGER PRIMARY KEY,
                    attempts INTEGER DEFAULT 0
                )
            ''')
            cursor.execute("SELECT attempts FROM earlytoke_attempts WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            return row[0] if row else 0
        except sqlite3.Error as e:
            logging.error(f"DB error in _sync_get_earlytoke_attempts for user {user_id}: {e}")
            return 0
        finally:
            if conn:
                conn.close()

    async def get_earlytoke_attempts(self, user_id: int):
        return await self.bot.loop.run_in_executor(None, self._sync_get_earlytoke_attempts, user_id)

    def _sync_increment_earlytoke_attempts(self, user_id: int):
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO earlytoke_attempts (user_id, attempts) VALUES (?, 1)
                ON CONFLICT(user_id) DO UPDATE SET attempts = attempts + 1
            ''', (user_id,))
            conn.commit()
        except sqlite3.Error as e:
            logging.error(f"DB error in _sync_increment_earlytoke_attempts for user {user_id}: {e}")
        finally:
            if conn:
                conn.close()

    async def increment_earlytoke_attempts(self, user_id: int):
        await self.bot.loop.run_in_executor(None, self._sync_increment_earlytoke_attempts, user_id)

    def _sync_reset_earlytoke_attempts(self, user_id: int):
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE earlytoke_attempts SET attempts = 0 WHERE user_id = ?
            ''', (user_id,))
            conn.commit()
        except sqlite3.Error as e:
            logging.error(f"DB error in _sync_reset_earlytoke_attempts for user {user_id}: {e}")
        finally:
            if conn:
                conn.close()

    async def reset_earlytoke_attempts(self, user_id: int):
        await self.bot.loop.run_in_executor(None, self._sync_reset_earlytoke_attempts, user_id)

    def _sync_increment_earlytoke_lifetime(self, user_id: int):
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO earlytoke_lifetime (user_id, count) VALUES (?, 1)
                ON CONFLICT(user_id) DO UPDATE SET count = count + 1
            ''', (user_id,))
            conn.commit()
        except sqlite3.Error as e:
            logging.error(f"DB error in _sync_increment_earlytoke_lifetime for user {user_id}: {e}")
        finally:
            if conn:
                conn.close()

    async def increment_earlytoke_lifetime(self, user_id: int):
        await self.bot.loop.run_in_executor(None, self._sync_increment_earlytoke_lifetime, user_id)

    def _sync_get_earlytoke_lifetime(self, user_id: int):
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS earlytoke_lifetime (
                    user_id INTEGER PRIMARY KEY,
                    count INTEGER DEFAULT 0
                )
            ''')
            cursor.execute("SELECT count FROM earlytoke_lifetime WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            return row[0] if row else 0
        except sqlite3.Error as e:
            logging.error(f"DB error in _sync_get_earlytoke_lifetime for user {user_id}: {e}")
            return 0
        finally:
            if conn:
                conn.close()

    async def get_earlytoke_lifetime(self, user_id: int):
        return await self.bot.loop.run_in_executor(None, self._sync_get_earlytoke_lifetime, user_id)

    @commands.group(invoke_without_command=True, brief="Displays your or another user's earned achievements 🏆. Usage: !achievements [@user]")
    async def achievements(self, ctx, member: discord.Member = None):
        """Displays earned toking achievements. Use '!achievements list' to see all available achievements."""
        if ctx.invoked_subcommand is None:  # Display user's achievements if no subcommand is called
            target_user = member or ctx.author

            earned_ids = await self._get_user_earned_achievements(target_user.id)

            embed = discord.Embed(
                title=f"🏆 Achievements for {target_user.display_name} 🏆",
                color=discord.Color.gold()
            )
            embed.set_thumbnail(url=target_user.display_avatar.url)

            if not earned_ids:
                embed.description = "No achievements earned yet. Keep toking!"
            else:
                description_lines = []
                for ach_id in earned_ids:
                    ach_details = next((ach for ach in ACHIEVEMENTS_LIST if ach["id"] == ach_id), None)
                    if ach_details:
                        description_lines.append(f"{ach_details['emoji']} **{ach_details['name']}**: {ach_details['description']}")
                    else:
                        description_lines.append(f"❓ **Unknown Achievement**: ID `{ach_id}`") # Fallback
                embed.description = "\n\n".join(description_lines)
            
            await ctx.send(embed=embed)

    @achievements.command(name="list", brief="Lists all available achievements and their requirements.")
    async def list_achievements(self, ctx):
        """Displays a list of all available achievements and how to earn them."""
        embed = discord.Embed(
            title="📜 All Available Achievements 📜",
            description="Here are all the achievements you can earn:",
            color=discord.Color.blue()
        )

        for ach in ACHIEVEMENTS_LIST:
            if not ach.get("hidden", False): # Only list non-hidden achievements
                criteria_text = ""
                if ach.get("source_cog") == "TreesTrackerCog" and ach.get("criteria_stat"):
                    stat_key = ach["criteria_stat"]
                    threshold = ach["threshold"]
                    if stat_key == "toke_count":
                        criteria_text = f"Earn by joining {threshold} group toke{'s' if threshold > 1 else ''}."
                    elif stat_key == "solo_toke_count":
                        criteria_text = f"Earn by completing {threshold} solo toke{'s' if threshold > 1 else ''}."
                    elif stat_key == "tokes_saved_count":
                        criteria_text = f"Earn by saving {threshold} toke session{'s' if threshold > 1 else ''}."
                    elif stat_key == "four_twenty_tokes_count":
                        criteria_text = f"Earn by joining {threshold} 4:20 toke{'s' if threshold > 1 else ''}."
                    elif stat_key == "wake_and_bake_tokes_count":
                        criteria_text = f"Join a toke between 5 AM and 9 AM ({threshold} time{'s' if threshold > 1 else ''})."
                    else: # Fallback for any other stats
                        stat_name = stat_key.replace('_', ' ').title()
                        criteria_text = f"Earn by reaching {threshold} {stat_name}."
                
                embed.add_field(name=f"{ach['emoji']} {ach['name']}", 
                                value=f"*{ach['description']}*\n{criteria_text}", 
                                inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="wipe", brief="[Admin Only] Wipes achievements for a user or all users. Usage: !wipe [@user|all]")
    @commands.has_permissions(administrator=True)
    async def wipe_achievements(self, ctx, target: discord.Member = None):
        """Wipes achievements for a specific user or all users (admin only). Usage: !wipe [@user|all]"""
        if target is None and (ctx.message.content.strip().endswith('all') or ctx.message.content.strip().endswith('all>')):
            # Wipe all users
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_achievements")
            conn.commit()
            conn.close()
            await ctx.send("All achievements have been wiped for all users.")
            logging.info(f"Admin {ctx.author} wiped all achievements.")
        elif target is not None:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_achievements WHERE user_id = ?", (target.id,))
            conn.commit()
            conn.close()
            await ctx.send(f"All achievements have been wiped for {target.display_name}.")
            logging.info(f"Admin {ctx.author} wiped achievements for user {target.display_name} (ID: {target.id}).")
        else:
            await ctx.send("Usage: !wipe [@user|all]")

    @commands.command(name="odds", brief="Shows how many earlytoke attempts a user has made. Usage: !odds [@user]")
    async def odds(self, ctx, member: discord.Member = None):
        """Shows how many earlytoke attempts a user has made. Usage: !odds [@user]"""
        target_user = member or ctx.author
        attempts = await self.get_earlytoke_attempts(target_user.id)
        await ctx.send(f"{target_user.display_name} has attempted !earlytoke {attempts} time(s) since their last successful early toke.")

    @commands.command(name="earlytokelife", brief="Shows how many lifetime early tokes a user has completed. Usage: !earlytokelife [@user]")
    async def earlytokelife(self, ctx, member: discord.Member = None):
        """Shows how many lifetime early tokes a user has completed. Usage: !earlytokelife [@user]"""
        target_user = member or ctx.author
        count = await self.get_earlytoke_lifetime(target_user.id)
        await ctx.send(f"{target_user.display_name} has completed {count} lifetime early tokes.")

async def setup(bot):
    await bot.add_cog(AchievementsCog(bot))
