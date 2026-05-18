A robust, modernized utility Discord bot. This version represents a complete overhaul of the original 4-year-old codebase, bringing it into the modern era of Discord development.

## 🌟 Key Features

### 🔢 Advanced Arithmetics
- **Standard Operations**: Upgraded `^add`, `^sub`, `^mul`, `^div`, and `^square` with float rounding protection and premium formatting.
- **Calculator Engine (`^calc`)**: Safe evaluation supporting advanced functions (trigonometry, logs, roots, factorials, gcd, lcm), mathematical constants, and channel-wide `ans` variable memory.
- **Specialized Commands**:
  - `^stats <numbers>` - Comprehensive dataset statistical analysis.
  - `^prime <n>` - primality check, prime factors breakdown, and full divisors list.
  - `^solve <a> <b> [c]` - Solves linear ($ax+b=0$) and quadratic ($ax^2+bx+c=0$) equations (real & complex).
  - `^convert <val> <from> <to>` - High-precision unit converter (Temp, Length, Weight, Data).

### 🛠 Utility & Moderation
- **Quote System**: `^quote` fetches motivational quotes via the ZenQuotes API.
- **Bot Info**: `^ping` to check latency.
- **Admin Tools**: `^kick`, `^ban`, `^unban`, and `^clear` for server management.

### ⚡ Modern Infrastructure
- **Asynchronous Engine**: Built with `discord.py` 2.0+ and `aiohttp` for maximum performance.
- **Secure Configuration**: Uses `.env` for token management (Zero hardcoded secrets).
- **Intents Ready**: Fully compatible with Discord's Privileged Gateway Intents.

## 🚀 Getting Started

1. **Prerequisites**:
   - Python 3.8+
   - A Discord Bot Token (from the [Developer Portal](https://discord.com/developers/applications))

2. **Installation**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuration**:
   Create a `.env` file in the root directory:
   ```env
   DISCORD_TOKEN=your_token_here
   ```

4. **Run the Bot**:
   ```bash
   python reuven_bot.py
   ```
