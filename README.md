# treescord

**Treescord** is a Discord bot designed to create a unique, interactive custom streaming channel experience. It allows users to participate in shared "toke" sessions directly within Discord, complete with countdowns, user tracking, and fun achievements.

Key Features:

-   **Interactive Toke Sessions:** Start and join group tokes with a countdown timer.
-   **Solo Tokes:** Track your personal solo sessions.
-   **Achievement System:** Earn ranks and special badges for participating in tokes, hitting milestones like 4:20 joins, early morning sessions, and more!
-   **User Statistics:** View your personal toke stats and see how you rank on the server leaderboard.
-   **VLC Integration:** Control a custom streaming channel via VLC using bot commands.

Requirements

1.  **Python 3.8+**
2.  **VLC Media Player:** Download and install from [https://www.videolan.org/vlc/](https://www.videolan.org/vlc/).
    *   **Important:** Ensure that the folder containing `libvlc.dll` (on Windows) or the equivalent library for your OS is added to your system's PATH environment variable.
3.  **Python Libraries:** Install the required Python packages using pip:
    ```bash
    pip install discord.py python-dotenv pysqlite3 python-vlc
    ```

## Setup

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/your-username/treescord.git # Replace with your actual repository URL
    cd treescord
    ```

2.  **Create a Discord Bot Application:**
    *   Go to the Discord Developer Portal.
    *   Click "New Application" and give it a name.
    *   Navigate to the "Bot" tab and click "Add Bot".
    *   Under "Privileged Gateway Intents", enable "Server Members Intent" and "Message Content Intent".
    *   Copy the bot's **token** (under the "Bot" tab, click "Reset Token" or "View Token"). **Keep this token secret!**

3.  **Configure Environment Variables:**
    *   Create a file named `.env` in the root directory of the project (`treescord/`).
    *   Add your bot token to this file:
        ```env
        DISCORD_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
        ```

## Running the Bot

Once you have completed the setup steps, you can run the bot using:

```bash
python treescord.py
```

Invite the bot to your Discord server using the OAuth2 URL Generator in the Discord Developer Portal (under the "OAuth2" > "URL Generator" tab). Select the `bot` and `application.commands` scopes, and grant necessary permissions (e.g., Send Messages, Read Message History, etc.).