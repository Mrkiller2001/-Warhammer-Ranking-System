"""
Database service layer with proper OOP design.
Handles all database operations with async support.
"""

import aiosqlite
from typing import List, Optional, Dict, Any
from datetime import datetime
from src.config import settings


class DatabaseService:
    """Database service for all data operations."""
    
    def __init__(self, db_path: str = None):
        """
        Initialize database service.
        
        Args:
            db_path: Path to SQLite database file
        """
        if db_path is None:
            # Extract path from DATABASE_URL (remove sqlite+aiosqlite:///)
            db_path = settings.database_url.replace("sqlite+aiosqlite:///", "")
        self.db_path = db_path
    
    async def initialize(self) -> None:
        """Create database tables if they don't exist."""
        async with aiosqlite.connect(self.db_path) as db:
            await self._create_games_table(db)
            await self._create_players_table(db)
            await self._create_matches_table(db)
            await self._create_campaigns_table(db)
            await self._create_campaign_games_table(db)
            await self._create_campaign_participants_table(db)
            await db.commit()
    
    async def _create_games_table(self, db: aiosqlite.Connection) -> None:
        """Create games table."""
        await db.execute("""
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                display_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    async def _create_players_table(self, db: aiosqlite.Connection) -> None:
        """Create players table."""
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
    
    async def _create_matches_table(self, db: aiosqlite.Connection) -> None:
        """Create matches table."""
        await db.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id INTEGER NOT NULL,
                winner_id INTEGER NOT NULL,
                loser_id INTEGER NOT NULL,
                winner_score INTEGER,
                loser_score INTEGER,
                winner_rating_before REAL NOT NULL,
                loser_rating_before REAL NOT NULL,
                winner_rating_after REAL NOT NULL,
                loser_rating_after REAL NOT NULL,
                notes TEXT,
                played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (game_id) REFERENCES games (id),
                FOREIGN KEY (winner_id) REFERENCES players (id),
                FOREIGN KEY (loser_id) REFERENCES players (id)
            )
        """)
    
    async def _create_campaigns_table(self, db: aiosqlite.Connection) -> None:
        """Create campaigns table."""
        await db.execute("""
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                game_id INTEGER NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP,
                FOREIGN KEY (game_id) REFERENCES games (id)
            )
        """)
    
    async def _create_campaign_games_table(self, db: aiosqlite.Connection) -> None:
        """Create campaign games table."""
        await db.execute("""
            CREATE TABLE IF NOT EXISTS campaign_games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id INTEGER NOT NULL,
                attacker_id INTEGER NOT NULL,
                defender_id INTEGER NOT NULL,
                attacker_score INTEGER NOT NULL,
                defender_score INTEGER NOT NULL,
                attacker_req INTEGER NOT NULL,
                defender_req INTEGER NOT NULL,
                winner_id INTEGER,
                mission_type TEXT DEFAULT 'standard',
                notes TEXT,
                played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (campaign_id) REFERENCES campaigns (id),
                FOREIGN KEY (attacker_id) REFERENCES players (id),
                FOREIGN KEY (defender_id) REFERENCES players (id),
                FOREIGN KEY (winner_id) REFERENCES players (id)
            )
        """)
    
    async def _create_campaign_participants_table(self, db: aiosqlite.Connection) -> None:
        """Create campaign participants table."""
        await db.execute("""
            CREATE TABLE IF NOT EXISTS campaign_participants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id INTEGER NOT NULL,
                player_id INTEGER NOT NULL,
                requisition_points INTEGER DEFAULT 0,
                supply_limit INTEGER DEFAULT 50,
                battles_won INTEGER DEFAULT 0,
                battles_lost INTEGER DEFAULT 0,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (campaign_id) REFERENCES campaigns (id),
                FOREIGN KEY (player_id) REFERENCES players (id),
                UNIQUE(campaign_id, player_id)
            )
        """)
    
    # Game Operations
    async def create_game(self, name: str, display_name: str) -> int:
        """Create a new game."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "INSERT INTO games (name, display_name) VALUES (?, ?)",
                (name, display_name)
            )
            await db.commit()
            return cursor.lastrowid
    
    async def get_game_by_id(self, game_id: int) -> Optional[Dict[str, Any]]:
        """Get game by ID."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM games WHERE id = ?",
                (game_id,)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def get_game_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get game by name."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM games WHERE name = ?",
                (name,)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def get_all_games(self) -> List[Dict[str, Any]]:
        """Get all games."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM games ORDER BY display_name")
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    # Player Operations
    async def create_player(
        self,
        discord_id: str,
        discord_name: str,
        game_id: int
    ) -> int:
        """Create a new player."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO players (discord_id, discord_name, game_id)
                VALUES (?, ?, ?)
                """,
                (discord_id, discord_name, game_id)
            )
            await db.commit()
            return cursor.lastrowid
    
    async def get_player_by_id(self, player_id: int) -> Optional[Dict[str, Any]]:
        """Get player by ID."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM players WHERE id = ?",
                (player_id,)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def get_player_by_discord_id(
        self,
        discord_id: str,
        game_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get player by Discord ID and game."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM players WHERE discord_id = ? AND game_id = ?",
                (discord_id, game_id)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def get_players_by_game(self, game_id: int) -> List[Dict[str, Any]]:
        """Get all players for a game."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM players WHERE game_id = ? ORDER BY rating DESC",
                (game_id,)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def update_player_rating(
        self,
        player_id: int,
        rating: float,
        rating_deviation: float,
        volatility: float
    ) -> None:
        """Update player rating."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                UPDATE players
                SET rating = ?, rating_deviation = ?, volatility = ?,
                    last_match_date = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (rating, rating_deviation, volatility, player_id)
            )
            await db.commit()
    
    async def update_player_stats(
        self,
        player_id: int,
        won: bool
    ) -> None:
        """Update player statistics after a match."""
        async with aiosqlite.connect(self.db_path) as db:
            if won:
                await db.execute(
                    """
                    UPDATE players
                    SET matches_played = matches_played + 1,
                        wins = wins + 1
                    WHERE id = ?
                    """,
                    (player_id,)
                )
            else:
                await db.execute(
                    """
                    UPDATE players
                    SET matches_played = matches_played + 1,
                        losses = losses + 1
                    WHERE id = ?
                    """,
                    (player_id,)
                )
            await db.commit()
    
    # Match Operations
    async def create_match(
        self,
        game_id: int,
        winner_id: int,
        loser_id: int,
        winner_rating_before: float,
        loser_rating_before: float,
        winner_rating_after: float,
        loser_rating_after: float,
        winner_score: Optional[int] = None,
        loser_score: Optional[int] = None,
        notes: Optional[str] = None
    ) -> int:
        """Create a new match record."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO matches (
                    game_id, winner_id, loser_id,
                    winner_score, loser_score,
                    winner_rating_before, loser_rating_before,
                    winner_rating_after, loser_rating_after,
                    notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    game_id, winner_id, loser_id,
                    winner_score, loser_score,
                    winner_rating_before, loser_rating_before,
                    winner_rating_after, loser_rating_after,
                    notes
                )
            )
            await db.commit()
            return cursor.lastrowid
    
    async def get_matches_by_game(
        self,
        game_id: int,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get recent matches for a game."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT * FROM matches
                WHERE game_id = ?
                ORDER BY played_at DESC
                LIMIT ?
                """,
                (game_id, limit)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    # Campaign Operations
    async def create_campaign(
        self,
        name: str,
        game_id: int,
        description: Optional[str] = None
    ) -> int:
        """Create a new campaign."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO campaigns (name, description, game_id)
                VALUES (?, ?, ?)
                """,
                (name, description, game_id)
            )
            await db.commit()
            return cursor.lastrowid
    
    async def get_campaign_by_id(self, campaign_id: int) -> Optional[Dict[str, Any]]:
        """Get campaign by ID."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM campaigns WHERE id = ?",
                (campaign_id,)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def get_active_campaigns(self) -> List[Dict[str, Any]]:
        """Get all active campaigns."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM campaigns WHERE is_active = 1 ORDER BY created_at DESC"
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def update_campaign(
        self,
        campaign_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> None:
        """Update campaign information."""
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        if is_active is not None:
            updates.append("is_active = ?")
            params.append(1 if is_active else 0)
            if not is_active:
                updates.append("ended_at = CURRENT_TIMESTAMP")
        
        if not updates:
            return
        
        params.append(campaign_id)
        query = f"UPDATE campaigns SET {', '.join(updates)} WHERE id = ?"
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(query, params)
            await db.commit()
