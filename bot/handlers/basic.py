"""Basic command handlers.

Each handler is a pure function: takes command text and returns response.
No Telegram dependency — same function works from --test mode or Telegram.
"""


def handle_start(command: str) -> str:
    """Handle /start command.
    
    Args:
        command: The command text (e.g., "/start").
        
    Returns:
        Welcome message.
    """
    return "Welcome to the LMS Bot! Use /help to see available commands."


def handle_help(command: str) -> str:
    """Handle /help command.
    
    Args:
        command: The command text (e.g., "/help").
        
    Returns:
        List of available commands.
    """
    return """Available commands:
/start - Welcome message
/help - Show this help
/health - Check backend status
/labs - List available labs
/scores <lab> - Get scores for a lab"""


def handle_health(command: str) -> str:
    """Handle /health command.
    
    Args:
        command: The command text (e.g., "/health").
        
    Returns:
        Backend health status (placeholder for now).
    """
    return "Backend status: OK (placeholder)"


def handle_labs(command: str) -> str:
    """Handle /labs command.
    
    Args:
        command: The command text (e.g., "/labs").
        
    Returns:
        List of available labs (placeholder for now).
    """
    return "Available labs: lab-01, lab-02, lab-03, lab-04 (placeholder)"


def handle_scores(command: str) -> str:
    """Handle /scores command.
    
    Args:
        command: The command text (e.g., "/scores lab-04").
        
    Returns:
        Scores information (placeholder for now).
    """
    return f"Scores for {command}: Not implemented yet (placeholder)"
