
import os

# Database Files
ACHIEVEMENTS_DB = "achievements.db"
MEDIA_DB = "media_library.db"
TOKERS_DB = "tokers.db"

# VLC Settings
VLC_PATH = r"C:\Program Files\VideoLAN\VLC"
VLC_ARGS = [
    "--fullscreen",
    "--audio-language=en",
    "--sub-language=en",
    "--avcodec-hw=auto",
    "--network-caching=2000",
]

# Toke Settings
TOKE_COUNTDOWN_SECONDS = 60
TOKE_COOLDOWN_SECONDS = 240

# Remote Settings
REMOTE_TIMEOUT_SECONDS = 300

# Pagination Settings
MEDIA_PAGE_SIZE = 10
PLAYLIST_PAGE_SIZE = 10
LEADERBOARD_PAGE_SIZE = 10

# Emojis (Replace these unicode characters with your custom emoji IDs if desired)
# Example: GREATER_THAN = "<:next_joint:123456789>"
EMOJIS = {
    "leaf": "🍃",
    "cloud": "☁️",
    "fire": "🔥",
    "trophy": "🏆",
    "medal_1": "🥇",
    "medal_2": "🥈",
    "medal_3": "🥉",
    "check": "✅",
    "cross": "❌",
    "back": "⬅️",
    "next": "➡️",
    "play_pause": "⏯️",
    "stop": "⏹️",
    "rewind": "⏪",
    "forward": "⏩",
    "shuffle": "🔀",
    "repeat": "🔁",
    "list": "📃",
    "phone": "📱",
    "time": "⏳",
    "sun": "☀️",
    "soap": "🧼", # For Toke Club / Fight Club
    "smoke_face": "😶‍🌫️",
    "wind": "💨",
    "maple": "🍁",
    "ring": "💍",
    "gem": "💎",
    "sparkles": "✨",
    "herb": "🌿",
    "pot": "🍯",
    "alembic": "⚗️",
    "boom": "💥",
    "star": "🌟",
    "eagle": "🦅",
    "scroll": "📜",
    "heart_green": "💚",
    "shield": "🛡️",
    "superhero": "🦸",
    "sunrise": "🌅",
    "building": "🏢",
    "cigarette": "🚬"
}
