# Telegram Bot Development Plan

## Overview

This document describes the implementation plan for the LMS Telegram bot. The bot provides students with access to their lab scores, health checks, and intelligent query handling through an LLM-powered intent router.

## Architecture

The bot follows a **separation of concerns** pattern:

1. **Handlers** (`handlers/`) — Pure functions that take command text and return responses. They have no Telegram dependency, making them testable via `--test` mode and reusable in unit tests.

2. **Services** (`services/`) — External API clients (LMS backend, LLM). These handle HTTP requests, authentication, and error handling.

3. **Entry Point** (`bot.py`) — Telegram client initialization and `--test` mode routing.

## Implementation Phases

### Task 1: Scaffold (Current)

Basic project structure with placeholder handlers. Test mode works without Telegram connection. Commands return static text.

### Task 2: Backend Integration

Connect handlers to the LMS backend API:
- `/health` — Real backend health check via `GET /health`
- `/labs` — Fetch available labs from `GET /items/`
- `/scores <lab>` — Query scores from backend with Bearer token auth

### Task 3: LLM Intent Routing

Add natural language support:
- User types "what labs are available" → LLM routes to `/labs` handler
- Tool descriptions guide LLM to pick correct handler
- Fallback for unrecognized intents

### Task 4: Deployment

Docker containerization for the bot:
- Dockerfile with Python runtime
- Environment variables for secrets
- Health checks and restart policies

## Testing Strategy

- **Test mode**: `uv run bot.py --test "/command"` for quick verification
- **Unit tests**: Test handlers directly without Telegram
- **Integration tests**: Full bot in Docker with mock Telegram

## Security Considerations

- Bot token and API keys stored in `.env.bot.secret` (gitignored)
- Bearer token auth for LMS API requests
- No secrets committed to git
