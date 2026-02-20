
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
