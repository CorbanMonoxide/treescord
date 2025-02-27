import discord
from discord.ext import commands
import vlc
import os
from dotenv import load_dotenv
import logging
import asyncio

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if TOKEN is None:
    logging.error("DISCORD_TOKEN not found in .env file.")
    exit()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

player = None
instance = None
media_list = None
media_list_player = None

@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user.name}')

@bot.command()
async def play(ctx, *, url: str):
    global player, instance, media_list, media_list_player
    try:
        logging.info(f"Received URL: {url}")
        if "\\" in url:
            url = url.replace("\\", "/")
            logging.info(f"Backslashes replaced: {url}")
        logging.info(f"Converted URL: {url}")

        async def stop_player():
            if media_list_player:
                media_list_player.stop()

        if media_list_player is not None:
            await asyncio.to_thread(stop_player)
            await asyncio.sleep(1)

        if instance is None: #check if instance exists.
            instance = vlc.Instance("--qt-start-minimized")

        media_list = instance.media_list_new()
        media = instance.media_new(url)
        media_list.add_media(media)

        if media_list_player is None: #check if media_list_player exists.
            media_list_player = instance.media_list_player_new()

        media_list_player.set_media_list(media_list)

        try:
            media_list_player.play()
        except Exception as play_error:
            logging.error(f"Play Error: {play_error}")
            await ctx.send("Play Error.")
            return

        logging.info(f"VLC state: {media_list_player.get_state()}")
        await ctx.send(f'Playing: {url}')
    except Exception as e:
        logging.error(f"General Error: {e}")
        await ctx.send(f'Error playing: {e}')

@bot.command()
async def add(ctx, *, url: str):
    global player, instance, media_list, media_list_player
    try:
        logging.info(f"Adding URL: {url}")
        if "\\" in url:
            url = url.replace("\\", "/")
            logging.info(f"Backslashes replaced: {url}")
        logging.info(f"Converted URL: {url}")
        if media_list is None:
            logging.error("No playlist instance. Use !play first.")
            await ctx.send("No playlist instance. Use !play first.")
            return

        media = instance.media_new(url)
        media_list.add_media(media)
        if media_list_player and media_list_player.is_playing() == 0:
            media_list_player.play()
        await ctx.send(f"Added {url} to the playlist.")
    except Exception as e:
        logging.error(f"Error adding: {e}")
        await ctx.send(f"Error adding: {e}")

@bot.command()
async def pause(ctx):
    global media_list_player
    try:
        media_list_player.pause()
        logging.info("Playback Paused.")
        await ctx.send("Playback Paused.")
    except Exception as e:
        logging.error(f'Error: {e}')
        await ctx.send(f'Error: {e}')

@bot.command()
async def stop(ctx):
    global media_list_player
    try:
        media_list_player.stop()
        logging.info("Playback Stopped.")
        await ctx.send("Playback Stopped.")
    except Exception as e:
        logging.error(f'Error: {e}')
        await ctx.send(f'Error: {e}')

@bot.command()
async def volume(ctx, level: int):
    global media_list_player
    try:
        media_list_player.get_media_player().audio_set_volume(level)
        logging.info(f"Volume set to {level}")
        await ctx.send(f"Volume set to {level}")
    except Exception as e:
        logging.error(f"Error: {e}")
        await ctx.send(f"Error: {e}")

@bot.command()
async def mute(ctx):
    global media_list_player
    try:
        media_list_player.get_media_player().audio_set_mute(1)
        logging.info("Muted.")
        await ctx.send("Muted.")
    except Exception as e:
        logging.error(f"Error: {e}")
        await ctx.send(f"Error: {e}")

@bot.command()
async def unmute(ctx):
    global media_list_player
    try:
        media_list_player.get_media_player().audio_set_mute(0)
        logging.info("Unmuted.")
        await ctx.send("Unmuted.")
    except Exception as e:
        logging.error(f"Error: {e}")
        await ctx.send(f"Error: {e}")

@bot.command()
async def fullscreen(ctx):
    global media_list_player
    try:
        media_list_player.get_media_player().set_fullscreen(1)
        logging.info("Fullscreen Enabled")
        await ctx.send("Fullscreen Enabled")
    except Exception as e:
        logging.error(f"Error: {e}")
        await ctx.send(f"Error: {e}")

@bot.command()
async def windowed(ctx):
    global media_list_player
    try:
        media_list_player.get_media_player().set_fullscreen(0)
        logging.info("Windowed Mode Enabled")
        await ctx.send("Windowed Mode Enabled")
    except Exception as e:
        logging.error(f"Error: {e}")
        await ctx.send(f"Error: {e}")

bot.run(TOKEN)