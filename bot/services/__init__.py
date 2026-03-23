"""Services for the Telegram bot.

Services handle external dependencies (APIs, LLMs, databases).
They are separate from handlers — this is *separation of concerns*.
"""

from services.api_client import LMSAPIClient

__all__ = ["LMSAPIClient"]
