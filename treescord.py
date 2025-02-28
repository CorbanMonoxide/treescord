import discord
from discord.ext import commands
import vlc
import os
from dotenv import load_dotenv
import logging
import asyncio
import sqlite3

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if TOKEN is None:
    logging.error("DISCORD_TOKEN not found in .env file.")
    exit()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

instance = vlc.Instance("--qt-start-minimized")
media_list = instance.media_list_new()
media_list_player = instance.media_list_player_new()
media_list_player.set_media_list(media_list)
media_list_player.get_media_player().set_fullscreen(1)

DATABASE_FILE = "media_library.db"
shared_playlist = []
current_index = -1

def get_media_library():
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT name, file_path FROM media")
        media_list_data = {name: file_path for name, file_path in cursor.fetchall()}
        conn.close()
        return media_list_data
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return {}

@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user.name}')

@bot.command()
async def play(ctx, *, media_name: str):
    global media_list, media_list_player, current_index
    try:
        logging.info(f"Received media name: {media_name}")
        media_library = get_media_library()
        file_path = media_library.get(media_name)
        if file_path:
            if media_list_player and media_list_player.is_playing() == 1:
                media_list_player.stop()
                await asyncio.sleep(1)

            media_list = instance.media_list_new()
            media_list_player.set_media_list(media_list)

            media = instance.media_new(file_path)
            media_list.add_media(media)

            try:
                media_list_player.play()
            except Exception as play_error:
                logging.error(f"Play Error: {play_error}")
                await ctx.send("Play Error.")
                return

            logging.info(f"VLC state: {media_list_player.get_state()}")
            await ctx.send(f'Playing: {media_name}')
        else:
            await ctx.send(f"Media '{media_name}' not found.")
    except Exception as e:
        logging.error(f"General Error: {e}")
        await ctx.send(f'Error playing: {e}')

@bot.command()
async def list(ctx):
    try:
        media_library = get_media_library()
        media_list_str = "\n".join(media_library.keys())
        await ctx.send(f"Media Library:\n{media_list_str}")
    except Exception as e:
        logging.error(f"Error listing media: {e}")
        await ctx.send(f"Error listing media: {e}")

@bot.command()
async def add(ctx, media_name: str):
    media_library = get_media_library()
    if media_name in media_library:
        shared_playlist.append(media_name)
        await ctx.send(f"Added '{media_name}' to the shared playlist.")
    else:
        await ctx.send(f"Media '{media_name}' not found in the library.")

@bot.command()
async def view(ctx):
    if shared_playlist:
        playlist_str = "\n".join(shared_playlist)
        await ctx.send(f"Shared Playlist:\n{playlist_str}")
    else:
        await ctx.send("The shared playlist is empty.")

@bot.command()
async def clear(ctx):
    global current_index
    shared_playlist.clear()
    current_index = -1
    await ctx.send("The shared playlist has been cleared.")

@bot.command()
async def remove(ctx, media_name: str):
    global current_index
    if media_name in shared_playlist:
        index = shared_playlist.index(media_name)
        shared_playlist.remove(media_name)
        if index <= current_index:
            current_index -= 1
        await ctx.send(f"Removed '{media_name}' from the shared playlist.")
    else:
        await ctx.send(f"'{media_name}' not found in the shared playlist.")

@bot.command()
async def playlist(ctx):
    await view(ctx)

@bot.command()
async def next(ctx):
    global current_index
    if shared_playlist:
        current_index += 1
        if current_index < len(shared_playlist):
            await play(ctx, media_name=shared_playlist[current_index])
        else:
            current_index = len(shared_playlist) - 1
            await ctx.send("End of playlist.")
    else:
        await ctx.send("The shared playlist is empty.")

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
    global media_list_player, current_index
    try:
        media_list_player.stop()
        logging.info("Playback Stopped.")
        await ctx.send("Playback Stopped.")
        current_index = -1
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

bot.run(TOKEN)