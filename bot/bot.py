"""Telegram bot entry point.

Usage:
    uv run bot.py              # Start Telegram bot
    uv run bot.py --test "/start"  # Test mode (no Telegram connection)
    uv run bot.py --test "what labs are available?"  # Natural language query
"""

import sys
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)
from config import load_config
from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
    route_natural_language,
)
from handlers.buttons import get_start_keyboard


def get_handler(command: str):
    """Get handler function for a command.

    Args:
        command: The command string (e.g., "/start", "/help").

    Returns:
        Handler function or None if command not recognized.
    """
    handlers = {
        "/start": handle_start,
        "/help": handle_help,
        "/health": handle_health,
        "/labs": handle_labs,
        "/scores": handle_scores,
    }

    # Extract command name (first word)
    cmd_name = command.split()[0].lower()
    return handlers.get(cmd_name)


def is_natural_language_query(text: str) -> bool:
    """Check if input is a natural language query (not a slash command).

    Args:
        text: User input text.

    Returns:
        True if it's a natural language query, False if it's a slash command.
    """
    return not text.strip().startswith("/")


def run_test_mode(command: str) -> None:
    """Run a command in test mode and print result to stdout.

    Args:
        command: The command to test (e.g., "/start", "/help", or natural language).
    """
    # Check if this is a natural language query
    if is_natural_language_query(command):
        response = route_natural_language(command)
        print(response)
        sys.exit(0)

    # Otherwise, treat as a slash command
    handler = get_handler(command)

    if handler is None:
        print(f"Unknown command: {command}")
        print("Available commands: /start, /help, /health, /labs, /scores")
        sys.exit(0)  # Exit 0, not 1!

    response = handler(command)
    print(response)
    sys.exit(0)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command with inline keyboard."""
    response = handle_start("/start")
    keyboard = get_start_keyboard()
    await update.message.reply_text(
        response.split("\n\n[Inline keyboard")[0],
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    response = handle_help("/help")
    await update.message.reply_text(response)


async def cmd_health(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /health command."""
    response = handle_health("/health")
    await update.message.reply_text(response)


async def cmd_labs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /labs command."""
    response = handle_labs("/labs")
    await update.message.reply_text(response)


async def cmd_scores(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /scores command."""
    command = "/scores " + " ".join(context.args)
    response = handle_scores(command)
    await update.message.reply_text(response)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle natural language messages via LLM."""
    user_message = update.message.text
    response = route_natural_language(user_message)
    await update.message.reply_text(response)


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline keyboard button callbacks."""
    query = update.callback_query
    await query.answer()

    callback_data = query.data
    user_message = ""

    # Map callback data to natural language queries
    if callback_data == "query_labs":
        user_message = "What labs are available?"
    elif callback_data == "query_students":
        user_message = "How many students are enrolled?"
    elif callback_data == "query_scores":
        user_message = "Show me scores for lab 1"
    elif callback_data == "query_top":
        user_message = "Who are the top 5 students?"
    elif callback_data == "query_pass_rates":
        user_message = "What are the pass rates for lab 1?"
    elif callback_data == "query_groups":
        user_message = "Compare group performance for lab 1"
    elif callback_data == "query_analytics":
        user_message = "Show analytics for lab 1"
    elif callback_data == "action_sync":
        user_message = "Sync the data"
    elif callback_data == "query_scores_help":
        user_message = "Show scores for lab 1"
    elif callback_data == "query_top_help":
        user_message = "Show top learners"

    if user_message:
        response = route_natural_language(user_message)
        await query.edit_message_text(response)


def main() -> None:
    """Main entry point."""
    config = load_config()

    # Check for --test mode
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        if len(sys.argv) < 3:
            print("Usage: uv run bot.py --test <command>")
            print("Example: uv run bot.py --test '/start'")
            sys.exit(1)

        command = sys.argv[2]
        run_test_mode(command)
        return

    # Normal mode: start Telegram bot
    if not config["bot_token"]:
        print("Error: BOT_TOKEN not set in .env.bot.secret")
        print("Please create .env.bot.secret with your bot token.")
        sys.exit(1)

    print("Starting Telegram bot...")
    print(f"Bot token: {config['bot_token'][:10]}...")

    # Set up logging
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    # Build application
    application = Application.builder().token(config["bot_token"]).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("help", cmd_help))
    application.add_handler(CommandHandler("health", cmd_health))
    application.add_handler(CommandHandler("labs", cmd_labs))
    application.add_handler(CommandHandler("scores", cmd_scores))

    # Register callback handler for inline buttons
    application.add_handler(CallbackQueryHandler(handle_callback))

    # Register message handler for natural language queries
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    print("Bot is running. Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
