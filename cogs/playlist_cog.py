# playlist_cog.py
import discord
from discord.ext import commands
import logging

class PlaylistCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.shared_playlist = []
        self.current_index = -1

    @commands.command(brief="Adds a media file to the playlist.")
    async def add(self, ctx, media_name: str):
        database_cog = self.bot.get_cog('DatabaseCog')
        if database_cog:
            media_library = database_cog.get_media_library()
            if media_name in media_library:
                self.shared_playlist.append(media_name)
                await ctx.send(f"Added '{media_name}' to the shared playlist.")
            else:
                await ctx.send(f"Media '{media_name}' not found in the library.")
        else:
            await ctx.send("Database cog not loaded.")

    @commands.command(brief="Views the current playlist.")
    async def view(self, ctx):
        if self.shared_playlist:
            playlist_str = "\n".join(self.shared_playlist)
            await ctx.send(f"Shared Playlist:\n{playlist_str}")
        else:
            await ctx.send("The shared playlist is empty.")

    @commands.command(brief="Clears the current playlist.")
    async def clear(self, ctx):
        self.shared_playlist.clear()
        self.current_index = -1
        await ctx.send("The shared playlist has been cleared.")

    @commands.command(brief="Removes a media file from the playlist.")
    async def remove(self, ctx, media_name: str):
        if media_name in self.shared_playlist:
            index = self.shared_playlist.index(media_name)
            self.shared_playlist.remove(media_name)
            if index <= self.current_index:
                self.current_index -= 1
            await ctx.send(f"Removed '{media_name}' from the shared playlist.")
        else:
            await ctx.send(f"'{media_name}' not found in the shared playlist.")

    @commands.command(brief="Displays the playlist.")
    async def playlist(self, ctx):
        await self.view(ctx)

    @commands.command(brief="Plays the next media file in the playlist.")
    async def next(self, ctx):
        if self.shared_playlist:
            self.current_index += 1
            if self.current_index < len(self.shared_playlist):
                playback_cog = self.bot.get_cog('PlaybackCog')
                if playback_cog:
                    await playback_cog.play(ctx, media_name=self.shared_playlist[self.current_index])
                else:
                    await ctx.send("Playback cog not loaded.")
            else:
                self.current_index = len(self.shared_playlist) - 1
                await ctx.send("End of playlist.")
        else:
            await ctx.send("The shared playlist is empty.")