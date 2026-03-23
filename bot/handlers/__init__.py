"""Command handlers for the Telegram bot.

Handlers are pure functions: they take input and return text.
They don't know about Telegram — same function works from --test mode,
unit tests, or Telegram.
"""

from handlers.commands.basic import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
)
from handlers.intent_router import route_natural_language

__all__ = [
    "handle_start",
    "handle_help",
    "handle_health",
    "handle_labs",
    "handle_scores",
    "route_natural_language",
]
