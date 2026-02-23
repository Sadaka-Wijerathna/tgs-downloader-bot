"""
Download history tracking module for TGS Emoji Downloader bot.

This module provides functionality to track and manage download history
for users, storing information about completed downloads in a JSON file.
"""

import os
import json
import time
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import threading

logger = logging.getLogger(__name__)


class DownloadHistory:
    """Manages download history with JSON-based persistence."""
    
    def __init__(self, history_file: str = "download_history.json", max_entries_per_user: int = 50):
        """Initialize the download history manager.
        
        Args:
            history_file: Path to the JSON file for storing history
            max_entries_per_user: Maximum number of history entries per user
        """
        self.history_file = history_file
        self.max_entries_per_user = max_entries_per_user
        self._lock = threading.Lock()
        self._ensure_history_file()
    
    def _ensure_history_file(self) -> None:
        """Ensure the history file exists."""
        if not os.path.exists(self.history_file):
            with open(self.history_file, 'w') as f:
                json.dump({}, f)
            logger.info(f"Created new history file: {self.history_file}")
    
    def _load_history(self) -> Dict:
        """Load history from JSON file.
        
        Returns:
            Dictionary with user_id as keys and list of download entries as values
        """
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Error loading history file: {e}")
            return {}
    
    def _save_history(self, history: Dict) -> None:
        """Save history to JSON file.
        
        Args:
            history: Dictionary with user_id as keys and list of download entries as values
        """
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving history file: {e}")
    
    def add_entry(
        self,
        user_id: int,
        pack_name: str,
        pack_title: str,
        total_stickers: int,
        success_count: int,
        failed_count: int,
        file_size: int,
        duration_seconds: int
    ) -> None:
        """Add a download entry to the history.
        
        Args:
            user_id: Telegram user ID
            pack_name: Pack identifier (e.g., "AnimatedEmojies")
            pack_title: Human-readable pack title
            total_stickers: Total number of animated stickers in pack
            success_count: Number of successfully downloaded stickers
            failed_count: Number of failed downloads
            file_size: Size of the ZIP file in bytes
            duration_seconds: Time taken for the download in seconds
        """
        with self._lock:
            history = self._load_history()
            user_id_str = str(user_id)
            
            if user_id_str not in history:
                history[user_id_str] = []
            
            entry = {
                'timestamp': time.time(),
                'date': datetime.now().isoformat(),
                'pack_name': pack_name,
                'pack_title': pack_title,
                'total_stickers': total_stickers,
                'success_count': success_count,
                'failed_count': failed_count,
                'file_size': file_size,
                'duration_seconds': duration_seconds,
                'status': 'completed' if success_count > 0 else 'failed'
            }
            
            history[user_id_str].append(entry)
            
            # Limit entries per user
            if len(history[user_id_str]) > self.max_entries_per_user:
                history[user_id_str] = history[user_id_str][-self.max_entries_per_user:]
            
            self._save_history(history)
            logger.info(f"Added history entry for user {user_id}: {pack_name}")
    
    def get_user_history(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get download history for a specific user.
        
        Args:
            user_id: Telegram user ID
            limit: Maximum number of entries to return (most recent first)
        
        Returns:
            List of download entries, sorted by timestamp (newest first)
        """
        with self._lock:
            history = self._load_history()
            user_id_str = str(user_id)
            
            if user_id_str not in history:
                return []
            
            entries = history[user_id_str]
            # Sort by timestamp, newest first
            entries.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
            
            return entries[:limit]
    
    def clear_user_history(self, user_id: int) -> int:
        """Clear all history for a specific user.
        
        Args:
            user_id: Telegram user ID
        
        Returns:
            Number of entries cleared
        """
        with self._lock:
            history = self._load_history()
            user_id_str = str(user_id)
            
            if user_id_str not in history:
                return 0
            
            count = len(history[user_id_str])
            del history[user_id_str]
            self._save_history(history)
            
            logger.info(f"Cleared {count} history entries for user {user_id}")
            return count
    
    def cleanup_old_entries(self, max_age_days: int = 30) -> int:
        """Remove history entries older than specified days.
        
        Args:
            max_age_days: Maximum age of entries to keep
        
        Returns:
            Number of entries removed
        """
        with self._lock:
            history = self._load_history()
            cutoff_time = time.time() - (max_age_days * 24 * 3600)
            removed_count = 0
            
            for user_id in list(history.keys()):
                original_count = len(history[user_id])
                history[user_id] = [
                    entry for entry in history[user_id]
                    if entry.get('timestamp', 0) > cutoff_time
                ]
                removed_count += original_count - len(history[user_id])
                
                # Remove user entry if no history left
                if not history[user_id]:
                    del history[user_id]
            
            if removed_count > 0:
                self._save_history(history)
                logger.info(f"Cleaned up {removed_count} old history entries")
            
            return removed_count
    
    def get_stats(self) -> Dict:
        """Get overall statistics about the history.
        
        Returns:
            Dictionary with statistics (total_users, total_entries, etc.)
        """
        with self._lock:
            history = self._load_history()
            
            total_users = len(history)
            total_entries = sum(len(entries) for entries in history.values())
            
            return {
                'total_users': total_users,
                'total_entries': total_entries,
                'avg_entries_per_user': total_entries / total_users if total_users > 0 else 0
            }


# Global instance
_history_instance: Optional[DownloadHistory] = None


def get_history_manager() -> DownloadHistory:
    """Get the global download history manager instance.
    
    Returns:
        DownloadHistory instance
    """
    global _history_instance
    if _history_instance is None:
        _history_instance = DownloadHistory()
    return _history_instance
