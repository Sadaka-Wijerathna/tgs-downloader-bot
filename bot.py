#!/usr/bin/env python3
"""
Telegram Bot for Converting Animated Emojis to TGS Files
This bot receives animated stickers/emojis and provides them as downloadable TGS files.
"""

import os
import re
import logging
import zipfile
import shutil
import time
import asyncio
import traceback
import uuid
from datetime import datetime
from functools import wraps
from typing import Callable, Any
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram.constants import ParseMode
from telegram.error import TelegramError, NetworkError, TimedOut, BadRequest, Forbidden

from messages import MSG
import config
from history import get_history_manager

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get bot token from environment variable
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not BOT_TOKEN:
    raise ValueError("Please set TELEGRAM_BOT_TOKEN environment variable")


def create_progress_bar(current: int, total: int, length: int = None) -> str:
    """Create a visual progress bar."""
    if length is None:
        length = config.PROGRESS_BAR_LENGTH
    if total == 0:
        return "[" + "░" * length + "] 0%"

    percentage = (current / total) * 100
    filled = int((current / total) * length)
    bar = "█" * filled + "░" * (length - filled)
    return f"[{bar}] {percentage:.1f}%"


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def sanitize_filename(name: str) -> str:
    """Sanitize a string to be safe for use in filenames."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    name = ''.join(char for char in name if ord(char) >= 32)
    name = name.strip()[:50]
    return name if name else "file"


def retry_on_network_error(max_retries: int = 3, delay: float = 2.0):
    """Decorator to retry async functions on network errors with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (NetworkError, TimedOut) as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt)
                        logger.warning(
                            f"Network error in {func.__name__} (attempt {attempt + 1}/{max_retries}): {e}. "
                            f"Retrying in {wait_time}s..."
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(
                            f"Network error in {func.__name__} after {max_retries} attempts: {e}"
                        )
            raise last_exception
        return wrapper
    return decorator


def cleanup_old_downloads(max_age_hours: int = None) -> None:
    """Remove old files and directories from the downloads folder.
    
    Args:
        max_age_hours: Maximum age in hours. Files older than this are removed.
                      Defaults to config.CLEANUP_AGE_HOURS
    """
    if max_age_hours is None:
        max_age_hours = config.CLEANUP_AGE_HOURS
    
    downloads_dir = config.DOWNLOADS_DIR
    if not os.path.exists(downloads_dir):
        logger.info(f"Downloads directory {downloads_dir} does not exist, skipping cleanup")
        return
    
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    cleaned_files = 0
    cleaned_dirs = 0
    freed_space = 0
    
    try:
        for item in os.listdir(downloads_dir):
            item_path = os.path.join(downloads_dir, item)
            
            try:
                # Get file/directory age
                item_age = current_time - os.path.getmtime(item_path)
                
                if item_age > max_age_seconds:
                    if os.path.isfile(item_path):
                        file_size = os.path.getsize(item_path)
                        os.remove(item_path)
                        cleaned_files += 1
                        freed_space += file_size
                        logger.info(f"Cleaned up old file: {item_path} (age: {item_age/3600:.1f}h)")
                    elif os.path.isdir(item_path):
                        # Calculate directory size before removal
                        dir_size = sum(
                            os.path.getsize(os.path.join(dirpath, filename))
                            for dirpath, _, filenames in os.walk(item_path)
                            for filename in filenames
                        )
                        shutil.rmtree(item_path)
                        cleaned_dirs += 1
                        freed_space += dir_size
                        logger.info(f"Cleaned up old directory: {item_path} (age: {item_age/3600:.1f}h)")
            except OSError as e:
                logger.warning(f"Failed to clean up {item_path}: {e}")
                continue
        
        if cleaned_files > 0 or cleaned_dirs > 0:
            logger.info(
                f"Cleanup complete: removed {cleaned_files} files and {cleaned_dirs} directories, "
                f"freed {freed_space / (1024*1024):.2f} MB"
            )
        else:
            logger.info("Cleanup complete: no old files found")
            
    except OSError as e:
        logger.error(f"Error during cleanup: {e}")


def get_disk_space_info(path: str = ".") -> dict:
    """Get disk space information for the given path.
    
    Args:
        path: Path to check disk space for
        
    Returns:
        Dictionary with 'total', 'used', 'free' in bytes
    """
    try:
        stat = shutil.disk_usage(path)
        return {
            'total': stat.total,
            'used': stat.used,
            'free': stat.free,
            'free_mb': stat.free / (1024 * 1024),
            'free_gb': stat.free / (1024 * 1024 * 1024)
        }
    except OSError as e:
        logger.error(f"Failed to get disk space info: {e}")
        return {'total': 0, 'used': 0, 'free': 0, 'free_mb': 0, 'free_gb': 0}


def check_disk_space(required_mb: float = None) -> tuple[bool, float]:
    """Check if there's sufficient disk space available.
    
    Args:
        required_mb: Required space in MB. If None, only checks minimum threshold.
        
    Returns:
        Tuple of (has_sufficient_space: bool, available_mb: float)
    """
    space_info = get_disk_space_info()
    available_mb = space_info['free_mb']
    
    if required_mb is not None:
        # Check if we have required space plus minimum buffer
        total_required = required_mb + config.MIN_FREE_SPACE_MB
        has_space = available_mb >= total_required
    else:
        # Just check minimum threshold
        has_space = available_mb >= config.MIN_FREE_SPACE_MB
    
    return has_space, available_mb


def estimate_pack_size(sticker_count: int) -> float:
    """Estimate the disk space required for a sticker pack.
    
    Args:
        sticker_count: Number of stickers in the pack
        
    Returns:
        Estimated size in MB
    """
    # Estimate: sticker size + ZIP overhead (assume 10% overhead)
    estimated_kb = sticker_count * config.ESTIMATED_STICKER_SIZE_KB
    estimated_mb = (estimated_kb * 1.1) / 1024  # Add 10% for ZIP overhead
    return estimated_mb


async def periodic_cleanup_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Periodic job to clean up old downloads."""
    logger.info("Running periodic cleanup job...")
    try:
        cleanup_old_downloads()
    except Exception as e:
        logger.error(f"Error in periodic cleanup job: {e}\n{traceback.format_exc()}")


async def download_single_sticker(
    bot,
    sticker,
    filename: str,
    idx: int,
    pack_name: str,
    semaphore: asyncio.Semaphore
) -> tuple[bool, int, str]:
    """Download a single sticker with retry logic and semaphore control.
    
    Args:
        bot: Telegram bot instance
        sticker: Sticker object to download
        filename: Path where to save the file
        idx: Index of the sticker (for logging)
        pack_name: Name of the pack (for logging)
        semaphore: Asyncio semaphore to limit concurrent downloads
        
    Returns:
        Tuple of (success: bool, index: int, error_message: str or None)
    """
    async with semaphore:
        try:
            @retry_on_network_error(max_retries=config.MAX_DOWNLOAD_RETRIES, delay=config.RETRY_DELAY_STICKER)
            async def download_with_retry():
                file = await bot.get_file(sticker.file_id)
                await file.download_to_drive(filename)
            
            await download_with_retry()
            logger.debug(f"Downloaded sticker {idx} from {pack_name}")
            return (True, idx, None)
            
        except (NetworkError, TimedOut) as e:
            error_msg = f"Network error: {e}"
            logger.warning(f"Network error downloading sticker {idx} from {pack_name}: {e}")
            return (False, idx, error_msg)
        except TelegramError as e:
            error_msg = f"Telegram error: {e}"
            logger.error(f"Telegram error downloading sticker {idx} from {pack_name}: {e}")
            return (False, idx, error_msg)
        except OSError as e:
            error_msg = f"File system error: {e}"
            logger.error(f"File system error downloading sticker {idx}: {e}")
            return (False, idx, error_msg)
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            logger.error(f"Unexpected error downloading sticker {idx}: {e}")
            return (False, idx, error_msg)


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the /start command is issued."""
    keyboard = [
        [InlineKeyboardButton(MSG.BTN_HELP,         callback_data="help"),
         InlineKeyboardButton(MSG.BTN_ABOUT,        callback_data="about")],
        [InlineKeyboardButton(MSG.BTN_HISTORY,      callback_data="history")],
        [InlineKeyboardButton(MSG.BTN_EXAMPLE_PACK, url=MSG.EXAMPLE_PACK_URL)],
    ]
    await update.message.reply_text(
        MSG.START,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message when the /help command is issued."""
    keyboard = [
        [InlineKeyboardButton(MSG.BTN_BACK_START, callback_data="start"),
         InlineKeyboardButton(MSG.BTN_ABOUT,      callback_data="about")],
    ]
    await update.message.reply_text(
        MSG.HELP,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send information about the bot."""
    keyboard = [
        [InlineKeyboardButton(MSG.BTN_START,      callback_data="start"),
         InlineKeyboardButton(MSG.BTN_HELP_SHORT, callback_data="help")],
    ]
    await update.message.reply_text(
        MSG.ABOUT,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show user's download history."""
    user_id = update.message.from_user.id
    
    try:
        history_manager = get_history_manager()
        entries = history_manager.get_user_history(user_id, limit=10)
        
        if not entries:
            keyboard = [
                [InlineKeyboardButton(MSG.BTN_START, callback_data="start")],
            ]
            await update.message.reply_text(
                MSG.HISTORY_EMPTY,
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
            return
        
        # Build history message
        history_text = MSG.HISTORY_HEADER.format(count=len(entries))
        
        for entry in entries:
            # Format date
            try:
                date_obj = datetime.fromisoformat(entry['date'])
                date_str = date_obj.strftime("%b %d, %Y %H:%M")
            except:
                date_str = "Unknown date"
            
            # Format duration
            duration = entry.get('duration_seconds', 0)
            if duration < 60:
                duration_str = f"{duration}s"
            else:
                duration_str = f"{duration//60}m {duration%60}s"
            
            # Status icon
            status_icon = "✅" if entry.get('status') == 'completed' else "❌"
            
            history_text += MSG.HISTORY_ENTRY.format(
                status_icon=status_icon,
                pack_title=entry.get('pack_title', 'Unknown Pack'),
                date=date_str,
                success=entry.get('success_count', 0),
                total=entry.get('total_stickers', 0),
                size=format_file_size(entry.get('file_size', 0)),
                duration=duration_str,
            ) + "\n"
        
        keyboard = [
            [InlineKeyboardButton(MSG.BTN_CLEAR_HISTORY, callback_data="clear_history")],
            [InlineKeyboardButton(MSG.BTN_START, callback_data="start")],
        ]
        
        await update.message.reply_text(
            history_text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        
    except Exception as e:
        logger.error(f"Error showing history for user {user_id}: {e}")
        await update.message.reply_text(
            "❌ An error occurred while retrieving your history. Please try again later.",
            parse_mode=ParseMode.HTML,
        )


# ---------------------------------------------------------------------------
# Message handlers
# ---------------------------------------------------------------------------

async def handle_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming stickers and convert them to TGS files."""
    sticker = update.message.sticker

    if not sticker.is_animated:
        await update.message.reply_text(MSG.STICKER_NOT_ANIMATED, parse_mode=ParseMode.HTML)
        return

    processing_msg = None
    temp_filename = None
    
    try:
        processing_msg = await update.message.reply_text(
            MSG.STICKER_PROCESSING, parse_mode=ParseMode.HTML
        )

        os.makedirs(config.DOWNLOADS_DIR, exist_ok=True)

        emoji_part = sanitize_filename(sticker.emoji) if sticker.emoji else "sticker"
        set_name   = sanitize_filename(sticker.set_name) if sticker.set_name else "unknown"
        unique_id  = sticker.file_unique_id[:8]
        temp_filename   = f"{config.DOWNLOADS_DIR}/{emoji_part}_{set_name}_{sticker.file_unique_id}.tgs"
        output_filename = f"{emoji_part}_{set_name}_{unique_id}.tgs"

        # Log sticker details for debugging
        logger.info(f"Sticker details - set_name: {sticker.set_name}, emoji: {sticker.emoji}, is_animated: {sticker.is_animated}")
        
        # Fetch pack details if sticker belongs to a set
        pack_info = None
        pack_link = None
        if sticker.set_name:
            try:
                logger.info(f"Attempting to fetch pack info for set: {sticker.set_name}")
                @retry_on_network_error(max_retries=config.MAX_DOWNLOAD_RETRIES, delay=config.RETRY_DELAY_FETCH)
                async def fetch_sticker_set():
                    return await context.bot.get_sticker_set(sticker.set_name)
                
                sticker_set = await fetch_sticker_set()
                # Get sticker type - it might be a string or an enum
                if hasattr(sticker_set, 'sticker_type'):
                    sticker_type = sticker_set.sticker_type
                    # If it's an enum, get the name; if it's already a string, use it
                    if hasattr(sticker_type, 'name'):
                        sticker_type = sticker_type.name
                    elif isinstance(sticker_type, str):
                        sticker_type = sticker_type
                    else:
                        sticker_type = str(sticker_type)
                else:
                    sticker_type = 'REGULAR'
                
                pack_info = {
                    'title': sticker_set.title,
                    'name': sticker.set_name,
                    'total_stickers': len(sticker_set.stickers),
                    'animated_count': len([s for s in sticker_set.stickers if s.is_animated]),
                    'sticker_type': sticker_type
                }
                # Determine pack link based on sticker type
                if pack_info['sticker_type'] in ['CUSTOM_EMOJI', 'custom_emoji']:
                    pack_link = f"https://t.me/addemoji/{sticker.set_name}"
                else:
                    pack_link = f"https://t.me/addstickers/{sticker.set_name}"
                
                logger.info(f"Successfully fetched pack info for {sticker.set_name}: {pack_info['title']}")
            except Exception as e:
                logger.error(f"Could not fetch pack info for {sticker.set_name}: {e}")
                logger.error(f"Exception details: {traceback.format_exc()}")
        else:
            logger.warning(f"Sticker {sticker.file_id} has no set_name attribute")

        # Retry wrapper for network operations
        @retry_on_network_error(max_retries=config.MAX_DOWNLOAD_RETRIES, delay=config.RETRY_DELAY_FETCH)
        async def download_with_retry():
            file = await context.bot.get_file(sticker.file_id)
            await file.download_to_drive(temp_filename)
            return file
        
        await download_with_retry()
        file_size = os.path.getsize(temp_filename)

        # Send pack details as a separate message if available
        if pack_info:
            details_message = MSG.STICKER_SUCCESS_WITH_PACK.format(
                file_size=format_file_size(file_size),
                pack_title=pack_info['title'],
                pack_name=pack_info['name'],
                pack_link=pack_link,
                total_stickers=pack_info['total_stickers'],
                animated_count=pack_info['animated_count'],
                emoji=sticker.emoji if sticker.emoji else '❓'
            )
            await update.message.reply_text(details_message, parse_mode=ParseMode.HTML)
            caption = f"✅ {sticker.emoji if sticker.emoji else '❓'} Sticker from {pack_info['title']}"
        else:
            caption = MSG.STICKER_SUCCESS.format(file_size=format_file_size(file_size))

        with open(temp_filename, 'rb') as tgs_file:
            await update.message.reply_document(
                document=tgs_file,
                filename=output_filename,
                caption=caption
            )

        if processing_msg:
            try:
                await processing_msg.delete()
            except TelegramError:
                pass  # Message might already be deleted
        
        logger.info(f"Successfully processed sticker {sticker.file_id}")

    except (NetworkError, TimedOut) as e:
        logger.error(f"Network error processing sticker {sticker.file_id}: {e}")
        await update.message.reply_text(MSG.STICKER_NETWORK_ERROR, parse_mode=ParseMode.HTML)
    except Forbidden as e:
        logger.error(f"Permission error processing sticker {sticker.file_id}: {e}")
        await update.message.reply_text(MSG.STICKER_PERMISSION_ERROR, parse_mode=ParseMode.HTML)
    except BadRequest as e:
        logger.error(f"Bad request processing sticker {sticker.file_id}: {e}")
        await update.message.reply_text(MSG.STICKER_ERROR, parse_mode=ParseMode.HTML)
    except OSError as e:
        logger.error(f"File system error processing sticker {sticker.file_id}: {e}")
        await update.message.reply_text(MSG.STICKER_ERROR, parse_mode=ParseMode.HTML)
    except TelegramError as e:
        logger.error(f"Telegram error processing sticker {sticker.file_id}: {e}")
        await update.message.reply_text(MSG.STICKER_ERROR, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f"Unexpected error processing sticker {sticker.file_id}: {e}\n{traceback.format_exc()}")
        await update.message.reply_text(MSG.STICKER_ERROR, parse_mode=ParseMode.HTML)
    finally:
        # Ensure temp file is cleaned up
        if temp_filename and os.path.exists(temp_filename):
            try:
                os.remove(temp_filename)
            except OSError as e:
                logger.warning(f"Failed to remove temp file {temp_filename}: {e}")


async def handle_custom_emoji(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle messages containing custom emojis (premium animated emojis)."""
    message = update.message

    if not message.entities and not message.caption_entities:
        return

    entities     = message.entities or message.caption_entities or []
    custom_emojis = [e for e in entities if e.type == "custom_emoji"]

    if not custom_emojis:
        return

    for entity in custom_emojis:
        custom_emoji_id = entity.custom_emoji_id
        processing_msg = None
        temp_filename = None

        try:
            processing_msg = await message.reply_text(
                MSG.CUSTOM_EMOJI_PROCESSING.format(short_id=custom_emoji_id[:8])
            )

            # Retry wrapper for network operations
            @retry_on_network_error(max_retries=config.MAX_DOWNLOAD_RETRIES, delay=config.RETRY_DELAY_FETCH)
            async def fetch_custom_emoji():
                return await context.bot.get_custom_emoji_stickers([custom_emoji_id])

            custom_emoji_stickers = await fetch_custom_emoji()

            if not custom_emoji_stickers:
                await processing_msg.edit_text(MSG.CUSTOM_EMOJI_NOT_FOUND)
                continue

            sticker = custom_emoji_stickers[0]
            
            # Debug: Log all sticker attributes
            logger.info(f"Custom emoji sticker object attributes: {dir(sticker)}")
            logger.info(f"Custom emoji sticker - file_id: {sticker.file_id}, file_unique_id: {sticker.file_unique_id}")
            logger.info(f"Custom emoji sticker - is_animated: {sticker.is_animated}, is_video: {sticker.is_video}")
            logger.info(f"Custom emoji sticker - emoji: {getattr(sticker, 'emoji', 'N/A')}, set_name: {getattr(sticker, 'set_name', 'N/A')}")
            logger.info(f"Custom emoji sticker - type: {getattr(sticker, 'type', 'N/A')}, premium_animation: {getattr(sticker, 'premium_animation', 'N/A')}")

            if not sticker.is_animated:
                await processing_msg.edit_text(MSG.CUSTOM_EMOJI_NOT_ANIMATED)
                continue

            os.makedirs(config.DOWNLOADS_DIR, exist_ok=True)

            emoji_part = sanitize_filename(sticker.emoji) if sticker.emoji else "emoji"
            set_part   = sanitize_filename(sticker.set_name) if sticker.set_name else "custom"
            unique_id  = custom_emoji_id[:8]
            temp_filename   = f"{config.DOWNLOADS_DIR}/custom_{emoji_part}_{sticker.file_unique_id}.tgs"
            output_filename = f"{emoji_part}_{set_part}_{unique_id}.tgs"

            # Retry wrapper for download
            @retry_on_network_error(max_retries=config.MAX_DOWNLOAD_RETRIES, delay=config.RETRY_DELAY_FETCH)
            async def download_emoji():
                file = await context.bot.get_file(sticker.file_id)
                await file.download_to_drive(temp_filename)

            await download_emoji()
            
            file_size = os.path.getsize(temp_filename)

            # Log sticker details for debugging
            logger.info(f"Custom emoji sticker details - set_name: {sticker.set_name}, emoji: {sticker.emoji}, is_animated: {sticker.is_animated}")

            # Fetch pack details if emoji belongs to a set
            pack_info = None
            pack_link = None
            if sticker.set_name:
                try:
                    logger.info(f"Attempting to fetch pack info for set: {sticker.set_name}")
                    @retry_on_network_error(max_retries=config.MAX_DOWNLOAD_RETRIES, delay=config.RETRY_DELAY_FETCH)
                    async def fetch_sticker_set():
                        return await context.bot.get_sticker_set(sticker.set_name)
                    
                    sticker_set = await fetch_sticker_set()
                    # Get sticker type - it might be a string or an enum
                    if hasattr(sticker_set, 'sticker_type'):
                        sticker_type = sticker_set.sticker_type
                        # If it's an enum, get the name; if it's already a string, use it
                        if hasattr(sticker_type, 'name'):
                            sticker_type = sticker_type.name
                        elif isinstance(sticker_type, str):
                            sticker_type = sticker_type
                        else:
                            sticker_type = str(sticker_type)
                    else:
                        sticker_type = 'CUSTOM_EMOJI'
                    
                    pack_info = {
                        'title': sticker_set.title,
                        'name': sticker.set_name,
                        'total_stickers': len(sticker_set.stickers),
                        'animated_count': len([s for s in sticker_set.stickers if s.is_animated]),
                        'sticker_type': sticker_type
                    }
                    # Custom emojis use addemoji link
                    pack_link = f"https://t.me/addemoji/{sticker.set_name}"
                    
                    logger.info(f"Successfully fetched pack info for custom emoji {sticker.set_name}: {pack_info['title']}")
                except Exception as e:
                    logger.error(f"Could not fetch pack info for custom emoji {sticker.set_name}: {e}")
                    logger.error(f"Exception details: {traceback.format_exc()}")
            else:
                logger.warning(f"Custom emoji {custom_emoji_id} has no set_name attribute")

            # Send pack details as a separate message if available
            if pack_info:
                details_message = MSG.CUSTOM_EMOJI_SUCCESS_WITH_PACK.format(
                    emoji_id=custom_emoji_id,
                    file_size=format_file_size(file_size),
                    pack_title=pack_info['title'],
                    pack_name=pack_info['name'],
                    pack_link=pack_link,
                    total_stickers=pack_info['total_stickers'],
                    animated_count=pack_info['animated_count'],
                    emoji=sticker.emoji if sticker.emoji else '❓'
                )
                await message.reply_text(details_message, parse_mode=ParseMode.HTML)
                caption = f"✅ {sticker.emoji if sticker.emoji else '❓'} Custom Emoji from {pack_info['title']}"
            else:
                caption = MSG.CUSTOM_EMOJI_SUCCESS.format(emoji_id=custom_emoji_id)

            with open(temp_filename, 'rb') as tgs_file:
                await message.reply_document(
                    document=tgs_file,
                    filename=output_filename,
                    caption=caption
                )

            # Delete processing message
            if processing_msg:
                try:
                    await processing_msg.delete()
                except TelegramError as e:
                    logger.debug(f"Could not delete processing message: {e}")
            
            logger.info(f"Successfully processed custom emoji {custom_emoji_id} - Pack info: {pack_info is not None}")

        except (NetworkError, TimedOut) as e:
            logger.error(f"Network error processing custom emoji {custom_emoji_id}: {e}")
            if processing_msg:
                try:
                    await processing_msg.edit_text(MSG.CUSTOM_EMOJI_ITEM_ERROR.format(error="Network error. Please try again."))
                except TelegramError:
                    pass
        except (Forbidden, BadRequest) as e:
            logger.error(f"Permission/request error processing custom emoji {custom_emoji_id}: {e}")
            if processing_msg:
                try:
                    await processing_msg.edit_text(MSG.CUSTOM_EMOJI_ITEM_ERROR.format(error=str(e)))
                except TelegramError:
                    pass
        except TelegramError as e:
            logger.error(f"Telegram error processing custom emoji {custom_emoji_id}: {e}")
            if processing_msg:
                try:
                    await processing_msg.edit_text(MSG.CUSTOM_EMOJI_ITEM_ERROR.format(error=str(e)))
                except TelegramError:
                    pass
        except Exception as e:
            logger.error(f"Unexpected error processing custom emoji {custom_emoji_id}: {e}\n{traceback.format_exc()}")
            if processing_msg:
                try:
                    await processing_msg.edit_text(MSG.CUSTOM_EMOJI_ITEM_ERROR.format(error="Unexpected error"))
                except TelegramError:
                    pass
        finally:
            # Ensure temp file is cleaned up
            if temp_filename and os.path.exists(temp_filename):
                try:
                    os.remove(temp_filename)
                except OSError as e:
                    logger.warning(f"Failed to remove temp file {temp_filename}: {e}")


# Preview functionality has been removed
# Users can directly download packs without preview


async def handle_emoji_pack_from_callback(
    message, context: ContextTypes.DEFAULT_TYPE, pack_name: str, download_id: str = None
) -> None:
    """Handle emoji/sticker pack download from callback query.
    
    This is a wrapper for handle_emoji_pack that accepts a message directly
    instead of an Update object, for use with callback queries.
    """
    # Skip showing pack details since they were already shown when URL was detected
    await _handle_emoji_pack_internal(message, context, pack_name, download_id, show_details=False)


async def handle_emoji_pack(
    update: Update, context: ContextTypes.DEFAULT_TYPE, pack_name: str, download_id: str = None
) -> None:
    """Handle emoji/sticker pack download from Telegram links."""
    await _handle_emoji_pack_internal(update.message, context, pack_name, download_id, show_details=True)


async def _handle_emoji_pack_internal(
    message, context: ContextTypes.DEFAULT_TYPE, pack_name: str, download_id: str = None, show_details: bool = True
) -> None:
    """Internal function to handle emoji/sticker pack download.
    
    Args:
        message: The message object (from update.message or query.message)
        context: The context object
        pack_name: Name of the sticker pack
        download_id: Optional unique download ID
        show_details: Whether to show pack details before download (False when called from button)
    """
    
    # Generate unique download ID if not provided
    if download_id is None:
        download_id = str(uuid.uuid4())
    
    # Initialize download state
    if 'download_states' not in context.user_data:
        context.user_data['download_states'] = {}
    
    # Download state tracking (pause/cancel) removed
    context.user_data['download_states'][download_id] = {
        'state': 'running',
        'pack_name': pack_name,
        'chat_id': message.chat_id
    }
    
    logger.info(f"=== DOWNLOAD STARTED ===")
    logger.info(f"Download ID: {download_id}")
    logger.info(f"Pack name: {pack_name}")
    logger.info(f"Initial state: {context.user_data['download_states'][download_id]}")
    logger.info(f"All download states: {list(context.user_data['download_states'].keys())}")
    logger.info(f"=========================")
    
    status_msg = None
    pack_dir = None
    zip_filename = None

    try:
        status_msg = await message.reply_text(
            MSG.PACK_FETCHING.format(pack_name=pack_name), parse_mode=ParseMode.HTML
        )

        # Retry wrapper for fetching sticker set
        @retry_on_network_error(max_retries=config.MAX_DOWNLOAD_RETRIES, delay=config.RETRY_DELAY_FETCH)
        async def fetch_sticker_set():
            return await context.bot.get_sticker_set(pack_name)

        sticker_set = await fetch_sticker_set()

        animated_stickers = [s for s in sticker_set.stickers if s.is_animated]
        total_stickers    = len(sticker_set.stickers)
        animated_count    = len(animated_stickers)

        if animated_count == 0:
            await status_msg.edit_text(
                MSG.PACK_NO_ANIMATED.format(title=sticker_set.title, total=total_stickers),
                parse_mode=ParseMode.HTML,
            )
            return

        # Check disk space before starting download
        estimated_size_mb = estimate_pack_size(animated_count)
        has_space, available_mb = check_disk_space(estimated_size_mb)
        
        if not has_space:
            await status_msg.edit_text(
                MSG.PACK_INSUFFICIENT_SPACE.format(
                    estimated_mb=f"{estimated_size_mb:.1f}",
                    available_mb=f"{available_mb:.1f}"
                ),
                parse_mode=ParseMode.HTML,
            )
            logger.warning(
                f"Insufficient disk space for pack {pack_name}: "
                f"need {estimated_size_mb:.1f}MB, have {available_mb:.1f}MB"
            )
            return
        
        # Warn if space is low but sufficient
        if available_mb < config.WARN_LOW_SPACE_MB:
            try:
                await message.reply_text(
                    MSG.PACK_LOW_SPACE_WARNING.format(available_mb=f"{available_mb:.1f}"),
                    parse_mode=ParseMode.HTML,
                )
            except TelegramError:
                pass  # Don't fail if warning can't be sent

        # Send detailed pack information only if requested (not when called from button)
        if show_details:
            # Determine pack link based on sticker type
            sticker_type = sticker_set.sticker_type if hasattr(sticker_set, 'sticker_type') else 'regular'
            if hasattr(sticker_type, 'name'):
                sticker_type = sticker_type.name
            elif isinstance(sticker_type, str):
                sticker_type = sticker_type
            else:
                sticker_type = str(sticker_type)
            
            if sticker_type in ['CUSTOM_EMOJI', 'custom_emoji']:
                pack_link = f"https://t.me/addemoji/{pack_name}"
            else:
                pack_link = f"https://t.me/addstickers/{pack_name}"
            
            # Send detailed pack information
            pack_details = MSG.PACK_DETAILS_INFO.format(
                pack_title=sticker_set.title,
                pack_name=pack_name,
                pack_link=pack_link,
                total_stickers=total_stickers,
                animated_count=animated_count,
                estimated_size=f"{estimated_size_mb:.1f}"
            )
            await message.reply_text(pack_details, parse_mode=ParseMode.HTML)
        
        await status_msg.edit_text(
            MSG.PACK_FOUND.format(
                title=sticker_set.title, total=total_stickers, animated=animated_count
            ),
            parse_mode=ParseMode.HTML,
        )

        os.makedirs(config.DOWNLOADS_DIR, exist_ok=True)
        pack_dir             = f"{config.DOWNLOADS_DIR}/{pack_name}_{message.message_id}"
        os.makedirs(pack_dir, exist_ok=True)
        pack_title_sanitized = sanitize_filename(sticker_set.title)

        success_count   = 0
        failed_count    = 0
        start_time      = time.time()
        update_interval = config.PROGRESS_UPDATE_INTERVAL_LARGE if animated_count > config.PACK_SIZE_THRESHOLD else config.PROGRESS_UPDATE_INTERVAL_SMALL
        
        # Create semaphore to limit concurrent downloads
        download_semaphore = asyncio.Semaphore(config.MAX_CONCURRENT_DOWNLOADS)
        
        # Prepare download tasks for parallel execution
        download_tasks = []
        for idx, sticker in enumerate(animated_stickers, 1):
            emoji_prefix = sanitize_filename(sticker.emoji) if sticker.emoji else "emoji"
            filename = f"{pack_dir}/{emoji_prefix}_{pack_title_sanitized}_{idx:03d}.tgs"
            
            task = download_single_sticker(
                context.bot,
                sticker,
                filename,
                idx,
                pack_name,
                download_semaphore
            )
            download_tasks.append(task)
        
        logger.info(f"Starting parallel download of {animated_count} stickers with max {config.MAX_CONCURRENT_DOWNLOADS} concurrent downloads")
        
        # Process downloads in batches with progress updates
        completed_count = 0
        last_update_time = time.time()
        
        # Use asyncio.as_completed to process results as they finish
        for coro in asyncio.as_completed(download_tasks):
            try:
                success, idx, error_msg = await coro
                completed_count += 1
                
                if success:
                    success_count += 1
                else:
                    failed_count += 1
                
                # Update progress at intervals or on completion
                current_time = time.time()
                should_update = (
                    completed_count % update_interval == 0 or 
                    completed_count == animated_count or
                    (current_time - last_update_time) >= config.PROGRESS_UPDATE_MIN_SECONDS
                )
                
                if should_update:
                    progress_bar = create_progress_bar(completed_count, animated_count)
                    elapsed = current_time - start_time
                    avg_time = elapsed / completed_count if completed_count > 0 else 0
                    remaining = int((animated_count - completed_count) * avg_time)
                    eta = f"{remaining}s" if remaining < 60 else f"{remaining//60}m {remaining%60}s"
                    
                    try:
                        await status_msg.edit_text(
                            MSG.PACK_PROGRESS.format(
                                title=sticker_set.title,
                                progress_bar=progress_bar,
                                current=completed_count,
                                total=animated_count,
                                pct=(completed_count / animated_count) * 100,
                                success=success_count,
                                failed=failed_count,
                                eta=eta,
                            ),
                            parse_mode=ParseMode.HTML,
                        )
                        last_update_time = current_time
                    except TelegramError as e:
                        # Ignore errors updating status message
                        logger.debug(f"Failed to update progress message: {e}")
                
            except asyncio.CancelledError:
                logger.info(f"Download task cancelled for pack {pack_name}")
                failed_count += 1
            except Exception as e:
                logger.error(f"Unexpected error processing download result: {e}")
                failed_count += 1
        
        logger.info(f"Completed parallel download: {success_count} succeeded, {failed_count} failed out of {animated_count} stickers")

        # Package and send ZIP
        if success_count > 0:
            await status_msg.edit_text(
                MSG.PACK_ZIPPING.format(success=success_count), parse_mode=ParseMode.HTML
            )

            zip_filename = f"{config.DOWNLOADS_DIR}/{pack_name}_{message.message_id}.zip"
            with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for f in os.listdir(pack_dir):
                    zipf.write(os.path.join(pack_dir, f), f)

            zip_size   = os.path.getsize(zip_filename)
            total_time = int(time.time() - start_time)
            time_str   = f"{total_time}s" if total_time < 60 else f"{total_time//60}m {total_time%60}s"

            with open(zip_filename, 'rb') as zip_file:
                await message.reply_document(
                    document=zip_file,
                    filename=f"{pack_title_sanitized}_emojis.zip",
                    caption=MSG.PACK_COMPLETE_CAPTION.format(
                        title=sticker_set.title,
                        success=success_count,
                        animated=animated_count,
                        zip_size=format_file_size(zip_size),
                        time_str=time_str,
                        failed=failed_count,
                    ),
                    parse_mode=ParseMode.HTML,
                )
            
            # Record download in history
            try:
                history_manager = get_history_manager()
                history_manager.add_entry(
                    user_id=message.chat_id,
                    pack_name=pack_name,
                    pack_title=sticker_set.title,
                    total_stickers=animated_count,
                    success_count=success_count,
                    failed_count=failed_count,
                    file_size=zip_size,
                    duration_seconds=total_time
                )
                logger.info(f"Recorded download history for user {message.chat_id}: {pack_name}")
            except Exception as e:
                logger.error(f"Failed to record download history: {e}")
                # Don't fail the download if history recording fails

            if status_msg:
                try:
                    await status_msg.edit_text(
                        MSG.PACK_COMPLETE_STATUS.format(
                            title=sticker_set.title,
                            success=success_count,
                            animated=animated_count,
                            zip_size=format_file_size(zip_size),
                            time_str=time_str,
                            failed=failed_count,
                        ),
                        parse_mode=ParseMode.HTML,
                    )
                except TelegramError:
                    pass
        else:
            if status_msg:
                try:
                    await status_msg.edit_text(
                        MSG.PACK_ALL_FAILED.format(animated=animated_count)
                    )
                except TelegramError:
                    pass
            return

        logger.info(f"Completed pack download: {pack_name} - {success_count}/{animated_count}")

    except (NetworkError, TimedOut) as e:
        logger.error(f"Network error handling pack {pack_name}: {e}")
        if status_msg:
            try:
                await status_msg.edit_text(
                    MSG.PACK_NETWORK_ERROR.format(success=success_count, total=animated_count),
                    parse_mode=ParseMode.HTML
                )
            except TelegramError:
                pass
    except BadRequest as e:
        logger.error(f"Pack not found or invalid: {pack_name}: {e}")
        if status_msg:
            try:
                await status_msg.edit_text(
                    MSG.PACK_NOT_FOUND_RETRY.format(pack_name=pack_name),
                    parse_mode=ParseMode.HTML
                )
            except TelegramError:
                pass
    except OSError as e:
        logger.error(f"File system error handling pack {pack_name}: {e}\n{traceback.format_exc()}")
        try:
            await message.reply_text(MSG.PACK_DISK_ERROR, parse_mode=ParseMode.HTML)
        except TelegramError:
            pass
    except TelegramError as e:
        logger.error(f"Telegram error handling pack {pack_name}: {e}")
        try:
            await message.reply_text(MSG.PACK_ERROR.format(error=str(e)), parse_mode=ParseMode.HTML)
        except TelegramError:
            pass
    except Exception as e:
        logger.error(f"Unexpected error handling pack {pack_name}: {e}\n{traceback.format_exc()}")
        try:
            await message.reply_text(MSG.PACK_ERROR.format(error="Unexpected error"), parse_mode=ParseMode.HTML)
        except TelegramError:
            pass
    finally:
        # Ensure cleanup of temporary files and directories
        if download_id in context.user_data.get('download_states', {}):
            del context.user_data['download_states'][download_id]
        
        if pack_dir and os.path.exists(pack_dir):
            try:
                shutil.rmtree(pack_dir)
                logger.info(f"Cleaned up pack directory: {pack_dir}")
            except OSError as e:
                logger.warning(f"Failed to remove pack directory {pack_dir}: {e}")
        
        if zip_filename and os.path.exists(zip_filename):
            try:
                os.remove(zip_filename)
                logger.info(f"Cleaned up zip file: {zip_filename}")
            except OSError as e:
                logger.warning(f"Failed to remove zip file {zip_filename}: {e}")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages that might contain emojis or pack URLs."""
    message = update.message
    text    = message.text

    pack_url_pattern = r't\.me/(?:addemoji|addstickers)/([A-Za-z0-9_]+)'
    pack_match = re.search(pack_url_pattern, text)

    if pack_match:
        pack_name = pack_match.group(1)
        
        # Fetch pack details to show comprehensive information
        status_msg = await message.reply_text(
            MSG.PACK_FETCHING.format(pack_name=pack_name),
            parse_mode=ParseMode.HTML
        )
        
        try:
            # Fetch sticker set
            @retry_on_network_error(max_retries=config.MAX_DOWNLOAD_RETRIES, delay=config.RETRY_DELAY_FETCH)
            async def fetch_sticker_set():
                return await context.bot.get_sticker_set(pack_name)
            
            sticker_set = await fetch_sticker_set()
            
            animated_stickers = [s for s in sticker_set.stickers if s.is_animated]
            total_stickers = len(sticker_set.stickers)
            animated_count = len(animated_stickers)
            
            if animated_count == 0:
                await status_msg.edit_text(
                    MSG.PACK_NO_ANIMATED.format(title=sticker_set.title, total=total_stickers),
                    parse_mode=ParseMode.HTML,
                )
                return
            
            # Determine pack link
            sticker_type = sticker_set.sticker_type if hasattr(sticker_set, 'sticker_type') else 'regular'
            if hasattr(sticker_type, 'name'):
                sticker_type = sticker_type.name
            elif isinstance(sticker_type, str):
                sticker_type = sticker_type
            else:
                sticker_type = str(sticker_type)
            
            if sticker_type in ['CUSTOM_EMOJI', 'custom_emoji']:
                pack_link = f"https://t.me/addemoji/{pack_name}"
            else:
                pack_link = f"https://t.me/addstickers/{pack_name}"
            
            # Estimate size
            estimated_size_mb = estimate_pack_size(animated_count)
            
            # Show detailed pack information
            pack_details = MSG.PACK_DETAILS_INFO.format(
                pack_title=sticker_set.title,
                pack_name=pack_name,
                pack_link=pack_link,
                total_stickers=total_stickers,
                animated_count=animated_count,
                estimated_size=f"{estimated_size_mb:.1f}"
            )
            
            keyboard = [
                [InlineKeyboardButton(MSG.BTN_DOWNLOAD, callback_data=f"download_{pack_name}")],
            ]
            
            await status_msg.edit_text(
                pack_details,
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
            
        except BadRequest as e:
            logger.error(f"Pack not found: {pack_name}: {e}")
            await status_msg.edit_text(
                MSG.PACK_NOT_FOUND.format(pack_name=pack_name),
                parse_mode=ParseMode.HTML,
            )
        except (NetworkError, TimedOut) as e:
            logger.error(f"Network error fetching pack {pack_name}: {e}")
            await status_msg.edit_text(
                "🌐 <b>Network Error</b>\n\nFailed to fetch pack details. Please try again.",
                parse_mode=ParseMode.HTML,
            )
        except Exception as e:
            logger.error(f"Error fetching pack details for {pack_name}: {e}")
            # Fallback to simple message
            keyboard = [
                [InlineKeyboardButton(MSG.BTN_DOWNLOAD, callback_data=f"download_{pack_name}")],
            ]
            await status_msg.edit_text(
                MSG.PACK_URL_DETECTED.format(pack_name=pack_name),
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        
        return

    if message.entities:
        custom_emojis = [e for e in message.entities if e.type == "custom_emoji"]
        if custom_emojis:
            await handle_custom_emoji(update, context)
            return

    if any(char for char in text if ord(char) > 127):
        await message.reply_text(MSG.TEXT_EMOJI_INFO)
    else:
        await message.reply_text(MSG.TEXT_UNKNOWN)


# ---------------------------------------------------------------------------
# Inline button callback
# ---------------------------------------------------------------------------

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline keyboard button presses."""
    query = update.callback_query
    
    # Log EVERY button click
    logger.info(f"\n{'#'*60}")
    logger.info(f"BUTTON CALLBACK TRIGGERED")
    logger.info(f"Callback data: {query.data}")
    logger.info(f"User: {query.from_user.id}")
    logger.info(f"{'#'*60}\n")

    if query.data.startswith("download_"):
        pack_name = query.data.replace("download_", "")
        # Generate a new download_id for this download
        download_id = str(uuid.uuid4())
        await query.answer("📥 Starting download...")
        # Create a modified update with the callback query's message
        # We can't modify update.message directly, so we pass the message separately
        await handle_emoji_pack_from_callback(query.message, context, pack_name, download_id)
        return

    if query.data == "clear_history":
        user_id = query.from_user.id
        try:
            history_manager = get_history_manager()
            count = history_manager.clear_user_history(user_id)
            await query.answer(f"✅ Cleared {count} entries")
            await query.edit_message_text(
                MSG.HISTORY_CLEARED,
                parse_mode=ParseMode.HTML,
            )
            logger.info(f"User {user_id} cleared their history ({count} entries)")
        except Exception as e:
            logger.error(f"Error clearing history for user {user_id}: {e}")
            await query.answer("❌ Error clearing history")
        return

    await query.answer()

    if query.data == "help":
        keyboard = [
            [InlineKeyboardButton(MSG.BTN_BACK_START, callback_data="start"),
             InlineKeyboardButton(MSG.BTN_ABOUT,      callback_data="about")],
        ]
        await query.edit_message_text(
            MSG.HELP, parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    elif query.data == "history":
        user_id = query.from_user.id
        try:
            history_manager = get_history_manager()
            entries = history_manager.get_user_history(user_id, limit=10)
            
            if not entries:
                keyboard = [
                    [InlineKeyboardButton(MSG.BTN_START, callback_data="start")],
                ]
                await query.edit_message_text(
                    MSG.HISTORY_EMPTY,
                    parse_mode=ParseMode.HTML,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                )
                return
            
            # Build history message
            history_text = MSG.HISTORY_HEADER.format(count=len(entries))
            
            for entry in entries:
                # Format date
                try:
                    date_obj = datetime.fromisoformat(entry['date'])
                    date_str = date_obj.strftime("%b %d, %Y %H:%M")
                except:
                    date_str = "Unknown date"
                
                # Format duration
                duration = entry.get('duration_seconds', 0)
                if duration < 60:
                    duration_str = f"{duration}s"
                else:
                    duration_str = f"{duration//60}m {duration%60}s"
                
                # Status icon
                status_icon = "✅" if entry.get('status') == 'completed' else "❌"
                
                history_text += MSG.HISTORY_ENTRY.format(
                    status_icon=status_icon,
                    pack_title=entry.get('pack_title', 'Unknown Pack'),
                    date=date_str,
                    success=entry.get('success_count', 0),
                    total=entry.get('total_stickers', 0),
                    size=format_file_size(entry.get('file_size', 0)),
                    duration=duration_str,
                ) + "\n"
            
            keyboard = [
                [InlineKeyboardButton(MSG.BTN_CLEAR_HISTORY, callback_data="clear_history")],
                [InlineKeyboardButton(MSG.BTN_START, callback_data="start")],
            ]
            
            await query.edit_message_text(
                history_text,
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        except Exception as e:
            logger.error(f"Error showing history for user {user_id}: {e}")
            await query.edit_message_text(
                "❌ An error occurred while retrieving your history. Please try again later.",
                parse_mode=ParseMode.HTML,
            )

    elif query.data == "about":
        keyboard = [
            [InlineKeyboardButton(MSG.BTN_START,      callback_data="start"),
             InlineKeyboardButton(MSG.BTN_HELP_SHORT, callback_data="help")],
        ]
        await query.edit_message_text(
            MSG.ABOUT, parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    elif query.data == "start":
        keyboard = [
            [InlineKeyboardButton(MSG.BTN_HELP,         callback_data="help"),
             InlineKeyboardButton(MSG.BTN_ABOUT,        callback_data="about")],
            [InlineKeyboardButton(MSG.BTN_HISTORY,      callback_data="history")],
            [InlineKeyboardButton(MSG.BTN_EXAMPLE_PACK, url=MSG.EXAMPLE_PACK_URL)],
        ]
        await query.edit_message_text(
            MSG.START, parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


# ---------------------------------------------------------------------------
# Error handler
# ---------------------------------------------------------------------------

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by updates with detailed information."""
    error = context.error
    
    # Log different error types with appropriate severity
    if isinstance(error, (NetworkError, TimedOut)):
        logger.warning(f"Network error in update {update}: {error}")
    elif isinstance(error, (BadRequest, Forbidden)):
        logger.error(f"Request/Permission error in update {update}: {error}")
    elif isinstance(error, TelegramError):
        logger.error(f"Telegram error in update {update}: {error}")
    else:
        logger.error(
            f"Unexpected error in update {update}: {error}\n"
            f"Traceback:\n{traceback.format_exc()}"
        )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def main() -> None:
    """Start the bot."""
    # Perform startup cleanup if enabled
    if config.CLEANUP_ON_STARTUP:
        logger.info("Performing startup cleanup...")
        try:
            cleanup_old_downloads()
        except Exception as e:
            logger.error(f"Error during startup cleanup: {e}")
    
    # Log disk space information
    space_info = get_disk_space_info()
    logger.info(
        f"Disk space: {space_info['free_gb']:.2f} GB free "
        f"({space_info['free_mb']:.0f} MB) out of {space_info['total'] / (1024**3):.2f} GB total"
    )
    if space_info['free_mb'] < config.WARN_LOW_SPACE_MB:
        logger.warning(
            f"Low disk space warning: only {space_info['free_mb']:.0f} MB available"
        )
    
    application = Application.builder().token(BOT_TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help",  help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("history", history_command))

    # Inline button handler
    application.add_handler(CallbackQueryHandler(button_callback))

    # Message handlers
    application.add_handler(MessageHandler(filters.Sticker.ALL, handle_sticker))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Error handler
    application.add_error_handler(error_handler)
    
    # Schedule periodic cleanup job if enabled
    if config.AUTO_CLEANUP_ENABLED and config.CLEANUP_INTERVAL_HOURS > 0:
        job_queue = application.job_queue
        if job_queue:
            interval_seconds = config.CLEANUP_INTERVAL_HOURS * 3600
            job_queue.run_repeating(
                periodic_cleanup_job,
                interval=interval_seconds,
                first=interval_seconds,  # First run after interval
                name="periodic_cleanup"
            )
            logger.info(
                f"Scheduled periodic cleanup job every {config.CLEANUP_INTERVAL_HOURS} hours"
            )

    logger.info("Bot is starting...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)

    logger.info("Bot is running. Press Ctrl+C to stop.")
    try:
        import asyncio
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot is stopping...")
    finally:
        # Perform final cleanup before shutdown
        if config.AUTO_CLEANUP_ENABLED:
            logger.info("Performing shutdown cleanup...")
            try:
                cleanup_old_downloads()
            except Exception as e:
                logger.error(f"Error during shutdown cleanup: {e}")
        
        await application.updater.stop()
        await application.stop()
        await application.shutdown()


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
