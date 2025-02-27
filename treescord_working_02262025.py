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

player = None  # Initialize global player variable.

@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user.name}')

@bot.command()
async def play(ctx, *, url: str):
    global player  # Use the global player variable.
    try:
        logging.info(f"Received URL: {url}")
        if "\\" in url:
            url = url.replace("\\", "/")
            logging.info(f"Backslashes replaced: {url}")
        logging.info(f"Converted URL: {url}")
        instance = vlc.Instance()
        player = instance.media_player_new()
        media = instance.media_new(url)
        player.set_media(media)
        try:
            player.play()
        except Exception as play_error:
            logging.error(f"Play Error: {play_error}")
            await ctx.send("Play Error.")
            return

        logging.info(f"VLC state: {player.get_state()}")
        await ctx.send(f'Playing: {url}')
    except Exception as e:
        logging.error(f"General Error: {e}")
        await ctx.send(f'Error playing: {e}')

@bot.command()
async def pause(ctx):
    global player  # Use the global player variable.
    try:
        player.pause()
        logging.info("Playback Paused.")
        await ctx.send("Playback Paused.")
    except Exception as e:
        logging.error(f'Error: {e}')
        await ctx.send(f'Error: {e}')

@bot.command()
async def stop(ctx):
    global player  # Use the global player variable.
    try:
        player.stop()
        logging.info("Playback Stopped.")
        await ctx.send("Playback Stopped.")
    except Exception as e:
        logging.error(f'Error: {e}')
        await ctx.send(f'Error: {e}')

@bot.command()
async def volume(ctx, level: int):
    global player  # Use the global player variable.
    try:
        player.audio_set_volume(level)
        logging.info(f"Volume set to {level}")
        await ctx.send(f"Volume set to {level}")
    except Exception as e:
        logging.error(f"Error: {e}")
        await ctx.send(f"Error: {e}")

@bot.command()
async def mute(ctx):
    global player  # Use the global player variable.
    try:
        player.audio_set_mute(1)
        logging.info("Muted.")
        await ctx.send("Muted.")
    except Exception as e:
        logging.error(f"Error: {e}")
        await ctx.send(f"Error: {e}")

@bot.command()
async def unmute(ctx):
    global player  # Use the global player variable.
    try:
        player.audio_set_mute(0)
        logging.info("Unmuted.")
        await ctx.send("Unmuted.")
    except Exception as e:
        logging.error(f"Error: {e}")
        await ctx.send(f"Error: {e}")

@bot.command()
async def fullscreen(ctx):
    global player  # Use the global player variable.
    try:
        player.set_fullscreen(1)
        logging.info("Fullscreen Enabled")
        await ctx.send("Fullscreen Enabled")
    except Exception as e:
        logging.error(f"Error: {e}")
        await ctx.send(f"Error: {e}")

@bot.command()
async def windowed(ctx):
    global player  # Use the global player variable.
    try:
        player.set_fullscreen(0)
        logging.info("Windowed Mode Enabled")
        await ctx.send("Windowed Mode Enabled")
    except Exception as e:
        logging.error(f"Error: {e}")
        await ctx.send(f"Error: {e}")



bot.run(TOKEN)