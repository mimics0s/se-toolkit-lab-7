"""Basic command handlers.

Each handler is a pure function: takes command text and returns response.
No Telegram dependency — same function works from --test mode or Telegram.
"""

from config import load_config
from services.api_client import LMSAPIClient
from handlers.buttons import get_start_keyboard


def _get_api_client() -> LMSAPIClient:
    """Create an API client from config.

    Returns:
        Configured LMSAPIClient instance.
    """
    config = load_config()
    return LMSAPIClient(
        base_url=config["lms_api_base_url"],
        api_key=config["lms_api_key"],
    )


def handle_start(command: str) -> str:
    """Handle /start command.

    Args:
        command: The command text (e.g., "/start").

    Returns:
        Welcome message with inline keyboard buttons.
    """
    welcome = """Welcome to the LMS Bot! 🎓

I can help you explore lab data, check scores, and analyze student performance.

Just ask me questions like:
• "What labs are available?"
• "Show me scores for lab 4"
• "Which lab has the lowest pass rate?"
• "Who are the top 5 students?"

Or use the buttons below to get started!"""
    
    # Include keyboard info in the response for test mode
    keyboard = get_start_keyboard()
    keyboard_info = "\n\n[Inline keyboard with buttons: "
    button_labels = []
    for row in keyboard:
        for btn in row:
            button_labels.append(btn["text"])
    keyboard_info += ", ".join(button_labels) + "]"
    
    return welcome + keyboard_info


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
        Backend health status with item count.
    """
    client = _get_api_client()
    try:
        is_healthy = client.is_healthy()
        item_count = client.get_item_count() if is_healthy else 0
        if is_healthy:
            return f"Backend status: OK (running) - Items: {item_count}"
        else:
            return "Backend status: Unreachable"
    except Exception as e:
        return f"Backend status: Error - {type(e).__name__}"


def handle_labs(command: str) -> str:
    """Handle /labs command.

    Args:
        command: The command text (e.g., "/labs").

    Returns:
        List of available labs from the backend.
    """
    client = _get_api_client()
    try:
        labs = client.get_labs()
        if not labs:
            return "No labs available."
        lines = ["Available labs:"]
        for lab in labs:
            lines.append(f"- {lab['title']}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error fetching labs: {type(e).__name__}"


def handle_scores(command: str) -> str:
    """Handle /scores command.

    Args:
        command: The command text (e.g., "/scores lab-04").

    Returns:
        Scores information for the specified lab.
    """
    # Parse lab argument
    parts = command.strip().split()
    if len(parts) < 2:
        return "Usage: /scores <lab-name> (e.g., /scores lab-01)"

    lab_arg = parts[1].lower()

    client = _get_api_client()
    try:
        # Find the lab by matching title
        labs = client.get_labs()
        lab = None

        for l in labs:
            title_lower = l["title"].lower()
            # Direct substring match
            if lab_arg in title_lower or title_lower.startswith(lab_arg):
                lab = l
                break

        if not lab:
            return f"Lab not found: {lab_arg}"

        # Get tasks for this lab
        tasks = client.get_tasks_for_lab(lab["id"])

        # Build response with task info
        lines = [f"Scores for {lab['title']}:"]
        for i, task in enumerate(tasks, 1):
            lines.append(f"{i}. {task['title']} - No attempts yet")

        if not tasks:
            lines.append("No tasks found for this lab.")

        return "\n".join(lines)
    except Exception as e:
        return f"Error fetching scores: {type(e).__name__}"
