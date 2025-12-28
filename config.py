"""
Configuration settings for the ranking bot.
"""

# Glicko-2 System Settings
DEFAULT_RATING = 1500.0
DEFAULT_RATING_DEVIATION = 350.0
DEFAULT_VOLATILITY = 0.06
SYSTEM_TAU = 0.5  # Constrains volatility changes (0.3-1.2 typical)

# Rating Classes
RATING_CLASSES = {
    2400: "Legendary",
    2200: "Master",
    2000: "Expert",
    1800: "Advanced",
    1600: "Intermediate",
    1400: "Novice",
    0: "Beginner"
}

# Discord Settings
MAX_RANKINGS_DISPLAY = 25
MAX_HISTORY_DISPLAY = 10

# Database Settings
DATABASE_VERSION = 1
