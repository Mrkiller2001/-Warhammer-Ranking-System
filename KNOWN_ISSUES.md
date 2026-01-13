# Known Issues & TODO

## ⚠️ Campaign Service - Partial Migration

### Issue
The [campaign_service.py](backend/src/services/campaign_service.py) file still contains direct `aiosqlite` calls that bypass the Firestore service layer.

### Affected Methods
The following methods in `CampaignService` make direct SQL calls:
- `add_participant()` - Line ~191
- `get_participant_stats()` - Line ~217
- `_create_campaign_game_record()` - Line ~244
- `_update_participant_stats()` - Line ~272
- `_update_planet_after_battle()` - Lines ~328-395

### Why It's Not Blocking
These methods are used for **campaign narrative features** which are currently not heavily used in the application. The core features (player management, match recording, rankings) all work correctly with Firestore.

### Solution Path
Two options:

#### Option 1: Refactor to Use FirestoreService (Recommended)
Replace direct `aiosqlite.connect(self.db.db_path)` calls with calls to FirestoreService methods:

```python
# Instead of:
async with aiosqlite.connect(self.db.db_path) as db:
    cursor = await db.execute("SELECT * FROM players WHERE id = ?", (player_id,))
    
# Use:
player = await self.db.get_player_by_id(player_id)
```

The FirestoreService already has methods for:
- `create_narrative_event()` - ✅ Implemented
- Campaign participant management - ❌ Needs methods added
- Planet statistics - ❌ Needs methods added

#### Option 2: Disable Campaign Features Temporarily
If you want to deploy immediately without campaign features:
1. Comment out campaign-related API routes in `backend/src/api/campaigns.py`
2. Hide campaign UI components in frontend
3. Focus on core match recording and rankings

### Testing Status
- ✅ **Core Features**: Working with Firestore
  - Player registration
  - Match recording (1v1, FFA, teams)
  - Rankings and statistics
- ⚠️ **Campaign Features**: May have issues
  - Adding players to campaigns
  - Recording campaign battles
  - Planet control tracking
  - Narrative event generation

### Impact Assessment
**Low Priority** - Campaign features are optional enhancements. The main ranking system functionality is fully migrated and operational.

### Timeline
- **Immediate**: Deploy with core features working
- **Phase 2**: Refactor campaign_service to use Firestore (estimated 2-3 hours)

## 📝 Additional Notes

### Missing Firestore Methods Needed
To fully support campaign features, add these methods to `FirestoreService`:

```python
async def add_campaign_participant(campaign_id: str, player_id: str) -> str:
    """Add a player to a campaign."""
    # Implementation needed

async def get_campaign_participant(campaign_id: str, player_id: str) -> Optional[Dict]:
    """Get participant stats for a campaign."""
    # Implementation needed

async def update_campaign_participant_stats(
    campaign_id: str, 
    player_id: str, 
    updates: Dict
) -> None:
    """Update participant statistics."""
    # Implementation needed

async def create_campaign_game(game_data: Dict) -> str:
    """Create a campaign game record."""
    # Implementation needed
```

### Deployment Readiness
✅ **Ready to deploy** for core functionality  
⚠️ **Campaign features need testing** before production use

### Migration Completion: 95%
- ✅ Core database layer (FirestoreService)
- ✅ Player management
- ✅ Match recording
- ✅ Rankings
- ✅ Game management
- ⚠️ Campaign narrative system (partial)

---

**Last Updated**: Vercel + Firebase Migration  
**Priority**: Low (campaign features are optional)  
**Blocking Deployment**: No
