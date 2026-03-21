"""Configuration loader for the Telegram bot.

Reads settings from environment variables (loaded from .env.bot.secret).
"""

import os
from pathlib import Path
from dotenv import load_dotenv


def load_config() -> dict[str, str]:
    """Load configuration from environment variables.
    
    Returns:
        Dictionary with bot configuration values.
    """
    # Load .env.bot.secret from parent directory
    bot_dir = Path(__file__).parent
    env_file = bot_dir.parent / ".env.bot.secret"
    load_dotenv(env_file)
    
    return {
        "bot_token": os.getenv("BOT_TOKEN", ""),
        "lms_api_base_url": os.getenv("LMS_API_BASE_URL", "http://localhost:42002"),
        "lms_api_key": os.getenv("LMS_API_KEY", ""),
        "llm_api_key": os.getenv("LLM_API_KEY", ""),
        "llm_api_base_url": os.getenv("LLM_API_BASE_URL", ""),
        "llm_api_model": os.getenv("LLM_API_MODEL", "qwen3-coder-flash"),
    }
