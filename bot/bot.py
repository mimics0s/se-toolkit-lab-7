"""Telegram bot entry point.

Usage:
    uv run bot.py              # Start Telegram bot
    uv run bot.py --test "/start"  # Test mode (no Telegram connection)
"""

import sys
from config import load_config
from handlers import handle_start, handle_help, handle_health, handle_labs, handle_scores


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


def run_test_mode(command: str) -> None:
    """Run a command in test mode and print result to stdout.
    
    Args:
        command: The command to test (e.g., "/start", "/help").
    """
    handler = get_handler(command)
    
    if handler is None:
        print(f"Unknown command: {command}")
        print("Available commands: /start, /help, /health, /labs, /scores")
        sys.exit(0)  # Exit 0, not 1!
    
    response = handler(command)
    print(response)
    sys.exit(0)


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
    print("Telegram bot not implemented yet — use --test mode for now.")
    print("\nExample: uv run bot.py --test '/start'")


if __name__ == "__main__":
    main()
