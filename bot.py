"""
Discord bot for tabletop gaming ranking system.
Supports Warhammer 40k, Age of Sigmar, MTG, and custom games.
Uses Glicko-2 rating system.
"""

import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
from database import Database
from rating_system import RatingSystem
from datetime import datetime

# Load environment variables
load_dotenv()

# Bot configuration
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = os.getenv('GUILD_ID')

# Initialize bot with intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
db = Database()
rating_system = RatingSystem()

# Guild object for slash commands
MY_GUILD = discord.Object(id=int(GUILD_ID)) if GUILD_ID else None


@bot.event
async def on_ready():
    """Initialize bot when ready."""
    print(f'{bot.user} has connected to Discord!')
    await db.initialize()
    print('Database initialized')
    
    # Sync commands
    if MY_GUILD:
        bot.tree.copy_global_to(guild=MY_GUILD)
        await bot.tree.sync(guild=MY_GUILD)
        print(f'Commands synced to guild {GUILD_ID}')
    else:
        await bot.tree.sync()
        print('Commands synced globally')


@bot.tree.command(name="games", description="List all available game systems")
async def games_command(interaction: discord.Interaction):
    """List all available games."""
    games = await db.get_all_games()
    
    if not games:
        await interaction.response.send_message("No games available yet!")
        return
    
    embed = discord.Embed(
        title="🎮 Available Game Systems",
        description="Register for any of these games using `/register <game>`",
        color=discord.Color.blue()
    )
    
    for game_name, display_name in games:
        embed.add_field(name=display_name, value=f"Command: `{game_name}`", inline=False)
    
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="register", description="Register yourself for a game system")
@app_commands.describe(game="The game system to register for (e.g., warhammer40k, aos, mtg)")
async def register_command(interaction: discord.Interaction, game: str):
    """Register a player for a specific game."""
    # Get game
    game_data = await db.get_game(game)
    if not game_data:
        await interaction.response.send_message(
            f"❌ Game '{game}' not found! Use `/games` to see available games.",
            ephemeral=True
        )
        return
    
    game_id, game_name, display_name = game_data
    
    # Register player
    success = await db.register_player(
        str(interaction.user.id),
        interaction.user.display_name,
        game_id
    )
    
    if success:
        embed = discord.Embed(
            title="✅ Registration Successful!",
            description=f"{interaction.user.mention} is now registered for **{display_name}**",
            color=discord.Color.green()
        )
        embed.add_field(name="Starting Rating", value="1500 ± 350", inline=True)
        embed.add_field(name="Rating Class", value="Novice", inline=True)
        embed.set_footer(text="Your rating will update as you play matches!")
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(
            f"ℹ️ You're already registered for {display_name}!",
            ephemeral=True
        )


@bot.tree.command(name="record_match", description="Record a match result")
@app_commands.describe(
    game="The game system",
    winner="The player who won",
    loser="The player who lost"
)
async def record_match_command(
    interaction: discord.Interaction,
    game: str,
    winner: discord.Member,
    loser: discord.Member
):
    """Record a match result and update ratings."""
    # Validate different players
    if winner.id == loser.id:
        await interaction.response.send_message(
            "❌ Winner and loser must be different players!",
            ephemeral=True
        )
        return
    
    # Get game
    game_data = await db.get_game(game)
    if not game_data:
        await interaction.response.send_message(
            f"❌ Game '{game}' not found! Use `/games` to see available games.",
            ephemeral=True
        )
        return
    
    game_id, game_name, display_name = game_data
    
    # Get players
    winner_data = await db.get_player(str(winner.id), game_id)
    loser_data = await db.get_player(str(loser.id), game_id)
    
    if not winner_data:
        await interaction.response.send_message(
            f"❌ {winner.mention} is not registered for {display_name}! Use `/register {game_name}`",
            ephemeral=True
        )
        return
    
    if not loser_data:
        await interaction.response.send_message(
            f"❌ {loser.mention} is not registered for {display_name}! Use `/register {game_name}`",
            ephemeral=True
        )
        return
    
    # Store original ratings
    winner_rating_before = winner_data['rating']
    loser_rating_before = loser_data['rating']
    
    # Calculate new ratings
    updated_winner, updated_loser = rating_system.update_ratings(winner_data, loser_data)
    
    # Update database
    await db.update_player_rating(
        winner_data['id'],
        updated_winner['rating'],
        updated_winner['rating_deviation'],
        updated_winner['volatility'],
        True
    )
    
    await db.update_player_rating(
        loser_data['id'],
        updated_loser['rating'],
        updated_loser['rating_deviation'],
        updated_loser['volatility'],
        False
    )
    
    # Record match
    await db.record_match(
        game_id,
        winner_data['id'],
        loser_data['id'],
        winner_rating_before,
        updated_winner['rating'],
        loser_rating_before,
        updated_loser['rating'],
        str(interaction.user.id)
    )
    
    # Calculate rating changes
    winner_change = updated_winner['rating'] - winner_rating_before
    loser_change = updated_loser['rating'] - loser_rating_before
    
    # Create result embed
    embed = discord.Embed(
        title=f"🏆 Match Recorded - {display_name}",
        description=f"{winner.mention} defeated {loser.mention}",
        color=discord.Color.gold(),
        timestamp=datetime.now()
    )
    
    embed.add_field(
        name=f"🥇 {winner.display_name} (Winner)",
        value=(
            f"**Rating:** {rating_system.format_rating(winner_rating_before, winner_data['rating_deviation'])} → "
            f"{rating_system.format_rating(updated_winner['rating'], updated_winner['rating_deviation'])}\n"
            f"**Change:** {winner_change:+.1f}\n"
            f"**Class:** {rating_system.get_rating_class(updated_winner['rating'])}\n"
            f"**Record:** {winner_data['wins'] + 1}W - {winner_data['losses']}L"
        ),
        inline=False
    )
    
    embed.add_field(
        name=f"🥈 {loser.display_name} (Loser)",
        value=(
            f"**Rating:** {rating_system.format_rating(loser_rating_before, loser_data['rating_deviation'])} → "
            f"{rating_system.format_rating(updated_loser['rating'], updated_loser['rating_deviation'])}\n"
            f"**Change:** {loser_change:+.1f}\n"
            f"**Class:** {rating_system.get_rating_class(updated_loser['rating'])}\n"
            f"**Record:** {loser_data['wins']}W - {loser_data['losses'] + 1}L"
        ),
        inline=False
    )
    
    embed.set_footer(text=f"Recorded by {interaction.user.display_name}")
    
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="rankings", description="View current rankings for a game")
@app_commands.describe(
    game="The game system",
    limit="Number of players to show (default: 25)"
)
async def rankings_command(interaction: discord.Interaction, game: str, limit: int = 25):
    """Display rankings for a game."""
    # Validate limit
    if limit < 1 or limit > 100:
        await interaction.response.send_message(
            "❌ Limit must be between 1 and 100!",
            ephemeral=True
        )
        return
    
    # Get game
    game_data = await db.get_game(game)
    if not game_data:
        await interaction.response.send_message(
            f"❌ Game '{game}' not found! Use `/games` to see available games.",
            ephemeral=True
        )
        return
    
    game_id, game_name, display_name = game_data
    
    # Get rankings
    rankings = await db.get_rankings(game_id, limit)
    
    if not rankings:
        await interaction.response.send_message(
            f"No players registered for {display_name} yet!",
            ephemeral=True
        )
        return
    
    # Create rankings embed
    embed = discord.Embed(
        title=f"🏆 {display_name} Rankings",
        description=f"Top {len(rankings)} players",
        color=discord.Color.gold()
    )
    
    for i, player in enumerate(rankings, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"#{i}"
        rating_str = rating_system.format_rating(player['rating'], player['rating_deviation'])
        rating_class = rating_system.get_rating_class(player['rating'])
        win_rate = (player['wins'] / player['matches_played'] * 100) if player['matches_played'] > 0 else 0
        
        embed.add_field(
            name=f"{medal} {player['discord_name']}",
            value=(
                f"**Rating:** {rating_str} ({rating_class})\n"
                f"**Record:** {player['wins']}W - {player['losses']}L ({win_rate:.1f}%)\n"
                f"**Matches:** {player['matches_played']}"
            ),
            inline=False
        )
    
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="player_stats", description="View detailed stats for a player")
@app_commands.describe(
    game="The game system",
    player="The player to view (leave empty for yourself)"
)
async def player_stats_command(
    interaction: discord.Interaction,
    game: str,
    player: discord.Member = None
):
    """Display detailed player statistics."""
    target_player = player or interaction.user
    
    # Get game
    game_data = await db.get_game(game)
    if not game_data:
        await interaction.response.send_message(
            f"❌ Game '{game}' not found! Use `/games` to see available games.",
            ephemeral=True
        )
        return
    
    game_id, game_name, display_name = game_data
    
    # Get player data
    player_data = await db.get_player(str(target_player.id), game_id)
    
    if not player_data:
        await interaction.response.send_message(
            f"❌ {target_player.mention} is not registered for {display_name}!",
            ephemeral=True
        )
        return
    
    # Calculate stats
    rating_str = rating_system.format_rating(player_data['rating'], player_data['rating_deviation'])
    rating_class = rating_system.get_rating_class(player_data['rating'])
    win_rate = (player_data['wins'] / player_data['matches_played'] * 100) if player_data['matches_played'] > 0 else 0
    
    # Create stats embed
    embed = discord.Embed(
        title=f"📊 Player Stats - {display_name}",
        description=f"Statistics for {target_player.mention}",
        color=discord.Color.blue()
    )
    
    embed.set_thumbnail(url=target_player.display_avatar.url)
    
    embed.add_field(name="Rating", value=rating_str, inline=True)
    embed.add_field(name="Class", value=rating_class, inline=True)
    embed.add_field(name="Matches", value=player_data['matches_played'], inline=True)
    
    embed.add_field(name="Wins", value=player_data['wins'], inline=True)
    embed.add_field(name="Losses", value=player_data['losses'], inline=True)
    embed.add_field(name="Win Rate", value=f"{win_rate:.1f}%", inline=True)
    
    if player_data['last_match_date']:
        embed.add_field(
            name="Last Match",
            value=f"<t:{int(datetime.fromisoformat(player_data['last_match_date']).timestamp())}:R>",
            inline=False
        )
    
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="add_game", description="Add a new game system (Admin only)")
@app_commands.describe(
    game_name="Short name for the game (e.g., kill_team)",
    display_name="Full display name (e.g., Kill Team)"
)
@app_commands.checks.has_permissions(administrator=True)
async def add_game_command(interaction: discord.Interaction, game_name: str, display_name: str):
    """Add a new game system (admin only)."""
    success = await db.add_game(game_name, display_name)
    
    if success:
        embed = discord.Embed(
            title="✅ Game Added!",
            description=f"**{display_name}** has been added to the system",
            color=discord.Color.green()
        )
        embed.add_field(name="Command Name", value=f"`{game_name}`")
        embed.add_field(name="Display Name", value=display_name)
        embed.set_footer(text="Players can now register using /register " + game_name)
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(
            f"❌ Game '{game_name}' already exists!",
            ephemeral=True
        )


@bot.tree.command(name="match_history", description="View recent match history")
@app_commands.describe(
    game="The game system",
    limit="Number of matches to show (default: 10)"
)
async def match_history_command(interaction: discord.Interaction, game: str, limit: int = 10):
    """Display recent match history."""
    # Validate limit
    if limit < 1 or limit > 50:
        await interaction.response.send_message(
            "❌ Limit must be between 1 and 50!",
            ephemeral=True
        )
        return
    
    # Get game
    game_data = await db.get_game(game)
    if not game_data:
        await interaction.response.send_message(
            f"❌ Game '{game}' not found! Use `/games` to see available games.",
            ephemeral=True
        )
        return
    
    game_id, game_name, display_name = game_data
    
    # Get match history
    matches = await db.get_match_history(game_id, limit)
    
    if not matches:
        await interaction.response.send_message(
            f"No matches recorded for {display_name} yet!",
            ephemeral=True
        )
        return
    
    # Create history embed
    embed = discord.Embed(
        title=f"📜 Match History - {display_name}",
        description=f"Last {len(matches)} matches",
        color=discord.Color.purple()
    )
    
    for match in matches:
        match_date = datetime.fromisoformat(match['match_date'])
        time_str = f"<t:{int(match_date.timestamp())}:R>"
        
        embed.add_field(
            name=f"{match['winner_name']} vs {match['loser_name']}",
            value=(
                f"**Winner:** {match['winner_name']} ({match['winner_change']:+.1f})\n"
                f"**Loser:** {match['loser_name']} ({match['loser_change']:+.1f})\n"
                f"**When:** {time_str}"
            ),
            inline=False
        )
    
    await interaction.response.send_message(embed=embed)


@add_game_command.error
async def add_game_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Handle permission errors for add_game command."""
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message(
            "❌ You need administrator permissions to add games!",
            ephemeral=True
        )


# Run the bot
if __name__ == "__main__":
    if not TOKEN:
        print("Error: DISCORD_TOKEN not found in environment variables!")
        print("Please create a .env file with your Discord bot token.")
        exit(1)
    
    bot.run(TOKEN)
