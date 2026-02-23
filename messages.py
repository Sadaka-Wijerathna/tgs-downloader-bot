"""
messages.py — All user-facing strings for the TGS Emoji Downloader bot.

Edit text here without touching any bot logic in bot.py.
Strings that need runtime values use str.format() placeholders: {variable}.
"""


class MSG:
    # ------------------------------------------------------------------ #
    #  /start                                                              #
    # ------------------------------------------------------------------ #
    START = (
        "👋 <b>Welcome to TGS Emoji Downloader!</b>\n\n"
        "🎯 <b>What I can do:</b>\n"
        "• Convert animated stickers to TGS files\n"
        "• Download animated custom emojis 🌟\n"
        "• Bulk download entire emoji packs as ZIP 📦\n\n"
        "🚀 <b>Quick Start:</b>\n"
        "1️⃣ Send me an animated sticker or custom emoji\n"
        "2️⃣ Or send an emoji pack URL\n"
        "   <code>t.me/addemoji/PackName</code>\n"
        "3️⃣ Get your TGS files instantly!\n\n"
        "💡 <i>TGS = Telegram's animated sticker format (Lottie-based)</i>\n\n"
        "Try it now! Send me something animated! 🎉"
    )

    # ------------------------------------------------------------------ #
    #  /help                                                               #
    # ------------------------------------------------------------------ #
    HELP = (
        "📚 <b>Help &amp; User Guide</b>\n\n"
        "🫧 <b>Commands:</b>\n"
        "/start - Welcome message &amp; quick start\n"
        "/help - Show this help guide\n"
        "/about - Bot information &amp; features\n\n"
        "🎯 <b>What I Support:</b>\n"
        "✅ Animated stickers (TGS format)\n"
        "✅ Animated custom emojis (Premium) 🌟\n"
        "✅ Entire emoji packs (as ZIP) 📦\n"
        "❌ Static stickers/images\n"
        "❌ Regular text emojis\n\n"
        "📝 <b>How to Use:</b>\n\n"
        "<b>1️⃣ Single Stickers/Emojis:</b>\n"
        "Just send any animated sticker or custom emoji.\n"
        "I'll instantly send you the TGS file!\n\n"
        "<b>2️⃣ Emoji Packs (Bulk Download):</b>\n"
        "Send me a pack URL in any of these formats:\n"
        "• <code>t.me/addemoji/PackName</code>\n"
        "• <code>https://t.me/addemoji/PackName</code>\n"
        "• <code>t.me/addstickers/PackName</code>\n\n"
        "The bot will automatically download all animated stickers as a ZIP file.\n\n"
        "💡 <b>Pro Tips:</b>\n"
        "• Custom emojis require Telegram Premium\n"
        "• Multiple custom emojis in one message = all processed\n"
        "• Packs delivered as single ZIP file 🗜️\n"
        "• Large packs (100+) take a few minutes\n"
        "• Progress bar shows real-time status\n\n"
        "ℹ️ <i>Only animated content is supported!</i>"
    )

    # ------------------------------------------------------------------ #
    #  /history                                                            #
    # ------------------------------------------------------------------ #
    HISTORY_EMPTY = (
        "📋 <b>Download History</b>\n\n"
        "You haven't downloaded any packs yet.\n\n"
        "Send me a pack URL to get started!"
    )
    # Placeholders: {count}
    HISTORY_HEADER = (
        "📋 <b>Download History</b>\n\n"
        "Your recent downloads ({count} total):\n\n"
    )
    # Placeholders: {date}, {pack_title}, {success}, {total}, {size}, {duration}, {status_icon}
    HISTORY_ENTRY = (
        "{status_icon} <b>{pack_title}</b>\n"
        "📅 {date}\n"
        "📦 {success}/{total} stickers | {size}\n"
        "⏱️ {duration}\n"
    )
    HISTORY_CLEARED = (
        "✅ <b>History Cleared</b>\n\n"
        "All your download history has been removed."
    )

    # ------------------------------------------------------------------ #
    #  /about                                                              #
    # ------------------------------------------------------------------ #
    ABOUT = (
        "ℹ️ <b>About TGS Emoji Downloader</b>\n\n"
        "🤖 <b>Bot Information:</b>\n"
        "Version: 2.1\n"
        "Type: Telegram Animated Emoji Converter\n"
        "Format: TGS (Lottie-based)\n\n"
        "✨ <b>Key Features:</b>\n"
        "• Single emoji/sticker conversion\n"
        "• Bulk pack downloads (unlimited size!)\n"
        "• ZIP file packaging for easy storage\n"
        "• Real-time progress tracking\n"
        "• Visual progress bars\n"
        "• File size information\n"
        "• Smart error handling\n\n"
        "📊 <b>Performance:</b>\n"
        "• No pack size limits (download 1000+ emojis!)\n"
        "• Automatic retry on failures\n"
        "• Efficient ZIP compression\n"
        "• Progress updates every 10 stickers\n\n"
        "💻 <b>Technology:</b>\n"
        "• Python 3.x\n"
        "• python-telegram-bot library\n"
        "• TGS format (Lottie JSON)\n\n"
        "👨‍💻 <b>Developer:</b>\n"
        "Created by <a href='https://t.me/SadadakaWijerathna'>Sadadaka Wijerathna</a>\n\n"
        "💬 <i>Made with ❤️ for the Telegram community!</i>"
    )

    # ------------------------------------------------------------------ #
    #  Sticker handler                                                     #
    # ------------------------------------------------------------------ #
    STICKER_NOT_ANIMATED = (
        "⚠️ <b>Not an animated sticker!</b>\n\n"
        "Please send an <b>animated</b> emoji or sticker (TGS format).\n\n"
        "ℹ️ Static stickers are not supported."
    )
    STICKER_PROCESSING = (
        "⏳ <b>Processing...</b>\n"
        "Converting your animated sticker to TGS file..."
    )
    # Placeholders: {file_size}
    STICKER_SUCCESS = (
        "✅ <b>Success!</b>\n\n"
        "💾 File size: {file_size}\n"
        "📊 Format: TGS (Lottie)\n\n"
        "<i>Download and use your animated sticker!</i>"
    )
    # Placeholders: {file_size}, {pack_title}, {pack_name}, {pack_link}, {total_stickers}, {animated_count}, {emoji}
    STICKER_SUCCESS_WITH_PACK = (
        "✅ <b>Sticker Downloaded!</b>\n\n"
        "{emoji} <b>Sticker Details:</b>\n"
        "💾 File size: {file_size}\n"
        "📊 Format: TGS (Lottie)\n\n"
        "🎯 <b>Pack Information:</b>\n"
        "🏷️ Name: <b>{pack_title}</b>\n"
        "🔗 Link: <a href='{pack_link}'>{pack_name}</a>\n"
        "📦 Total stickers: {total_stickers}\n"
        "✨ Animated: {animated_count}\n\n"
        "<i>Click the link above to view or download the full pack!</i>"
    )
    STICKER_ERROR = (
        "❌ <b>Error!</b>\n\n"
        "Sorry, there was an error processing your sticker.\n\n"
        "🔄 Please try again or contact support if the issue persists."
    )
    STICKER_NETWORK_ERROR = (
        "🌐 <b>Network Error!</b>\n\n"
        "Failed to download the sticker due to network issues.\n\n"
        "🔄 Please try again in a moment."
    )
    STICKER_TIMEOUT_ERROR = (
        "⏱️ <b>Timeout Error!</b>\n\n"
        "The download took too long and timed out.\n\n"
        "🔄 Please try again."
    )
    STICKER_PERMISSION_ERROR = (
        "🔒 <b>Permission Error!</b>\n\n"
        "I don't have permission to access this sticker.\n\n"
        "Please check if the sticker is from a private pack."
    )

    # ------------------------------------------------------------------ #
    #  Custom emoji handler                                                #
    # ------------------------------------------------------------------ #
    # Placeholders: {short_id}
    CUSTOM_EMOJI_PROCESSING = "⏳ Processing custom emoji (ID: {short_id}...)..."
    CUSTOM_EMOJI_NOT_FOUND = (
        "❌ Could not retrieve this custom emoji. It might not be available."
    )
    CUSTOM_EMOJI_NOT_ANIMATED = (
        "⚠️ This custom emoji is not animated. Only animated custom emojis are supported."
    )
    # Placeholders: {emoji_id}
    CUSTOM_EMOJI_SUCCESS = (
        "✅ Here's your animated custom emoji as a TGS file!\n"
        "Emoji ID: {emoji_id}"
    )
    # Placeholders: {emoji_id}, {file_size}, {pack_title}, {pack_name}, {pack_link}, {total_stickers}, {animated_count}, {emoji}
    CUSTOM_EMOJI_SUCCESS_WITH_PACK = (
        "✅ <b>Custom Emoji Downloaded!</b>\n\n"
        "{emoji} <b>Emoji Details:</b>\n"
        "🆔 ID: <code>{emoji_id}</code>\n"
        "💾 File size: {file_size}\n"
        "📊 Format: TGS (Lottie)\n\n"
        "🎯 <b>Pack Information:</b>\n"
        "🏷️ Name: <b>{pack_title}</b>\n"
        "🔗 Link: <a href='{pack_link}'>{pack_name}</a>\n"
        "📦 Total emojis: {total_stickers}\n"
        "✨ Animated: {animated_count}\n\n"
        "<i>Click the link above to view or download the full pack!</i>"
    )
    # Placeholders: {error}
    CUSTOM_EMOJI_ITEM_ERROR = "❌ Error processing this custom emoji: {error}"
    CUSTOM_EMOJI_GENERAL_ERROR = (
        "❌ Sorry, there was an error processing your custom emojis. Please try again."
    )

    # ------------------------------------------------------------------ #
    #  Pack preview                                                        #
    # ------------------------------------------------------------------ #
    # Placeholders: {pack_name}
    PREVIEW_LOADING = (
        "🔍 <b>Loading Preview...</b>\n\n"
        "Pack: <code>{pack_name}</code>\n"
        "Please wait..."
    )
    # Placeholders: {pack_name}
    PACK_NOT_FOUND = (
        "❌ <b>Pack Not Found!</b>\n\n"
        "Could not find pack: <code>{pack_name}</code>\n\n"
        "<b>Please check:</b>\n"
        "• Pack name is correct\n"
        "• Pack is public and accessible\n"
        "• URL format: <code>t.me/addemoji/PackName</code>"
    )
    # Placeholders: {title}, {total}, (animated count is always 0 here)
    PACK_NO_ANIMATED = (
        "ℹ️ <b>No Animated Stickers!</b>\n\n"
        "Pack: <b>{title}</b>\n"
        "Total stickers: {total}\n"
        "Animated stickers: <b>0</b>\n\n"
        "⚠️ This bot only supports animated stickers (TGS format)."
    )
    # Placeholders: {title}, {total}, {animated}, {preview_count}
    PREVIEW_STATS = (
        "👀 <b>Pack Preview</b>\n\n"
        "🏷️ <b>{title}</b>\n\n"
        "📊 <b>Statistics:</b>\n"
        "• Total stickers: {total}\n"
        "• Animated: <b>{animated}</b>\n\n"
        "📸 Showing {preview_count} sample stickers below...\n\n"
        "<i>Choose an action:</i>"
    )
    # Placeholders: {title}, {animated}
    PREVIEW_COMPLETE = (
        "✨ <b>Preview Complete!</b>\n\n"
        "🏷️ {title}\n"
        "📦 {animated} animated stickers available\n\n"
        "<b>What would you like to do?</b>"
    )
    # Placeholders: {error}
    PREVIEW_ERROR = (
        "❌ An error occurred while previewing the emoji pack.\n\n"
        "Error: {error}\n\n"
        "Please try again or contact support if the issue persists."
    )

    # ------------------------------------------------------------------ #
    #  Pack download                                                       #
    # ------------------------------------------------------------------ #
    # Placeholders: {pack_name}
    PACK_FETCHING = (
        "🔍 <b>Fetching Pack...</b>\n\n"
        "Pack: <code>{pack_name}</code>\n"
        "Please wait, this may take a moment..."
    )
    # Placeholders: {pack_name}  (reuses PACK_NOT_FOUND but adds retry hint)
    PACK_NOT_FOUND_RETRY = (
        "❌ <b>Pack Not Found!</b>\n\n"
        "Could not find pack: <code>{pack_name}</code>\n\n"
        "<b>Please check:</b>\n"
        "• Pack name is correct\n"
        "• Pack is public and accessible\n"
        "• URL format: <code>t.me/addemoji/PackName</code>\n\n"
        "🔄 Try again with the correct pack URL."
    )
    # Placeholders: {pack_title}, {pack_name}, {pack_link}, {total_stickers}, {animated_count}, {estimated_size}
    PACK_DETAILS_INFO = (
        "🎯 <b>Pack Information</b>\n\n"
        "🏷️ <b>Name:</b> {pack_title}\n"
        "🔗 <b>Link:</b> <a href='{pack_link}'>{pack_name}</a>\n\n"
        "📊 <b>Statistics:</b>\n"
        "📦 Total stickers: {total_stickers}\n"
        "✨ Animated: <b>{animated_count}</b>\n"
        "💾 Estimated size: ~{estimated_size} MB\n\n"
        "<i>Click the link above to view the pack in Telegram!</i>"
    )
    # Placeholders: {title}, {total}, {animated}
    PACK_FOUND = (
        "✅ <b>Pack Found!</b>\n\n"
        "🏷️ <b>{title}</b>\n\n"
        "📊 <b>Statistics:</b>\n"
        "• Total stickers: {total}\n"
        "• Animated: <b>{animated}</b>\n\n"
        "⏳ <b>Starting download...</b>\n"
        "Downloading {animated} animated stickers...\n\n"
        "<i>This may take a few moments.</i>"
    )
    # Placeholders: {title}, {progress_bar}, {current}, {total}, {pct},
    #               {success}, {failed}, {eta}
    PACK_PROGRESS = (
        "📥 <b>Downloading Pack</b>\n\n"
        "🏷️ {title}\n\n"
        "{progress_bar}\n"
        "<b>{current}/{total}</b> stickers ({pct:.1f}%)\n\n"
        "✅ Success: {success}\n"
        "❌ Failed: {failed}\n"
        "⏱️ ETA: {eta}"
    )
    # Placeholders: {title}, {progress_bar}, {current}, {total}, {pct},
    #               {success}, {failed}, {eta}
    PACK_PAUSED = (
        "⏸️ <b>Download Paused</b>\n\n"
        "🏷️ {title}\n\n"
        "{progress_bar}\n"
        "<b>{current}/{total}</b> stickers ({pct:.1f}%)\n\n"
        "✅ Success: {success}\n"
        "❌ Failed: {failed}\n"
        "⏱️ ETA: {eta}\n\n"
        "<i>Download is paused. Click Resume to continue.</i>"
    )
    # Placeholders: {title}, {success}, {total}, {failed}
    PACK_CANCELLED = (
        "🛑 <b>Download Cancelled</b>\n\n"
        "🏷️ {title}\n\n"
        "📊 <b>Progress when stopped:</b>\n"
        "✅ Downloaded: {success}/{total}\n"
        "❌ Failed: {failed}\n\n"
        "<i>Download stopped by user request.</i>"
    )
    PACK_ZIPPING = (
        "📦 <b>Creating ZIP Archive...</b>\n\n"
        "Packing {success} stickers...\n"
        "<i>Almost done!</i>"
    )
    # Placeholders: {title}, {success}, {animated}, {zip_size}, {time_str}, {failed}
    PACK_COMPLETE_CAPTION = (
        "🎉 <b>Pack Complete!</b>\n\n"
        "🏷️ <b>{title}</b>\n\n"
        "📦 <b>Archive Contents:</b>\n"
        "• {success} animated TGS files\n"
        "• File size: {zip_size}\n"
        "• Format: ZIP (compressed)\n\n"
        "⏱️ Total time: {time_str}\n"
        "❌ Failed: {failed}\n\n"
        "<i>Extract the ZIP to access all emoji files!</i>"
    )
    # Placeholders: {title}, {success}, {animated}, {zip_size}, {time_str}, {failed}
    PACK_COMPLETE_STATUS = (
        "✅ <b>Download Complete!</b>\n\n"
        "🏷️ {title}\n\n"
        "📊 <b>Summary:</b>\n"
        "✅ Successfully packed: <b>{success}/{animated}</b>\n"
        "❌ Failed: {failed}\n"
        "💾 ZIP size: {zip_size}\n"
        "⏱️ Time taken: {time_str}\n\n"
        "📁 <b>ZIP file sent above!</b>"
    )
    PACK_ALL_FAILED = (
        "❌ Failed to download any stickers from the pack.\n\n"
        "All {animated} download attempts failed.\n"
        "Please try again later."
    )
    # Placeholders: {error}
    PACK_ERROR = (
        "❌ An error occurred while processing the emoji pack.\n\n"
        "Error: {error}\n\n"
        "Please try again or contact support if the issue persists."
    )
    PACK_NETWORK_ERROR = (
        "🌐 <b>Network Error!</b>\n\n"
        "Failed to download the pack due to network issues.\n\n"
        "Progress: {success}/{total} stickers downloaded\n\n"
        "🔄 Please try again to resume."
    )
    PACK_DISK_ERROR = (
        "💾 <b>Disk Error!</b>\n\n"
        "Not enough disk space or permission denied.\n\n"
        "Please check your storage and try again."
    )
    PACK_INSUFFICIENT_SPACE = (
        "⚠️ <b>Insufficient Disk Space!</b>\n\n"
        "Estimated space needed: {estimated_mb} MB\n"
        "Available space: {available_mb} MB\n\n"
        "Please free up some disk space and try again."
    )
    PACK_LOW_SPACE_WARNING = (
        "⚠️ <b>Low Disk Space Warning</b>\n\n"
        "Available space: {available_mb} MB\n"
        "This pack may require significant space.\n\n"
        "Download will proceed, but monitor your disk space."
    )

    # ------------------------------------------------------------------ #
    #  Text / URL handler                                                  #
    # ------------------------------------------------------------------ #
    # Placeholders: {pack_name}
    PACK_URL_DETECTED = (
        "🎯 <b>Sticker Pack Detected!</b>\n\n"
        "📍 Pack: <code>{pack_name}</code>\n\n"
        "Click the button below to download all animated stickers as a ZIP file.\n\n"
        "<i>The download will start immediately.</i>"
    )
    TEXT_EMOJI_INFO = (
        "ℹ️ I can process:\n"
        "• Animated stickers (send as sticker)\n"
        "• Animated custom emojis (premium emojis)\n"
        "• Emoji pack URLs (t.me/addemoji/PackName)\n\n"
        "Regular text emojis are not supported. "
        "Please send an animated sticker, custom emoji, or pack URL!"
    )
    TEXT_UNKNOWN = (
        "👋 Send me:\n"
        "• An animated sticker or custom emoji\n"
        "• An emoji pack URL (e.g., t.me/addemoji/NewsEmoji)\n\n"
        "Use /help for more information."
    )

    # ------------------------------------------------------------------ #
    #  Inline button callbacks                                             #
    # ------------------------------------------------------------------ #
    CANCEL_PREVIEW_ACK = (
        "❌ <b>Preview Cancelled</b>\n\n"
        "Send me another pack URL anytime!"
    )

    # ------------------------------------------------------------------ #
    #  Button labels                                                       #
    # ------------------------------------------------------------------ #
    BTN_HELP = "📚 Help &amp; Guide"
    BTN_ABOUT = "ℹ️ About"
    BTN_HISTORY = "📋 History"
    BTN_CLEAR_HISTORY = "🗑️ Clear History"
    BTN_EXAMPLE_PACK = "🔗 Example Pack"
    BTN_BACK_START = "🏠 Back to Start"
    BTN_START = "🏠 Start"
    BTN_HELP_SHORT = "📚 Help"
    BTN_PREVIEW = "👀 Preview Pack"
    BTN_DOWNLOAD = "📥 Download Full Pack"
    BTN_DOWNLOAD_FULL = "📥 Download Full Pack"
    BTN_DOWNLOAD_FULL_PACK = "📦 Download Full Pack"
    BTN_CANCEL = "❌ Cancel"
    BTN_CANCEL_DOWNLOAD = "🛑 Cancel Download"
    BTN_PAUSE_DOWNLOAD = "⏸️ Pause"
    BTN_RESUME_DOWNLOAD = "▶️ Resume"

    # ------------------------------------------------------------------ #
    #  Misc                                                                #
    # ------------------------------------------------------------------ #
    EXAMPLE_PACK_URL = "https://t.me/addemoji/AnimatedEmojies"
