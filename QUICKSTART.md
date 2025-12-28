# Quick Start Guide

## Setup Steps

### 1. Install Python Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Create Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to "Bot" section:
   - Click "Add Bot"
   - Copy the bot token (keep it secret!)
   - Enable these Privileged Gateway Intents:
     - ✅ SERVER MEMBERS INTENT
     - ✅ MESSAGE CONTENT INTENT
4. Go to "OAuth2" > "URL Generator":
   - Select scopes: `bot` and `applications.commands`
   - Select bot permissions:
     - Send Messages
     - Embed Links
     - Read Message History
     - Use Slash Commands
   - Copy the generated URL and open it to invite the bot to your server

### 3. Get Your Guild (Server) ID

1. Enable Developer Mode in Discord:
   - User Settings > Advanced > Developer Mode (toggle on)
2. Right-click your server icon and select "Copy ID"

### 4. Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your values:
DISCORD_TOKEN=your_bot_token_here
GUILD_ID=your_guild_id_here
```

### 5. Run the Bot

```bash
python bot.py
```

The bot should now be online in your Discord server!

## Available Commands

- `/games` - List all available game systems
- `/register <game>` - Register for a game (e.g., `/register warhammer40k`)
- `/record_match <game> <winner> <loser>` - Record a match result
- `/rankings <game>` - View rankings for a game
- `/player_stats <game> [player]` - View player statistics
- `/match_history <game>` - View recent match history
- `/add_game <game_name> <display_name>` - Add new game (admin only)

## Default Games

The system comes with these games pre-configured:
- `warhammer40k` - Warhammer 40,000
- `aos` - Age of Sigmar
- `mtg` - Magic: The Gathering

## Example Usage Flow

```
1. /register warhammer40k
   → You're now registered with starting rating 1500 ± 350

2. /record_match warhammer40k @Player1 @Player2
   → Match recorded, ratings updated using Glicko-2

3. /rankings warhammer40k
   → View current leaderboard

4. /player_stats warhammer40k @Player1
   → See detailed stats for Player1
```

## Free Hosting Options

### Option 1: Railway.app (Recommended)

1. Sign up at [Railway.app](https://railway.app)
2. Click "New Project" > "Deploy from GitHub repo"
3. Connect your repository
4. Add environment variables:
   - Click on your service
   - Go to "Variables" tab
   - Add `DISCORD_TOKEN` and `GUILD_ID`
5. Deploy!

Railway offers 500 hours/month on the free tier (enough for 24/7 operation).

### Option 2: Fly.io

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Launch app (follow prompts)
fly launch

# Set secrets
fly secrets set DISCORD_TOKEN=your_token
fly secrets set GUILD_ID=your_guild_id

# Deploy
fly deploy
```

Fly.io offers 3 shared-cpu VMs on the free tier.

### Option 3: Self-host (Raspberry Pi, old PC, etc.)

Just run `python bot.py` and keep it running. Consider using:
- `tmux` or `screen` to keep it running when you disconnect
- systemd service for automatic restart on reboot

## Troubleshooting

### Bot is offline
- Check that your `DISCORD_TOKEN` is correct
- Verify the bot is invited to your server with proper permissions

### Commands don't show up
- Make sure `GUILD_ID` is set correctly
- Wait a few minutes for Discord to sync commands
- Try kicking and re-inviting the bot

### Database errors
- Make sure the directory is writable
- Delete `rankings.db` to reset the database

## Advanced Configuration

### Adjusting Rating System Parameters

Edit `rating_system.py` to change the `tau` parameter:
- Lower tau (0.3): More conservative rating changes
- Higher tau (1.2): More volatile rating changes
- Default (0.5): Balanced

### Adding Custom Games

Admins can add games via Discord:
```
/add_game kill_team "Kill Team"
/add_game necromunda "Necromunda"
```

## Support

For issues or questions:
1. Check the README.md for detailed documentation
2. Review the code comments in `bot.py`, `database.py`, and `rating_system.py`
3. Create an issue on GitHub
