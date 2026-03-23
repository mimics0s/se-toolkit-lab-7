"""Inline keyboard buttons for the Telegram bot.

Provides keyboard layouts for common actions.
"""

from typing import Any


def get_start_keyboard() -> list[list[dict[str, Any]]]:
    """Get the inline keyboard for the /start command.

    Returns:
        Inline keyboard markup as a list of button rows.
        Each row is a list of button dicts with 'text' and 'callback_data'.
    """
    return [
        [
            {"text": "📚 What labs are available?", "callback_data": "query_labs"},
            {"text": "👥 How many students?", "callback_data": "query_students"},
        ],
        [
            {"text": "📊 Lab scores", "callback_data": "query_scores"},
            {"text": "🏆 Top learners", "callback_data": "query_top"},
        ],
        [
            {"text": "📈 Pass rates", "callback_data": "query_pass_rates"},
            {"text": "👥 Group comparison", "callback_data": "query_groups"},
        ],
        [
            {"text": "🔄 Sync data", "callback_data": "action_sync"},
        ],
    ]


def get_help_keyboard() -> list[list[dict[str, Any]]]:
    """Get the inline keyboard for the /help command.

    Returns:
        Inline keyboard markup.
    """
    return [
        [
            {"text": "📚 Available labs", "callback_data": "query_labs"},
            {"text": "📊 View scores", "callback_data": "query_scores_help"},
        ],
        [
            {"text": "🏆 Leaderboard", "callback_data": "query_top_help"},
            {"text": "📈 Analytics", "callback_data": "query_analytics"},
        ],
    ]


def format_keyboard_message(text: str, keyboard: list[list[dict[str, Any]]]) -> dict[str, Any]:
    """Format a message with inline keyboard for Telegram API.

    Args:
        text: Message text to display.
        keyboard: Inline keyboard markup.

    Returns:
        Dict suitable for sending to Telegram Bot API.
    """
    return {
        "text": text,
        "reply_markup": {
            "inline_keyboard": keyboard,
        },
        "parse_mode": "Markdown",
    }
