# treescord.py
import discord
from discord.ext import commands
import vlc
import os
from dotenv import load_dotenv
import logging

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

instance = vlc.Instance("--qt-start-minimized")

async def setup_hook():
    from cogs.playback_cog import PlaybackCog
    from cogs.playlist_cog import PlaylistCog
    from cogs.database_cog import DatabaseCog
    from cogs.volume_cog import VolumeCog

    # Initialize the cogs
    database_cog = DatabaseCog(bot)
    playlist_cog = PlaylistCog(bot)
    playback_cog = PlaybackCog(bot, instance)
    volume_cog = VolumeCog(bot, instance)

    # Add the cogs to the bot
    await bot.add_cog(database_cog)
    await bot.add_cog(playlist_cog)
    await bot.add_cog(playback_cog)
    await bot.add_cog(volume_cog)

bot.setup_hook = setup_hook

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

    help_embed = discord.Embed(title="Bot Commands", description="List of available commands:")
    categories = {
        "Playback": ["play", "pause", "stop", "status"], # Removed forward, backward, jump
        "Playlist": ["add", "view", "clear", "remove", "next", "restart", "shuffle", "unshuffle"],
        "Media Library": ["list"],
        "Volume": ["volume", "mute", "unmute"]
    }
    for category, commands_list in categories.items():
        command_texts = []
        for cmd_name in commands_list:
            cmd = bot.get_command(cmd_name)
            if cmd:
                command_texts.append(f"**{cmd.name}**: {cmd.brief or 'No description'}")
        if command_texts:
            help_embed.add_field(name=category, value="\n".join(command_texts), inline=False)
    await ctx.send(embed=help_embed)

bot.run(TOKEN)