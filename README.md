# Tabletop Gaming Ranking System

A Discord bot that implements the Glicko-2 rating system for tabletop games including Warhammer 40k, Age of Sigmar, Magic: The Gathering, and more!

## Features

- **Multiple Game Systems**: Support for Warhammer 40k, Age of Sigmar, MTG, and ability to add custom games
- **Glicko-2 Rating System**: Industry-standard rating algorithm used by Chess.com, Lichess, and more
- **Discord Integration**: Easy-to-use slash commands
- **Minimal Cost**: Uses SQLite database and can be hosted on free tiers (Railway, Fly.io, etc.)
- **Independent Rankings**: Each game system maintains separate player rankings

## Setup

### Prerequisites

- Python 3.9 or higher
- Discord account and server with admin permissions

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd Warhammer-Ranking-System
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a Discord Bot:
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Click "New Application"
   - Go to "Bot" section and click "Add Bot"
   - Copy the bot token
   - Enable "MESSAGE CONTENT INTENT" under Privileged Gateway Intents
   - Go to OAuth2 > URL Generator
   - Select scopes: `bot`, `applications.commands`
   - Select permissions: `Send Messages`, `Use Slash Commands`
   - Copy the generated URL and invite the bot to your server

5. Configure environment:
```bash
cp .env.example .env
# Edit .env and add your Discord bot token and guild ID
```

6. Run the bot:
```bash
python bot.py
```

## Commands

- `/register <game>` - Register yourself for a game system
- `/record_match <game> <winner> <loser>` - Record a match result
- `/rankings <game>` - View current rankings for a game
- `/player_stats <game> <player>` - View a player's statistics
- `/add_game <game_name>` - Add a new game system (admin only)
- `/games` - List all available game systems

## Glicko-2 Rating System

The bot uses the Glicko-2 rating system, which consists of three components:

- **Rating (r)**: The player's skill level (starts at 1500)
- **Rating Deviation (RD)**: Uncertainty in the rating (starts at 350)
- **Volatility (σ)**: Degree of expected fluctuation in rating

Players with more matches have lower RD values, making their ratings more stable.

## Deployment Options (Free Tier)

### Railway.app
1. Sign up at [Railway.app](https://railway.app)
2. Connect your GitHub repository
3. Add environment variables in Railway dashboard
4. Deploy!

### Fly.io
1. Install flyctl: `curl -L https://fly.io/install.sh | sh`
2. Run `fly launch`
3. Set secrets: `fly secrets set DISCORD_TOKEN=your_token`
4. Deploy: `fly deploy`

## Database Schema

The bot uses SQLite with the following tables:
- `games`: Stores available game systems
- `players`: Player information per game system
- `matches`: Match history and results
- `ratings`: Player ratings over time

## Contributing

Feel free to submit issues and pull requests!

## License

MIT License
