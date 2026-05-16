A utility Discord bot built with `discord.py`.

## Features
- **Utility Commands**: `^ping`, `^add`, `^square`, `^quote`.
- **Moderation**: `^kick`, `^ban`, `^unban`, `^clear`.
- **Fun**: Responds to "who is the goat?".
- **Asynchronous**: Uses `aiohttp` for non-blocking API calls.
- **Secure**: Configuration via environment variables.

## Setup
1. Clone the repository.
2. Create a `.env` file and add your `DISCORD_TOKEN`.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the bot:
   ```bash
   python3 reuven_bot.py
   ```

## Development
This bot was originally created 4 years ago and was modernized in May 2026 to support Discord's Privileged Gateway Intents and asynchronous patterns.
