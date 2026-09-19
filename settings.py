"""
settings.py - Global constants, color palettes, and configurations.
"""

# Screen Configuration
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "ARCHERY - Precision Challenge"

# Dark Minimalist Color Palette
COLOR_BG = (12, 15, 20)             # Deep dark void background
COLOR_BG_DARK = (7, 9, 13)          # Darker overlay / borders
COLOR_ARENA_LINE = (28, 35, 51)     # Subtle grid / boundary lines
COLOR_CARD_BG = (18, 22, 32, 220)   # Semi-transparent dark card background

# Neon & Accent Colors
COLOR_CYAN = (56, 189, 248)         # Cyan neon accent / bow
COLOR_CYAN_GLOW = (56, 189, 248, 60)# Cyan glow
COLOR_GOLD = (251, 191, 36)         # Gold / Bullseye
COLOR_GREEN = (34, 197, 94)         # Green / Hit
COLOR_RED = (244, 63, 94)           # Coral red / Miss / Alert
COLOR_PURPLE = (168, 85, 247)       # Purple accent

# UI & Text Colors
COLOR_TEXT_WHITE = (248, 250, 252)  # Crisp white text
COLOR_TEXT_MUTED = (148, 163, 184)  # Muted secondary text
COLOR_TEXT_DARK = (71, 85, 105)     # Dark subtle details

# Bow & Arrow Settings
BOW_POS_X = 140
BOW_POS_Y = 360
BOW_RADIUS = 42
BOW_MIN_ANGLE = -75  # degrees
BOW_MAX_ANGLE = 75   # degrees
ARROW_SPEED = 24.0   # Fast and responsive
ARROW_GRAVITY = 0.08 # Subtle natural arc drop
ARROW_LENGTH = 52
TRAJECTORY_POINTS = 16
TRAJECTORY_STEP = 2.2

# Target Settings
TARGET_DEFAULT_X = 1100
TARGET_RADIUS_OUTER = 56
TARGET_RADIUS_MID = 40
TARGET_RADIUS_INNER = 25
TARGET_RADIUS_BULLSEYE = 12

# Score Values
SCORE_BULLSEYE = 100
SCORE_INNER = 50
SCORE_MID = 25
SCORE_OUTER = 10

# Ring Colors (Modern Minimalist concentric rings)
COLOR_RING_OUTER = (30, 41, 59)     # Deep slate
COLOR_RING_MID = (2, 132, 199)      # Neon blue
COLOR_RING_INNER = (245, 158, 11)   # Amber / Orange
COLOR_RING_BULLSEYE = (239, 68, 68) # Red bullseye center

# Game Rules
TOTAL_ROUNDS = 5
ARROWS_PER_ROUND = 5
MAX_LIVES = 3
COMBO_MULTIPLIER_BONUS = 5 # Extra points per combo streak
