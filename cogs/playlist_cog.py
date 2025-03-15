# playlist_cog.py
import discord
from discord.ext import commands
import logging

# Function to normalize media names
def normalize_media_name(media_name):
    # Remove special characters and convert to lowercase
    return media_name.lower().strip()

class PlaylistCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.shared_playlist = []  # Stores tuples of (normalized_name, file_path)
        self.current_index = -1

    @commands.command(brief="Adds a media file to the playlist.")
    async def add(self, ctx, media_name: str):
        database_cog = self.bot.get_cog('DatabaseCog')
        if database_cog:
            media_library = database_cog.get_media_library()
            if media_name in media_library:
                file_path = media_library[media_name]
                normalized_name = normalize_media_name(media_name)
                self.shared_playlist.append((normalized_name, file_path))
                await ctx.send(f"Added '{media_name}' to the shared playlist.")
            else:
                await ctx.send(f"Media '{media_name}' not found in the library.")
        else:
            await ctx.send("Database cog not loaded.")

    @commands.command(brief="Views the current playlist.")
    async def view(self, ctx):
        """
        Displays the current playlist, splitting the output into multiple messages if necessary.
        """
        if not self.shared_playlist:
            await ctx.send("The shared playlist is empty.")
            return

        # Split the playlist into chunks of 20 items each
        chunk_size = 20  # Reduced chunk size to stay under 2,000 characters
        chunks = [self.shared_playlist[i:i + chunk_size] for i in range(0, len(self.shared_playlist), chunk_size)]

        # Send each chunk as a separate message
        for i, chunk in enumerate(chunks):
            playlist_str = "\n".join([name for name, _ in chunk])
            await ctx.send(f"Shared Playlist (Part {i + 1}):\n{playlist_str}")

    @commands.command(brief="Clears the current playlist.")
    async def clear(self, ctx):
        self.shared_playlist.clear()
        self.current_index = -1
        await ctx.send("The shared playlist has been cleared.")

    @commands.command(brief="Removes a media file from the playlist.")
    async def remove(self, ctx, media_name: str):
        normalized_name = normalize_media_name(media_name)
        for item in self.shared_playlist:
            if item[0] == normalized_name:
                self.shared_playlist.remove(item)
                if self.shared_playlist:
                    self.current_index = min(self.current_index, len(self.shared_playlist) - 1)
                await ctx.send(f"Removed '{media_name}' from the shared playlist.")
                return
        await ctx.send(f"'{media_name}' not found in the shared playlist.")

    @commands.command(brief="Plays the next media file in the playlist.")
    async def next(self, ctx):
        if self.shared_playlist:
            self.current_index += 1
            if self.current_index < len(self.shared_playlist):
                playback_cog = self.bot.get_cog('PlaybackCog')
                if playback_cog:
                    _, file_path = self.shared_playlist[self.current_index]
                    await playback_cog.play(ctx, file_path=file_path)
                else:
                    await ctx.send("Playback cog not loaded.")
            else:
                self.current_index = len(self.shared_playlist) - 1
                await ctx.send("End of playlist.")
        else:
            await ctx.send("The shared playlist is empty.")

    @commands.command(brief="Restarts the shared playlist from the beginning.")
    async def restart(self, ctx):
        """
        Restarts the shared playlist from the beginning.
        """
        if not self.shared_playlist:
            await ctx.send("The shared playlist is empty.")
            return

        # Reset the current index to 0
        self.current_index = 0

        # Play the first item in the playlist
        playback_cog = self.bot.get_cog('PlaybackCog')
        if playback_cog:
            _, file_path = self.shared_playlist[self.current_index]
            await playback_cog.play(ctx, file_path=file_path)
        else:
            await ctx.send("Playback cog not loaded.")