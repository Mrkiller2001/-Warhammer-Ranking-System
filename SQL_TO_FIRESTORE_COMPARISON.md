# Code Migration: SQL to Firestore

This document shows the key differences between the old SQL-based approach and the new Firestore approach.

## Database Service Comparison

### Creating a Player

#### Old (SQL - database_service.py)
```python
async def create_player(
    self,
    discord_id: str,
    discord_name: str,
    game_id: int,  # Integer ID
    rating: float = 1500.0,
    rating_deviation: float = 350.0,
    volatility: float = 0.06
) -> Dict[str, Any]:
    async with aiosqlite.connect(self.db_path) as db:
        cursor = await db.execute("""
            INSERT INTO players (discord_id, discord_name, game_id, rating, rating_deviation, volatility)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (discord_id, discord_name, game_id, rating, rating_deviation, volatility))
        
        await db.commit()
        player_id = cursor.lastrowid
        return await self.get_player(player_id)
```

#### New (Firestore - firestore_service.py)
```python
async def create_player(
    self,
    discord_id: str,
    discord_name: str,
    game_id: str,  # String document ID
    rating: float = 1500.0,
    rating_deviation: float = 350.0,
    volatility: float = 0.06
) -> Dict[str, Any]:
    player_ref = self.db.collection('players').document()
    player_data = {
        'discord_id': discord_id,
        'discord_name': discord_name,
        'game_id': game_id,
        'rating': rating,
        'rating_deviation': rating_deviation,
        'volatility': volatility,
        'matches_played': 0,
        'wins': 0,
        'losses': 0,
        'last_match_date': None,
        'created_at': firestore.SERVER_TIMESTAMP
    }
    player_ref.set(player_data)
    
    player_doc = player_ref.get()
    return {'id': player_doc.id, **player_doc.to_dict()}
```

### Querying Players by Game

#### Old (SQL)
```python
async def get_players_by_game(self, game_id: int) -> List[Dict[str, Any]]:
    async with aiosqlite.connect(self.db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT * FROM players 
            WHERE game_id = ? 
            ORDER BY rating DESC
        """, (game_id,))
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
```

#### New (Firestore)
```python
async def get_players_by_game(self, game_id: str) -> List[Dict[str, Any]]:
    players_ref = self.db.collection('players')
    query = players_ref.where(filter=FieldFilter('game_id', '==', game_id))\
                      .order_by('rating', direction=firestore.Query.DESCENDING)
    
    players = []
    for doc in query.stream():
        players.append({'id': doc.id, **doc.to_dict()})
    
    return players
```

---

## Data Structure Changes

### SQL Schema (Before)

```sql
-- Flat relational structure
games (id, name, display_name, created_at)
players (id, discord_id, game_id, rating, ...)
matches (id, game_id, winner_id, loser_id, ...)
campaigns (id, name, game_id, ...)
planets (id, campaign_id, name, ...)
campaign_games (id, campaign_id, planet_id, ...)
```

### Firestore Structure (After)

```
games/                          # Collection
  {gameId}/                     # Document
    name: string
    display_name: string
    created_at: timestamp

players/                        # Collection
  {playerId}/                   # Document
    game_id: string (reference)
    discord_id: string
    rating: number
    ...

campaigns/                      # Collection
  {campaignId}/                 # Document
    name: string
    game_id: string
    is_active: boolean
    
    planets/                    # Subcollection
      {planetId}/               # Document
        name: string
        position: number
        ...
    
    games/                      # Subcollection
      {gameId}/                 # Document
        planet_id: string
        attacker_id: string
        ...
```

---

## Key Differences

### 1. ID Types

**SQL**: Integer auto-increment
```python
player_id: int = 123
```

**Firestore**: String document IDs
```python
player_id: str = "abc123xyz789"
```

### 2. Relationships

**SQL**: Foreign keys
```sql
FOREIGN KEY (game_id) REFERENCES games(id)
```

**Firestore**: Document references (stored as strings)
```python
player_data = {
    'game_id': 'game_doc_id_string',  # Reference by ID
    ...
}
```

### 3. Nested Data

**SQL**: Separate joined tables
```sql
SELECT * FROM campaigns c
JOIN planets p ON p.campaign_id = c.id
```

**Firestore**: Subcollections
```python
planets = campaign_doc.collection('planets').stream()
```

### 4. Timestamps

**SQL**: `CURRENT_TIMESTAMP` or Python datetime
```sql
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

**Firestore**: Server-side timestamp
```python
'created_at': firestore.SERVER_TIMESTAMP
```

### 5. Querying

**SQL**: SQL statements
```python
cursor = await db.execute("""
    SELECT * FROM players WHERE game_id = ? AND rating > ?
""", (game_id, 1500))
```

**Firestore**: Query API
```python
query = players_ref\
    .where(filter=FieldFilter('game_id', '==', game_id))\
    .where(filter=FieldFilter('rating', '>', 1500))
```

---

## API Endpoints - No Changes Needed!

The beauty of this migration is that **your API endpoints remain the same**. The Pydantic models handle the conversion between integer and string IDs automatically.

### Example: Create Player Endpoint

```python
# This endpoint works with BOTH database backends!
@router.post("/", response_model=PlayerResponse)
async def create_player(player: PlayerCreate):
    # The service layer handles the database specifics
    result = await db_service.create_player(
        discord_id=player.discord_id,
        discord_name=player.discord_name,
        game_id=player.game_id
    )
    return result
```

---

## Migration Considerations

### Data Type Changes

| SQL Type | Firestore Type | Notes |
|----------|----------------|-------|
| `INTEGER` | Not used for IDs | Firestore uses string document IDs |
| `TEXT` | `string` | Direct mapping |
| `REAL` | `number` | Direct mapping |
| `BOOLEAN` | `boolean` | Direct mapping |
| `TIMESTAMP` | `timestamp` | Use `firestore.SERVER_TIMESTAMP` |
| Foreign Key (INT) | String reference | Store document ID as string |

### ID Mapping During Migration

When migrating, you need to map old integer IDs to new string IDs:

```python
# Migration mapping
id_mappings = {
    'games': {
        1: 'abc123',  # Old SQL ID → New Firestore ID
        2: 'def456',
    },
    'players': {
        10: 'xyz789',
        11: 'uvw012',
    }
}
```

---

## Performance Considerations

### SQL Advantages
- ✅ Complex JOIN operations
- ✅ ACID transactions across tables
- ✅ Mature querying capabilities
- ✅ Predictable costs

### Firestore Advantages
- ✅ Automatic scaling
- ✅ Real-time listeners
- ✅ Offline support
- ✅ Global distribution
- ✅ No server management

### Firestore Limitations
- ⚠️ Limited JOIN-like operations
- ⚠️ Queries require indexes for complex filters
- ⚠️ Costs based on reads/writes (not storage)
- ⚠️ Maximum 1 write/second per document

---

## Indexing

### SQL
```sql
CREATE INDEX idx_players_game_rating 
ON players(game_id, rating DESC);
```

### Firestore (firestore.indexes.json)
```json
{
  "indexes": [{
    "collectionGroup": "players",
    "queryScope": "COLLECTION",
    "fields": [
      {"fieldPath": "game_id", "order": "ASCENDING"},
      {"fieldPath": "rating", "order": "DESCENDING"}
    ]
  }]
}
```

---

## Transactions

### SQL
```python
async with db.begin():
    # Multiple operations
    await db.execute("UPDATE players SET rating = ? WHERE id = ?", ...)
    await db.execute("INSERT INTO matches ...", ...)
    # Auto-commit or rollback
```

### Firestore
```python
from google.cloud.firestore import Transaction

@firestore.transactional
def update_in_transaction(transaction: Transaction):
    # Read phase
    player_ref = db.collection('players').document(player_id)
    player = player_ref.get(transaction=transaction)
    
    # Write phase
    transaction.update(player_ref, {'rating': new_rating})
    transaction.set(match_ref, match_data)
```

---

## Configuration Changes

### Old (.env with SQL)
```env
DATABASE_URL=postgresql://user:pass@host/db
# or
DATABASE_URL=sqlite+aiosqlite:///./rankings.db
```

### New (.env with Firestore)
```env
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
# DATABASE_URL no longer needed
```

### Old (requirements.txt)
```txt
aiosqlite>=0.19.0
sqlalchemy>=2.0.23
psycopg2-binary>=2.9.9
asyncpg>=0.29.0
```

### New (requirements.txt)
```txt
firebase-admin>=6.4.0
# SQLAlchemy dependencies removed
```

---

## Testing Differences

### SQL Testing
```python
@pytest.fixture
async def db():
    # Create test database
    db = DatabaseService(":memory:")
    await db.initialize()
    yield db
```

### Firestore Testing
```python
@pytest.fixture
def db():
    # Use Firestore emulator
    os.environ['FIRESTORE_EMULATOR_HOST'] = 'localhost:8080'
    db = FirestoreService()
    yield db
```

---

## Summary of Changes

### ✅ What Changed
- Database backend (SQL → Firestore)
- ID types (int → string)
- Query syntax (SQL → Firestore Query API)
- Relationship handling (Foreign keys → Document references)
- Configuration (DATABASE_URL → Firebase credentials)

### ✅ What Stayed the Same
- API endpoints
- Pydantic models
- Business logic
- Frontend code
- Discord bot integration

### ⚡ New Capabilities
- Real-time data sync
- Offline support
- Automatic scaling
- Global distribution
- Subcollections for better data organization

---

## When to Use Each

### Use SQL When:
- Complex JOIN operations are frequent
- Need strict ACID guarantees
- Predictable costs important
- Self-hosted infrastructure

### Use Firestore When:
- Need automatic scaling
- Want real-time updates
- Prefer managed service
- Building mobile/web apps
- Global user base

---

For your Warhammer Ranking System, Firestore is ideal because:
1. ✅ Community-sized data (fits free tier)
2. ✅ Real-time leaderboards possible
3. ✅ Easy deployment with Vercel
4. ✅ Automatic scaling for events
5. ✅ No database server management
