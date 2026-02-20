import discord
from discord.ext import commands
import vlc
import os
import subprocess
from dotenv import load_dotenv
import logging
import config

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if TOKEN is None:
    logging.error("DISCORD_TOKEN not found in .env file.")
    exit()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Disable the default help command
bot.remove_command('help')

def refresh_vlc_plugin_cache():
    """
    Attempts to run vlc-cache-gen.exe to clear stale plugin warnings.
    """
    vlc_path = config.VLC_PATH
    cache_gen_exe = os.path.join(vlc_path, "vlc-cache-gen.exe")
    plugins_path = os.path.join(vlc_path, "plugins")

    if os.path.exists(cache_gen_exe) and os.path.exists(plugins_path):
        try:
            logging.info("Attempting to refresh VLC plugin cache...")
            # Run the command. capture_output=True prevents it from spamming the console if it works.
            subprocess.run([cache_gen_exe, plugins_path], check=True, capture_output=True)
            logging.info("VLC plugin cache refreshed successfully.")
        except subprocess.CalledProcessError as e:
            logging.warning(f"Failed to refresh VLC plugin cache (Access Denied?): {e}")
        except Exception as e:
            logging.warning(f"Error running vlc-cache-gen: {e}")
    else:
        logging.warning("vlc-cache-gen.exe or plugins folder not found. Skipping cache refresh.")

instance = None
try:
    # Attempt to refresh cache before creating instance
    refresh_vlc_plugin_cache()

    # Add hardware acceleration and other performance-related flags.
    vlc_args = config.VLC_ARGS
    instance = vlc.Instance(*vlc_args)
    logging.info(f"VLC instance created successfully with args: {' '.join(vlc_args)}")
except Exception as e:
    logging.error(f"Fatal: Failed to create VLC instance: {e}")
    logging.error("The bot cannot run without a VLC instance. Please ensure VLC is installed correctly.")
    # We don't exit here to allow the bot to run for development/testing of other features, 
    # but playback won't work.
    
async def setup_hook():
    from cogs.playback_cog import PlaybackCog
    from cogs.playlist_cog import PlaylistCog
    from cogs.database_cog import DatabaseCog
    from cogs.volume_cog import VolumeCog
    from cogs.toke_cog import TokeCog
    from cogs.remote_cog import RemoteCog
    from cogs.trees_tracker_cog import TreesTrackerCog
    from cogs.achievements_cog import AchievementsCog

    # Initialize the cogs
    database_cog = DatabaseCog(bot)
    playlist_cog = PlaylistCog(bot)
    playback_cog = PlaybackCog(bot, instance)  # Pass the instance.
    volume_cog = VolumeCog(bot)
    toke_cog = TokeCog(bot)
    remote_cog = RemoteCog(bot)
    trees_tracker_cog = TreesTrackerCog(bot)
    achievements_cog = AchievementsCog(bot)

    # Add the cogs to the bot
    await bot.add_cog(database_cog)
    await bot.add_cog(playlist_cog)
    await bot.add_cog(playback_cog)
    await bot.add_cog(volume_cog)
    await bot.add_cog(toke_cog)
    await bot.add_cog(remote_cog)
    await bot.add_cog(trees_tracker_cog)
    await bot.add_cog(achievements_cog)

    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        logging.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logging.error(f"Failed to sync commands: {e}")

bot.setup_hook = setup_hook

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command.")
    else:
        logging.error(f"Unhandled command error: {error}", exc_info=True)
        await ctx.send(f"An error occurred: {error}")

@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user.name}')

@bot.command()
async def help(ctx, command_name=None):
    if command_name:
        command = bot.get_command(command_name)
        if command:
            help_text = f"**{command.name}**: {command.help or command.brief or 'No description available.'}"
            await ctx.send(help_text)
        else:
            await ctx.send("Command not found.")
        return

    help_embed = discord.Embed(title="Bot Commands", description="📃List of available commands:)")
    categories = {
        "Playback": ["!play", "!pause", "!stop", "!status", "!forward", "!rewind"],
        "Volume": ["!volume", "!mute", "!unmute"],
        "Playlist": ["!playlist", "!add", "!clear", "!next", "!previous", "!jump", "!shuffle", "!unshuffle"],
        "Media Library": ["!media or !list"],
        "Toke": ["!toke", "!leaderboard", "!l8toke", "!earlytoke"],
        "Stats & Achievements": ["!stats", "!achievements"],
        "Remote Control": ["!remote"]
    }
    for category, commands_list in categories.items():
        command_texts = []
        for cmd_name_with_prefix in commands_list:
            # Extract the actual command name by removing the "!" prefix
            actual_cmd_name = cmd_name_with_prefix[1:]
            cmd = bot.get_command(actual_cmd_name)
            if cmd:
                command_texts.append(f"**{cmd_name_with_prefix}**: {cmd.brief or 'No description'}")
        if command_texts:
            help_embed.add_field(name=category, value="\n".join(command_texts), inline=False)
    await ctx.send(embed=help_embed)


@bot.command()
@commands.is_owner()
async def getemojis(ctx):
    """Lists all custom emojis available to the server."""
    emojis = [f"{e.name}: {str(e)}" for e in ctx.guild.emojis]
    if not emojis:
        await ctx.send("No custom emojis found in this server!")
        return

    # Send in chunks to avoid message limit
    chunk_size = 1900
    current_chunk = "```\n"
    for line in emojis:
        if len(current_chunk) + len(line) + 1 > chunk_size:
            current_chunk += "```"
            await ctx.send(current_chunk)
            current_chunk = "```\n"
        current_chunk += line + "\n"

    if len(current_chunk) > 4: # check if chunk has content besides ```\n
         current_chunk += "```"
         await ctx.send(current_chunk)

bot.run(TOKEN)