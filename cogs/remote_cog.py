# remote_cog.py
import discord
from discord.ext import commands
import logging
import asyncio
import vlc

class RemoteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.controller_messages = {}  # Store controller messages and related data

    async def create_controller(self, ctx):
        """Creates a controller message with playback control reactions."""
        description = (
            "Use reactions to control playback:\n"
            "⏮️ - Previous track\n"
            "⏯️ - Pause/Resume playback\n"
            "⏭️ - Next track\n"
            "⏹️ - Stop playback\n"
            "🔀 - Shuffle playlist\n"
            "🎞️ - Show current playback status\n"
            "📃 - Show current playlist\n"
            "🔇 - Mute/Unmute audio\n"
            "🍃 - Join/Start Toke\n"
            "❌ - Close Remote"
        )
        embed = discord.Embed(title="Playback Controller", description=description)
        message = await ctx.send(embed=embed)

        # Add control reactions
        controls = ["⏮️", "⏯️", "⏭️", "⏹️", "🔀", "🎞️", "📃", "🔇", "🍃", "❌"]
        for control in controls:
            await message.add_reaction(control)

        # Store controller message ID and context
        self.controller_messages[message.id] = {"ctx": ctx}
        return message

    async def update_controller(self, message):
        """Updates the controller message with the current playback status."""
        playback_cog = self.bot.get_cog("PlaybackCog")
        if not playback_cog or not playback_cog.media_player or not playback_cog.media_player.get_media():
            embed = discord.Embed(title="Playback Controller", description="Nothing is currently playing.")
            await message.edit(embed=embed)
            return

        try:
            media = playback_cog.media_player.get_media()
            current_time_ms = playback_cog.media_player.get_time()
            total_time_ms = playback_cog.media_player.get_length()

            if total_time_ms <= 0:
                embed = discord.Embed(title="Playback Controller", description="Unable to determine media duration.")
                await message.edit(embed=embed)
                return

            progress_percent = (current_time_ms / total_time_ms) * 100
            bar_length = 20
            filled_length = int(bar_length * current_time_ms // total_time_ms)
            progress_bar = '▓' * filled_length + '░' * (bar_length - filled_length)
            state = "Playing" if playback_cog.media_player.is_playing() else "Paused"
            volume = playback_cog.media_player.audio_get_volume()
            
            # Handle potential NoneType from get_meta
            title = media.get_meta(vlc.Meta.Title)
            if title is None:
                title = "Unknown"

            embed = discord.Embed(title="Playback Controller", color=0x3498db)
            embed.add_field(name="Media", value=title, inline=False)
            embed.add_field(name="Status", value=state, inline=True)
            embed.add_field(name="Volume", value=f"{volume}%", inline=True)
            embed.add_field(name="Progress", value=f"{playback_cog.format_time(current_time_ms)} / {playback_cog.format_time(total_time_ms)} ({progress_percent:.1f}%)", inline=False)
            embed.add_field(name="Progress Bar", value=f"`{progress_bar}`", inline=False)
            await message.edit(embed=embed)
        except Exception as e:
            logging.error(f"Error updating controller: {e}")
            embed = discord.Embed(title="Playback Controller", description=f"Error: {e}")
            await message.edit(embed=embed)

    @commands.command(brief="Creates a playback controller📱.")
    async def remote(self, ctx):
        """Creates a controller message that users can interact with."""
        await self.create_controller(ctx)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Handles playback control reactions."""
        if user.bot:
            return

        message_id = reaction.message.id
        if message_id not in self.controller_messages:
            return

        ctx = self.controller_messages[message_id]["ctx"]
        playback_cog = self.bot.get_cog("PlaybackCog")
        playlist_cog = self.bot.get_cog("PlaylistCog")
        volume_cog = self.bot.get_cog("VolumeCog")

        if not playback_cog:
            return

        if str(reaction.emoji) == "⏮️":  # Previous
            if playlist_cog:
                await playlist_cog.previous(ctx)
            await self.update_controller(reaction.message)
        elif str(reaction.emoji) == "⏯️":  # Pause/Resume
            await playback_cog.pause(ctx)
            await self.update_controller(reaction.message)
        elif str(reaction.emoji) == "⏭️":  # Next
            if playlist_cog:
                await playlist_cog.next(ctx)
            await self.update_controller(reaction.message)
        elif str(reaction.emoji) == "⏹️":  # Stop
            await playback_cog.stop(ctx)
            await self.update_controller(reaction.message)
        elif str(reaction.emoji) == "🔀": # Shuffle
            if playlist_cog:
                await playlist_cog.shuffle(ctx)
            await self.update_controller(reaction.message)
        elif str(reaction.emoji) == "🎞️": # status
            await playback_cog.status(ctx)
            await self.update_controller(reaction.message) # Update controller after status display
        elif str(reaction.emoji) == "📃": # Show playlist
            if playlist_cog:
                await playlist_cog.playlist(ctx)
            # Do not update the controller here as playlist sends its own message.
        elif str(reaction.emoji) == "🔇": # mute/unmute
            if volume_cog:
                if playback_cog.media_player.audio_get_mute() == 0:
                    await volume_cog.mute(ctx)
                else:
                    await volume_cog.unmute(ctx)
            await self.update_controller(reaction.message)
        elif str(reaction.emoji) == "🍃": # Join/Start Toke
            toke_cog = self.bot.get_cog("TokeCog")
            if toke_cog:
                await toke_cog.toke(ctx) # TokeCog.toke sends its own messages
            else:
                await ctx.send("Toke feature is not available.", delete_after=10)
            # Do not update the controller here as toke sends its own message.

        elif str(reaction.emoji) == "❌": # Close Remote
            try:
                await reaction.message.delete()
                if message_id in self.controller_messages:
                    del self.controller_messages[message_id]
            except discord.NotFound:
                logging.warning(f"Remote message {message_id} already deleted or not found.")
            return # Don't try to remove reaction from a deleted message

        await reaction.message.remove_reaction(reaction, user)