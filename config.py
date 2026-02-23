"""tgs-downloader configuration.

This project previously had many user-facing strings scattered around the code.
To make maintenance and localization easier, keep *all bot UI text* in
`MESSAGES` below and reference it from the bot code.

Non-text configuration values (paths, limits, logging, etc.) also live here.
"""

# Bot Settings
BOT_VERSION = "2.1"
BOT_NAME = "TGS Emoji Downloader"

# Download Settings
DOWNLOADS_DIR = "downloads"
TEMP_DIR_PREFIX = "temp_pack_"

# Progress Update Settings
PROGRESS_UPDATE_INTERVAL_SMALL = 5  # For packs < 50 stickers
PROGRESS_UPDATE_INTERVAL_LARGE = 10  # For packs >= 50 stickers
PROGRESS_BAR_LENGTH = 10
PROGRESS_UPDATE_MIN_SECONDS = 5  # Minimum seconds between progress updates (increased to allow button clicks)
PACK_SIZE_THRESHOLD = 50  # Sticker count threshold for update interval

# File Size Limits
MAX_ZIP_SIZE_MB = 50  # Telegram bot file size limit
MAX_SINGLE_FILE_SIZE_MB = 20

# Rate Limiting and Concurrency
MAX_PACKS_PER_HOUR = 5
MAX_STICKERS_PER_REQUEST = 100
MAX_CONCURRENT_DOWNLOADS = 5  # Number of parallel downloads
DOWNLOAD_SEMAPHORE_LIMIT = 10  # Max simultaneous network operations

# Logging Settings
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = "INFO"
LOG_FILE = "bot.log"
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT = 5

# Retry Settings
MAX_DOWNLOAD_RETRIES = 3
RETRY_DELAY_SECONDS = 2.0  # Base delay for exponential backoff
RETRY_DELAY_STICKER = 1.0  # Delay for individual sticker retries
RETRY_DELAY_FETCH = 2.0  # Delay for fetching sticker sets/metadata

# Cleanup Settings
AUTO_CLEANUP_ENABLED = True
CLEANUP_DELAY_SECONDS = 5
CLEANUP_AGE_HOURS = 1  # Remove files older than this many hours
CLEANUP_ON_STARTUP = True  # Clean old files when bot starts
CLEANUP_INTERVAL_HOURS = 6  # Run periodic cleanup every N hours

# Disk Space Settings
MIN_FREE_SPACE_MB = 100  # Minimum free space required before downloads
ESTIMATED_STICKER_SIZE_KB = 50  # Average size per sticker for estimation
WARN_LOW_SPACE_MB = 500  # Warn if free space below this threshold
