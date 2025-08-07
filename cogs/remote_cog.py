import discord
from discord.ext import commands
import logging

# This View class holds all the buttons and their logic.
class RemoteView(discord.ui.View):
    def __init__(self, bot, *, timeout=300):  # Timeout after 5 minutes of inactivity
        super().__init__(timeout=timeout)
        self.bot = bot
        self.message: discord.Message = None

    async def on_timeout(self):
        """Disables all buttons when the view times out."""
        for item in self.children:
            item.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except discord.NotFound:
                pass  # Message was deleted

    # --- Helper methods to get other cogs ---
    def _get_playback_cog(self):
        return self.bot.get_cog("PlaybackCog")

    def _get_playlist_cog(self):
        return self.bot.get_cog("PlaylistCog")

    def _get_toke_cog(self):
        return self.bot.get_cog("TokeCog")

    async def _get_context(self, interaction: discord.Interaction) -> commands.Context:
        """Creates a context object to pass to commands that require it."""
        # Manually create a context object from the interaction.
        # This is necessary because bot.get_context(interaction) is only for
        # application command interactions, not component interactions.
        # We pass the interaction to the context so that ctx.send() will
        # correctly use interaction.followup.send() after we defer.
        ctx = commands.Context(
            message=interaction.message,
            bot=self.bot,
            view=commands.view.StringView(interaction.message.content),
            interaction=interaction,
        )
        ctx.author = interaction.user  # Set the author to the user who clicked
        return ctx

    # --- Button Callbacks ---

    @discord.ui.button(emoji="⏮️", style=discord.ButtonStyle.secondary, row=0)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        playlist_cog = self._get_playlist_cog()
        if not playlist_cog:
            return await interaction.response.send_message("Playlist system not ready.", ephemeral=True)

        await interaction.response.defer()

        ctx = await self._get_context(interaction)
        previous_command = self.bot.get_command('previous')
        if previous_command:
            await previous_command.callback(playlist_cog, ctx)
        else:
            await interaction.followup.send("Previous command not implemented.", ephemeral=True)

    @discord.ui.button(emoji="⏯️", style=discord.ButtonStyle.primary, row=0)
    async def pause_resume_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        playback_cog = self._get_playback_cog()
        if not (playback_cog and playback_cog.media_player):
            return await interaction.response.send_message("Player not ready.", ephemeral=True)

        # .pause() toggles between play and pause
        playback_cog.media_player.pause()
        status = "paused" if playback_cog.media_player.get_state() == discord.vlc.State.Paused else "resumed"
        await interaction.response.send_message(f"Playback {status}.", ephemeral=True)

    @discord.ui.button(emoji="⏹️", style=discord.ButtonStyle.danger, row=0)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        playback_cog = self._get_playback_cog()
        if not (playback_cog and playback_cog.media_player):
            return await interaction.response.send_message("Player not ready.", ephemeral=True)

        playback_cog.media_player.stop()
        await interaction.response.send_message("Playback stopped.", ephemeral=True)

    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.secondary, row=0)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        playlist_cog = self._get_playlist_cog()
        if not playlist_cog:
            return await interaction.response.send_message("Playlist system not ready.", ephemeral=True)

        await interaction.response.defer()

        ctx = await self._get_context(interaction)
        next_command = self.bot.get_command('next')
        if next_command:
            await next_command.callback(playlist_cog, ctx)
        else:
            await interaction.followup.send("Next command not implemented.", ephemeral=True)

    @discord.ui.button(emoji="🔀", style=discord.ButtonStyle.secondary, row=0)
    async def shuffle_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        playlist_cog = self._get_playlist_cog()
        if not playlist_cog:
            return await interaction.response.send_message("Playlist system not ready.", ephemeral=True)

        await interaction.response.defer()

        ctx = await self._get_context(interaction)
        shuffle_command = self.bot.get_command('shuffle')
        if shuffle_command:
            await shuffle_command.callback(playlist_cog, ctx)
        else:
            await interaction.followup.send("Shuffle command not implemented.", ephemeral=True)

    @discord.ui.button(emoji="📃", style=discord.ButtonStyle.secondary, row=1)
    async def playlist_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        playlist_cog = self._get_playlist_cog()
        if not playlist_cog:
            return await interaction.response.send_message("Playlist system not ready.", ephemeral=True)

        await interaction.response.defer()

        ctx = await self._get_context(interaction)
        playlist_command = self.bot.get_command('playlist')
        if playlist_command:
            await playlist_command.callback(playlist_cog, ctx)
        else:
            await interaction.followup.send("Playlist command not implemented.", ephemeral=True)

    @discord.ui.button(emoji="🍃", style=discord.ButtonStyle.success, row=1)
    async def toke_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        toke_cog = self._get_toke_cog()
        if not toke_cog:
            return await interaction.response.send_message("Toke system not ready.", ephemeral=True)

        await interaction.response.defer()

        ctx = await self._get_context(interaction)
        toke_command = self.bot.get_command('toke')
        if toke_command:
            # The toke command in TokeCog takes ctx as its only argument besides self
            await toke_command.callback(toke_cog, ctx)
        else:
            await interaction.followup.send("Toke command not implemented.", ephemeral=True)


class RemoteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Displays a remote control for the media player 🎮.")
    async def remote(self, ctx: commands.Context):
        """Creates an interactive remote control with buttons."""
        embed = discord.Embed(title="😎😎😎😎🍃🍃🍃🍃😎😎😎😎", description="Media Controls.Toke Button. 'Nuff Said.", color=discord.Color.blue())
        view = RemoteView(self.bot)
        message = await ctx.send(embed=embed, view=view)
        view.message = message  # Store message for timeout handling

    async def create_controller(self, ctx: commands.Context):
        """Alias for the remote command, called from other cogs."""
        await self.remote(ctx)

async def setup(bot):
    await bot.add_cog(RemoteCog(bot))