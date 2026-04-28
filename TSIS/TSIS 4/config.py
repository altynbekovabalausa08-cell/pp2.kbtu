# Screen and grid settings
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
CELL_SIZE = 20
COLS = SCREEN_WIDTH // CELL_SIZE   # 30 columns
ROWS = SCREEN_HEIGHT // CELL_SIZE  # 30 rows

# Game speed (frames per second)
BASE_FPS = 8
SPEED_PER_LEVEL = 2   # FPS added each level
FOOD_PER_LEVEL = 5    # eat this many foods to level up

# Colors
WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
GREEN  = (0,   200, 0)
RED    = (220, 0,   0)
DARK_RED = (120, 0, 0)    # poison food
YELLOW = (255, 220, 0)    # speed boost
BLUE   = (0,   120, 255)  # slow motion
PURPLE = (180, 0,   255)  # shield
GRAY   = (120, 120, 120)  # obstacles
DARK_GRAY = (40, 40, 40)
ORANGE = (255, 140, 0)

# Food point values
FOOD_WEIGHTS = [
    (1, RED,    0.6),   # normal: 60% chance, 1 point
    (3, ORANGE, 0.3),   # bonus:  30% chance, 3 points
    (5, YELLOW, 0.1),   # rare:   10% chance, 5 points
]

FOOD_LIFETIME = 7000   # ms before food disappears
POWERUP_LIFETIME = 8000  # ms before power-up disappears
POWERUP_EFFECT = 5000    # ms the effect lasts after collecting