"""
Migration script to transfer data from SQLite/PostgreSQL to Firebase Firestore.
Run this script after setting up Firebase to migrate existing data.
"""

import asyncio
import sys
from typing import Dict, Any
from src.services.database_service import DatabaseService
from src.services.firestore_service import FirestoreService
from src.config import settings


class DataMigration:
    """Handle migration from SQL database to Firestore."""
    
    def __init__(self):
        self.sql_db = DatabaseService()
        self.firestore_db = FirestoreService()
        self.id_mappings = {
            'games': {},
            'players': {},
            'campaigns': {},
            'planets': {}
        }
    
    async def migrate_all(self):
        """Run complete migration."""
        print("🚀 Starting data migration from SQL to Firestore...")
        print("=" * 60)
        
        try:
            # Initialize databases
            await self.sql_db.initialize()
            await self.firestore_db.initialize()
            
            # Migrate in order (respecting dependencies)
            await self.migrate_games()
            await self.migrate_players()
            await self.migrate_matches()
            await self.migrate_campaigns()
            
            print("\n" + "=" * 60)
            print("✅ Migration completed successfully!")
            print("\nID Mappings Summary:")
            for entity, mappings in self.id_mappings.items():
                print(f"  - {entity}: {len(mappings)} records")
            
        except Exception as e:
            print(f"\n❌ Migration failed: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    async def migrate_games(self):
        """Migrate games."""
        print("\n📦 Migrating games...")
        games = await self.sql_db.get_all_games()
        
        for game in games:
            try:
                new_game = await self.firestore_db.create_game(
                    name=game['name'],
                    display_name=game['display_name']
                )
                # Store mapping of old ID to new ID
                self.id_mappings['games'][game['id']] = new_game['id']
                print(f"  ✓ Migrated game: {game['display_name']}")
            except Exception as e:
                print(f"  ✗ Failed to migrate game {game['name']}: {e}")
        
        print(f"  → Migrated {len(games)} games")
    
    async def migrate_players(self):
        """Migrate players."""
        print("\n👥 Migrating players...")
        
        for old_game_id, new_game_id in self.id_mappings['games'].items():
            players = await self.sql_db.get_players_by_game(old_game_id)
            
            for player in players:
                try:
                    new_player = await self.firestore_db.create_player(
                        discord_id=player['discord_id'],
                        discord_name=player['discord_name'],
                        game_id=new_game_id,
                        rating=player['rating'],
                        rating_deviation=player['rating_deviation'],
                        volatility=player['volatility']
                    )
                    
                    # Update stats separately
                    await self.firestore_db.update_player_stats(
                        player_id=new_player['id'],
                        matches_played=player['matches_played'],
                        wins=player['wins'],
                        losses=player['losses'],
                        last_match_date=player.get('last_match_date')
                    )
                    
                    self.id_mappings['players'][player['id']] = new_player['id']
                    print(f"  ✓ Migrated player: {player['discord_name']}")
                except Exception as e:
                    print(f"  ✗ Failed to migrate player {player['discord_name']}: {e}")
        
        print(f"  → Migrated {len(self.id_mappings['players'])} players")
    
    async def migrate_matches(self):
        """Migrate matches."""
        print("\n⚔️  Migrating matches...")
        
        total_matches = 0
        for old_game_id, new_game_id in self.id_mappings['games'].items():
            matches = await self.sql_db.get_matches_by_game(old_game_id, limit=1000)
            
            for match in matches:
                try:
                    # Map old player IDs to new ones
                    old_winner_id = match['winner_id']
                    old_loser_id = match['loser_id']
                    
                    if old_winner_id not in self.id_mappings['players']:
                        print(f"  ⚠ Skipping match: winner ID {old_winner_id} not found")
                        continue
                    
                    if old_loser_id not in self.id_mappings['players']:
                        print(f"  ⚠ Skipping match: loser ID {old_loser_id} not found")
                        continue
                    
                    new_winner_id = self.id_mappings['players'][old_winner_id]
                    new_loser_id = self.id_mappings['players'][old_loser_id]
                    
                    await self.firestore_db.create_match(
                        game_id=new_game_id,
                        winner_id=new_winner_id,
                        loser_id=new_loser_id,
                        winner_score=match.get('winner_score'),
                        loser_score=match.get('loser_score'),
                        winner_rating_before=match['winner_rating_before'],
                        loser_rating_before=match['loser_rating_before'],
                        winner_rating_after=match['winner_rating_after'],
                        loser_rating_after=match['loser_rating_after'],
                        notes=match.get('notes')
                    )
                    total_matches += 1
                except Exception as e:
                    print(f"  ✗ Failed to migrate match: {e}")
        
        print(f"  → Migrated {total_matches} matches")
    
    async def migrate_campaigns(self):
        """Migrate campaigns and related data."""
        print("\n🌍 Migrating campaigns...")
        
        for old_game_id, new_game_id in self.id_mappings['games'].items():
            campaigns = await self.sql_db.get_campaigns_by_game(old_game_id)
            
            for campaign in campaigns:
                try:
                    # Create campaign
                    new_campaign = await self.firestore_db.create_campaign(
                        name=campaign['name'],
                        description=campaign.get('description', ''),
                        game_id=new_game_id,
                        narrative_seed=campaign['narrative_seed']
                    )
                    old_campaign_id = campaign['id']
                    new_campaign_id = new_campaign['id']
                    self.id_mappings['campaigns'][old_campaign_id] = new_campaign_id
                    
                    # Update campaign status
                    if not campaign['is_active']:
                        await self.firestore_db.end_campaign(new_campaign_id)
                    
                    print(f"  ✓ Migrated campaign: {campaign['name']}")
                    
                    # Migrate campaign participants
                    await self.migrate_campaign_participants(old_campaign_id, new_campaign_id)
                    
                    # Migrate planets
                    await self.migrate_planets(old_campaign_id, new_campaign_id)
                    
                    # Migrate campaign games
                    await self.migrate_campaign_games(old_campaign_id, new_campaign_id)
                    
                    # Migrate narrative events
                    await self.migrate_narrative_events(old_campaign_id, new_campaign_id)
                    
                except Exception as e:
                    print(f"  ✗ Failed to migrate campaign {campaign['name']}: {e}")
        
        print(f"  → Migrated {len(self.id_mappings['campaigns'])} campaigns")
    
    async def migrate_campaign_participants(self, old_campaign_id: int, new_campaign_id: str):
        """Migrate campaign participants."""
        participants = await self.sql_db.get_campaign_participants(old_campaign_id)
        
        for participant in participants:
            old_player_id = participant['player_id']
            if old_player_id in self.id_mappings['players']:
                new_player_id = self.id_mappings['players'][old_player_id]
                await self.firestore_db.create_campaign_participant(
                    campaign_id=new_campaign_id,
                    player_id=new_player_id,
                    requisition_points=participant['requisition_points'],
                    supply_limit=participant['supply_limit']
                )
    
    async def migrate_planets(self, old_campaign_id: int, new_campaign_id: str):
        """Migrate planets."""
        planets = await self.sql_db.get_campaign_planets(old_campaign_id)
        
        for planet in planets:
            try:
                new_planet = await self.firestore_db.create_planet(
                    campaign_id=new_campaign_id,
                    name=planet['name'],
                    planet_type=planet['planet_type'],
                    description=planet['description'],
                    position=planet['position'],
                    size=planet['size'],
                    color=planet['color'],
                    strategic_value=planet['strategic_value']
                )
                
                # Update planet status if needed
                if planet.get('current_controller') or planet.get('is_contested'):
                    updates = {}
                    if planet.get('current_controller'):
                        # Map controller ID
                        old_controller = planet['current_controller']
                        if old_controller in self.id_mappings['players']:
                            updates['current_controller'] = self.id_mappings['players'][old_controller]
                    if planet.get('is_contested'):
                        updates['is_contested'] = planet['is_contested']
                    if planet.get('games_played'):
                        updates['games_played'] = planet['games_played']
                    
                    if updates:
                        await self.firestore_db.update_planet(
                            campaign_id=new_campaign_id,
                            planet_id=new_planet['id'],
                            updates=updates
                        )
                
                self.id_mappings['planets'][planet['id']] = new_planet['id']
            except Exception as e:
                print(f"    ✗ Failed to migrate planet {planet['name']}: {e}")
    
    async def migrate_campaign_games(self, old_campaign_id: int, new_campaign_id: str):
        """Migrate campaign games."""
        games = await self.sql_db.get_campaign_games(old_campaign_id, limit=1000)
        
        for game in games:
            try:
                # Map IDs
                old_planet_id = game['planet_id']
                old_attacker_id = game['attacker_id']
                old_defender_id = game['defender_id']
                old_winner_id = game.get('winner_id')
                
                if (old_planet_id not in self.id_mappings['planets'] or
                    old_attacker_id not in self.id_mappings['players'] or
                    old_defender_id not in self.id_mappings['players']):
                    continue
                
                new_planet_id = self.id_mappings['planets'][old_planet_id]
                new_attacker_id = self.id_mappings['players'][old_attacker_id]
                new_defender_id = self.id_mappings['players'][old_defender_id]
                new_winner_id = self.id_mappings['players'].get(old_winner_id) if old_winner_id else None
                
                await self.firestore_db.create_campaign_game(
                    campaign_id=new_campaign_id,
                    planet_id=new_planet_id,
                    attacker_id=new_attacker_id,
                    defender_id=new_defender_id,
                    attacker_score=game['attacker_score'],
                    defender_score=game['defender_score'],
                    attacker_req=game['attacker_req'],
                    defender_req=game['defender_req'],
                    winner_id=new_winner_id,
                    mission_type=game.get('mission_type', 'standard'),
                    notes=game.get('notes')
                )
            except Exception as e:
                print(f"    ✗ Failed to migrate campaign game: {e}")
    
    async def migrate_narrative_events(self, old_campaign_id: int, new_campaign_id: str):
        """Migrate narrative events."""
        events = await self.sql_db.get_campaign_events(old_campaign_id, limit=500)
        
        for event in events:
            try:
                # Map IDs if present
                planet_id = None
                player_id = None
                
                if event.get('planet_id') and event['planet_id'] in self.id_mappings['planets']:
                    planet_id = self.id_mappings['planets'][event['planet_id']]
                
                if event.get('player_id') and event['player_id'] in self.id_mappings['players']:
                    player_id = self.id_mappings['players'][event['player_id']]
                
                await self.firestore_db.create_narrative_event(
                    campaign_id=new_campaign_id,
                    event_type=event['event_type'],
                    title=event['title'],
                    description=event['description'],
                    planet_id=planet_id,
                    player_id=player_id
                )
            except Exception as e:
                print(f"    ✗ Failed to migrate narrative event: {e}")


async def main():
    """Run migration."""
    print("\n⚠️  WARNING: This will migrate data from SQL to Firestore.")
    print("Make sure you have:")
    print("  1. Backed up your SQL database")
    print("  2. Set up Firebase and configured credentials")
    print("  3. Updated .env with Firebase settings")
    print("")
    
    response = input("Continue with migration? (yes/no): ")
    if response.lower() != 'yes':
        print("Migration cancelled.")
        return
    
    migration = DataMigration()
    await migration.migrate_all()


if __name__ == "__main__":
    asyncio.run(main())
