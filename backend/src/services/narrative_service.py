"""
Narrative generation service for creating unique campaign stories and planets.
Uses procedural generation to ensure no two campaigns are the same.
"""

import random
from typing import List, Dict, Tuple
from datetime import datetime


class NarrativeService:
    """Service for generating campaign narratives and planet systems."""
    
    # Planet name components for procedural generation
    PLANET_PREFIXES = [
        "Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Sigma", "Omega",
        "Nova", "Vox", "Hex", "Mortis", "Ultima", "Sanctus", "Bellum", "Fortis",
        "Tertius", "Quintus", "Septimus", "Magnus", "Minor", "Primus", "Secundus"
    ]
    
    PLANET_SUFFIXES = [
        "Prime", "Secundus", "Tertius", "Major", "Minor", "Extremis",
        "Maximus", "Inferior", "Superior", "Eternal", "Obscurus"
    ]
    
    PLANET_NAMES = [
        "Armageddon", "Cadia", "Vigilus", "Baal", "Ultramar", "Fenris", "Caliban",
        "Medusa", "Nocturne", "Deliverance", "Macragge", "Chogoris", "Prospero",
        "Barbarus", "Chemos", "Olympia", "Colchis", "Nuceria", "Isstvan", "Molech",
        "Tallarn", "Vraks", "Badab", "Betalis", "Kronus", "Cyprus", "Kaurava",
        "Aurelia", "Tartarus", "Graia", "Meridian", "Acheron", "Typhon", "Hadex",
        "Sanctum", "Infernus", "Gloriana", "Valedor", "Damocles", "Agripinaa"
    ]
    
    # Planet types with characteristics
    PLANET_TYPES = {
        "forge": {
            "colors": ["#8B4513", "#CD853F", "#A0522D"],
            "descriptions": [
                "A forge world of endless factories and manufactorums",
                "Ancient machinery rumbles beneath rust-red skies",
                "Massive industrial complexes stretch across the surface"
            ],
            "strategic_value": "Industrial production and war materiel"
        },
        "death": {
            "colors": ["#2F4F4F", "#696969", "#778899"],
            "descriptions": [
                "A barren wasteland of ash and bone",
                "Death hangs heavy in the toxic atmosphere",
                "Ruins of ancient civilizations dot the lifeless surface"
            ],
            "strategic_value": "Strategic location and hidden relics"
        },
        "shrine": {
            "colors": ["#FFD700", "#F0E68C", "#DAA520"],
            "descriptions": [
                "Sacred temples rise toward golden skies",
                "Holy sites attract pilgrims from across the sector",
                "Ancient shrines hold powerful artifacts"
            ],
            "strategic_value": "Religious significance and morale boost"
        },
        "hive": {
            "colors": ["#696969", "#708090", "#2F4F4F"],
            "descriptions": [
                "Towering hive cities pierce polluted skies",
                "Billions toil in the underhives below",
                "A world of endless urban sprawl"
            ],
            "strategic_value": "Population and recruitment center"
        },
        "agri": {
            "colors": ["#228B22", "#32CD32", "#90EE90"],
            "descriptions": [
                "Endless fields stretch to the horizon",
                "Agricultural production feeds entire sectors",
                "Pastoral beauty masks strategic importance"
            ],
            "strategic_value": "Food production and supply lines"
        },
        "fortress": {
            "colors": ["#4B0082", "#483D8B", "#6A5ACD"],
            "descriptions": [
                "Impregnable fortifications cover the surface",
                "A keystone of imperial defense",
                "Massive void shields protect strategic assets"
            ],
            "strategic_value": "Military strongpoint and staging area"
        },
        "ice": {
            "colors": ["#B0E0E6", "#ADD8E6", "#87CEEB"],
            "descriptions": [
                "Frozen wastes conceal ancient secrets",
                "Ice storms rage across the tundra",
                "Cold beauty hides deadly dangers"
            ],
            "strategic_value": "Rare minerals and research facilities"
        },
        "jungle": {
            "colors": ["#006400", "#228B22", "#2E8B57"],
            "descriptions": [
                "Dense jungle conceals deadly fauna",
                "Ancient ruins hide beneath the canopy",
                "A green hell of endless conflict"
            ],
            "strategic_value": "Natural resources and hidden bases"
        }
    }
    
    # Narrative templates for different events
    OPENING_NARRATIVES = [
        "The {sector} Sector burns with the fires of war...",
        "Ancient prophecies foretell doom for the {sector} Sector...",
        "A great crusade begins in the {sector} Sector...",
        "Darkness descends upon the {sector} Sector...",
        "The Emperor's light reaches the {sector} Sector..."
    ]
    
    CONFLICT_REASONS = [
        "an ancient artifact of immense power",
        "strategic control of the sector",
        "a prophesied event that will reshape the galaxy",
        "resources vital to the war effort",
        "the liberation of loyal imperial citizens",
        "the destruction of a great evil",
        "revenge for past betrayals",
        "the fulfillment of an ancient oath"
    ]
    
    FACTIONS = [
        "Space Marines", "Chaos Forces", "Ork Waaagh!", "Tyranid Hive Fleet",
        "Necron Dynasty", "T'au Empire", "Aeldari Craftworld", "Dark Eldar Kabal",
        "Imperial Guard", "Adeptus Mechanicus", "Genestealer Cult", "Death Guard"
    ]
    
    def __init__(self):
        """Initialize narrative service."""
        pass
    
    def generate_solar_system(self, campaign_name: str, campaign_id: int) -> Tuple[List[Dict], str, int]:
        """
        Generate a unique solar system with planets and initial narrative.
        
        Args:
            campaign_name: Name of the campaign
            campaign_id: ID of the campaign
            
        Returns:
            Tuple of (planets list, initial narrative, seed)
        """
        # Create deterministic seed from campaign name and timestamp
        seed = hash(f"{campaign_name}_{campaign_id}_{datetime.now().isoformat()}")
        rng = random.Random(seed)
        
        # Generate 3-8 planets
        num_planets = rng.randint(3, 8)
        planets = []
        used_names = set()
        
        for position in range(1, num_planets + 1):
            planet = self._generate_planet(rng, position, used_names)
            planets.append(planet)
            used_names.add(planet['name'])
        
        # Generate initial narrative
        sector_name = self._generate_sector_name(rng)
        narrative = self._generate_opening_narrative(rng, sector_name, planets)
        
        return planets, narrative, seed
    
    def _generate_planet(self, rng: random.Random, position: int, used_names: set) -> Dict:
        """Generate a single planet with unique characteristics."""
        # Generate unique planet name
        name = self._generate_unique_planet_name(rng, used_names)
        
        # Select planet type
        planet_type = rng.choice(list(self.PLANET_TYPES.keys()))
        type_data = self.PLANET_TYPES[planet_type]
        
        # Generate characteristics
        color = rng.choice(type_data['colors'])
        description = rng.choice(type_data['descriptions'])
        size = rng.uniform(0.6, 1.8)  # Relative size
        
        return {
            'name': name,
            'planet_type': planet_type,
            'position': position,
            'color': color,
            'size': round(size, 2),
            'description': description,
            'strategic_value': type_data['strategic_value']
        }
    
    def _generate_unique_planet_name(self, rng: random.Random, used_names: set) -> str:
        """Generate a unique planet name."""
        max_attempts = 100
        for _ in range(max_attempts):
            # 50% chance of using a base name, 50% chance of generating composite
            if rng.random() < 0.5 and len(self.PLANET_NAMES) > 0:
                name = rng.choice(self.PLANET_NAMES)
                # Add suffix if name already used
                if name in used_names:
                    suffix = rng.choice(self.PLANET_SUFFIXES)
                    name = f"{name} {suffix}"
            else:
                prefix = rng.choice(self.PLANET_PREFIXES)
                suffix = rng.choice(self.PLANET_SUFFIXES)
                roman = rng.choice(['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X'])
                
                # Generate different name patterns
                pattern = rng.randint(1, 4)
                if pattern == 1:
                    name = f"{prefix} {suffix}"
                elif pattern == 2:
                    name = f"{prefix}-{roman}"
                elif pattern == 3:
                    base = rng.choice(self.PLANET_NAMES)
                    name = f"{base} {suffix}"
                else:
                    name = f"{prefix} {roman}"
            
            if name not in used_names:
                return name
        
        # Fallback: add random number
        return f"{rng.choice(self.PLANET_PREFIXES)}-{rng.randint(100, 999)}"
    
    def _generate_sector_name(self, rng: random.Random) -> str:
        """Generate a sector name."""
        prefixes = ["Sanctus", "Ultima", "Obscurus", "Tempestus", "Pacificus", "Solar"]
        sectors = [
            "Segmentum", "Sector", "Sub-sector", "System", "Reach", 
            "Expanse", "Marches", "Void", "Cluster", "Domain"
        ]
        
        # 70% chance of complex name
        if rng.random() < 0.7:
            prefix = rng.choice(prefixes)
            sector = rng.choice(sectors)
            return f"{prefix} {sector}"
        else:
            name = rng.choice(self.PLANET_PREFIXES + list(self.PLANET_NAMES[:10]))
            sector = rng.choice(sectors)
            return f"{name} {sector}"
    
    def _generate_opening_narrative(self, rng: random.Random, sector_name: str, planets: List[Dict]) -> str:
        """Generate the opening narrative for a campaign."""
        opening = rng.choice(self.OPENING_NARRATIVES).format(sector=sector_name)
        reason = rng.choice(self.CONFLICT_REASONS)
        
        # Mention a key planet
        key_planet = rng.choice(planets)
        
        narrative = f"""{opening}

Forces across the sector mobilize for control of {reason}. The fate of worlds hangs in the balance.

{key_planet['name']}, a {key_planet['planet_type']} world of strategic importance, stands at the center of the coming storm. {key_planet['description']}

The campaign begins. Let the galaxy burn."""
        
        return narrative
    
    def generate_battle_narrative(self, 
                                   planet_name: str, 
                                   planet_type: str,
                                   winner_name: str, 
                                   loser_name: str,
                                   score_diff: int) -> str:
        """
        Generate narrative text for a battle result.
        
        Args:
            planet_name: Name of the planet where battle occurred
            planet_type: Type of planet
            winner_name: Name of the winner
            loser_name: Name of the loser
            score_diff: Score difference (margin of victory)
            
        Returns:
            Narrative text describing the battle
        """
        if score_diff <= 5:
            intensity = "hard-fought"
            outcome = "narrowly claimed victory"
        elif score_diff <= 15:
            intensity = "fierce"
            outcome = "secured a decisive victory"
        else:
            intensity = "devastating"
            outcome = "crushed all opposition"
        
        narratives = [
            f"In a {intensity} battle on {planet_name}, {winner_name} {outcome} against {loser_name}. The {planet_type} world trembles with the echoes of war.",
            f"The skies of {planet_name} burned as {winner_name} {outcome} over {loser_name}. Control of this vital {planet_type} world shifts.",
            f"Victory on {planet_name}! {winner_name} {outcome} in {intensity} combat against {loser_name}. The campaign narrative evolves.",
            f"Blood was spilled on {planet_name} as {winner_name} {outcome}. {loser_name}'s forces retreat from the {planet_type} world."
        ]
        
        return random.choice(narratives)
    
    def generate_planet_conquest_event(self, planet_name: str, controller: str, games_played: int) -> str:
        """Generate narrative for planet conquest milestone."""
        if games_played == 3:
            return f"{controller} establishes a foothold on {planet_name}. The planet's fate hangs in the balance."
        elif games_played == 5:
            return f"{controller}'s control of {planet_name} solidifies. Enemy forces struggle to maintain their positions."
        elif games_played >= 8:
            return f"{planet_name} falls to {controller}! The planet is fully conquered, its resources now fuel the war machine."
        return f"The battle for {planet_name} intensifies. {controller} leads the fight for control."
