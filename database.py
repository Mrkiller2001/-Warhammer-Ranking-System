"""
Database management for the ranking system.
Handles SQLite database operations for games, players, matches, and ratings.
"""

import aiosqlite
import os
from datetime import datetime
from typing import List, Optional, Tuple

DATABASE_PATH = os.getenv("DATABASE_PATH", "rankings.db")


class Database:
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path

    async def initialize(self):
        """Create database tables if they don't exist."""
        async with aiosqlite.connect(self.db_path) as db:
            # Games table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS games (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    display_name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Players table (one entry per player per game)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    discord_id TEXT NOT NULL,
                    discord_name TEXT NOT NULL,
                    game_id INTEGER NOT NULL,
                    rating REAL DEFAULT 1500.0,
                    rating_deviation REAL DEFAULT 350.0,
                    volatility REAL DEFAULT 0.06,
                    matches_played INTEGER DEFAULT 0,
                    wins INTEGER DEFAULT 0,
                    losses INTEGER DEFAULT 0,
                    last_match_date TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (game_id) REFERENCES games (id),
                    UNIQUE(discord_id, game_id)
                )
            """)

            # Matches table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS matches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id INTEGER NOT NULL,
                    winner_id INTEGER NOT NULL,
                    loser_id INTEGER NOT NULL,
                    winner_rating_before REAL,
                    winner_rating_after REAL,
                    loser_rating_before REAL,
                    loser_rating_after REAL,
                    match_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    recorded_by TEXT NOT NULL,
                    FOREIGN KEY (game_id) REFERENCES games (id),
                    FOREIGN KEY (winner_id) REFERENCES players (id),
                    FOREIGN KEY (loser_id) REFERENCES players (id)
                )
            """)

            # Create indices for better performance
            await db.execute("CREATE INDEX IF NOT EXISTS idx_players_discord_id ON players(discord_id)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_players_game_id ON players(game_id)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_matches_game_id ON matches(game_id)")

            # Insert default games
            default_games = [
                ("warhammer40k", "Warhammer 40,000"),
                ("aos", "Age of Sigmar"),
                ("mtg", "Magic: The Gathering")
            ]

            for game_name, display_name in default_games:
                await db.execute(
                    "INSERT OR IGNORE INTO games (name, display_name) VALUES (?, ?)",
                    (game_name, display_name)
                )

            await db.commit()

    async def add_game(self, name: str, display_name: str) -> bool:
        """Add a new game system."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "INSERT INTO games (name, display_name) VALUES (?, ?)",
                    (name.lower().replace(" ", "_"), display_name)
                )
                await db.commit()
                return True
        except aiosqlite.IntegrityError:
            return False

    async def get_game(self, name: str) -> Optional[Tuple[int, str, str]]:
        """Get game by name. Returns (id, name, display_name)."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT id, name, display_name FROM games WHERE name = ?",
                (name.lower().replace(" ", "_"),)
            ) as cursor:
                return await cursor.fetchone()

    async def get_all_games(self) -> List[Tuple[str, str]]:
        """Get all available games. Returns list of (name, display_name)."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT name, display_name FROM games ORDER BY name"
            ) as cursor:
                return await cursor.fetchall()

    async def register_player(self, discord_id: str, discord_name: str, game_id: int) -> bool:
        """Register a player for a specific game."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """INSERT INTO players (discord_id, discord_name, game_id)
                       VALUES (?, ?, ?)""",
                    (discord_id, discord_name, game_id)
                )
                await db.commit()
                return True
        except aiosqlite.IntegrityError:
            return False

    async def get_player(self, discord_id: str, game_id: int) -> Optional[dict]:
        """Get player information for a specific game."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                """SELECT id, discord_id, discord_name, rating, rating_deviation,
                          volatility, matches_played, wins, losses, last_match_date
                   FROM players WHERE discord_id = ? AND game_id = ?""",
                (discord_id, game_id)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {
                        "id": row[0],
                        "discord_id": row[1],
                        "discord_name": row[2],
                        "rating": row[3],
                        "rating_deviation": row[4],
                        "volatility": row[5],
                        "matches_played": row[6],
                        "wins": row[7],
                        "losses": row[8],
                        "last_match_date": row[9]
                    }
                return None

    async def update_player_rating(self, player_id: int, rating: float, 
                                   rating_deviation: float, volatility: float,
                                   is_winner: bool):
        """Update player's rating after a match."""
        async with aiosqlite.connect(self.db_path) as db:
            win_loss_update = "wins = wins + 1" if is_winner else "losses = losses + 1"
            await db.execute(
                f"""UPDATE players 
                    SET rating = ?, rating_deviation = ?, volatility = ?,
                        matches_played = matches_played + 1,
                        {win_loss_update},
                        last_match_date = ?
                    WHERE id = ?""",
                (rating, rating_deviation, volatility, datetime.now().isoformat(), player_id)
            )
            await db.commit()

    async def record_match(self, game_id: int, winner_id: int, loser_id: int,
                          winner_rating_before: float, winner_rating_after: float,
                          loser_rating_before: float, loser_rating_after: float,
                          recorded_by: str):
        """Record a match in the database."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT INTO matches 
                   (game_id, winner_id, loser_id, winner_rating_before, winner_rating_after,
                    loser_rating_before, loser_rating_after, recorded_by)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (game_id, winner_id, loser_id, winner_rating_before, winner_rating_after,
                 loser_rating_before, loser_rating_after, recorded_by)
            )
            await db.commit()

    async def get_rankings(self, game_id: int, limit: int = 25) -> List[dict]:
        """Get rankings for a game, sorted by rating."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                """SELECT discord_name, rating, rating_deviation, matches_played, wins, losses
                   FROM players
                   WHERE game_id = ?
                   ORDER BY rating DESC, rating_deviation ASC
                   LIMIT ?""",
                (game_id, limit)
            ) as cursor:
                rows = await cursor.fetchall()
                return [
                    {
                        "discord_name": row[0],
                        "rating": row[1],
                        "rating_deviation": row[2],
                        "matches_played": row[3],
                        "wins": row[4],
                        "losses": row[5]
                    }
                    for row in rows
                ]

    async def get_match_history(self, game_id: int, limit: int = 10) -> List[dict]:
        """Get recent match history for a game."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                """SELECT m.match_date, 
                          w.discord_name as winner_name, 
                          l.discord_name as loser_name,
                          m.winner_rating_after - m.winner_rating_before as winner_change,
                          m.loser_rating_after - m.loser_rating_before as loser_change
                   FROM matches m
                   JOIN players w ON m.winner_id = w.id
                   JOIN players l ON m.loser_id = l.id
                   WHERE m.game_id = ?
                   ORDER BY m.match_date DESC
                   LIMIT ?""",
                (game_id, limit)
            ) as cursor:
                rows = await cursor.fetchall()
                return [
                    {
                        "match_date": row[0],
                        "winner_name": row[1],
                        "loser_name": row[2],
                        "winner_change": row[3],
                        "loser_change": row[4]
                    }
                    for row in rows
                ]
