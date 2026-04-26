import pygame
import sys
from pygame.locals import *
import random

# ── Init ──────────────────────────────────────────────────────────────────────
clock = pygame.time.Clock()
pygame.init()

WIDTH  = 500
HEIGHT = 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer")

# Load and scale background and game-over images
bg           = pygame.image.load("images/way.png")
bg           = pygame.transform.scale(bg, (WIDTH, HEIGHT))
game_over_img = pygame.image.load("images/game_over.jpeg")
game_over_img = pygame.transform.scale(game_over_img, (WIDTH, HEIGHT))

font      = pygame.font.Font(None, 41)
font_small = pygame.font.Font(None, 28)

# ── Coin weight table ─────────────────────────────────────────────────────────
# Each entry: (point_value, probability_weight, display_label, tint_color)
# Higher probability_weight = appears more often (weighted random choice).
COIN_TYPES = [
    {"value": 1, "weight": 60, "label": "+1", "color": (255, 215,   0)},  # gold   – common
    {"value": 3, "weight": 30, "label": "+3", "color": (192, 192, 192)},  # silver – uncommon
    {"value": 5, "weight": 10, "label": "+5", "color": (255, 100, 100)},  # red    – rare
]

# How many coins must be collected to trigger the next enemy speed increase
SPEED_UP_EVERY = 5   # every N coins → enemies get faster


# ── Enemy Car ─────────────────────────────────────────────────────────────────
class EnemyCar(pygame.sprite.Sprite):
    def __init__(self, speed_boost=0):
        super().__init__()
        # Load and scale the enemy sprite
        self.image = pygame.image.load("images/enemy_car.png")
        self.image = pygame.transform.scale(self.image, (80, 170))
        self.rect  = self.image.get_rect()
        # Smaller hitbox so a collision only fires when cars truly overlap
        self.hitbox = pygame.Rect(0, 0, 48, 110)
        # Store the current global speed boost (increases with each level)
        self.speed_boost = speed_boost
        self.reset()

    def reset(self):
        """Place the enemy at a random x position above the screen."""
        self.rect.center = (random.randint(60, WIDTH - 60), -50)
        self.speed       = random.randint(6, 8) + self.speed_boost
        self.hitbox.center = self.rect.center

    def apply_boost(self, boost):
        """Update the stored boost and immediately raise the current speed."""
        self.speed_boost = boost
        self.speed       = random.randint(6, 8) + self.speed_boost

    def move_ecar(self):
        """Move the enemy downward and reset once it leaves the screen."""
        self.rect.y += self.speed
        # Keep the hitbox centred on the sprite every frame
        self.hitbox.center = self.rect.center
        if self.rect.y > HEIGHT:
            self.reset()

    def draw_ecar(self):
        screen.blit(self.image, self.rect)


# ── Coin ──────────────────────────────────────────────────────────────────────
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Load the base coin image
        self.base_image = pygame.image.load("images/coin.png")
        self.base_image = pygame.transform.scale(self.base_image, (50, 50))
        self.rect        = self.base_image.get_rect()
        self.speed       = 4
        # Pick a random coin type according to the probability weights
        self._pick_type()
        self.random_place()

    def _pick_type(self):
        """Weighted random selection of coin type."""
        population = COIN_TYPES
        weights    = [ct["weight"] for ct in population]
        # random.choices returns a list; take the first element
        self.coin_type = random.choices(population, weights=weights, k=1)[0]
        # Tint a copy of the base image to reflect the coin's rarity
        self.image = self.base_image.copy()
        tint_surf  = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
        r, g, b    = self.coin_type["color"]
        tint_surf.fill((r, g, b, 100))          # semi-transparent colour overlay
        self.image.blit(tint_surf, (0, 0))

    def random_place(self):
        """Place coin at a random position above the visible screen, then re-pick type."""
        self._pick_type()
        self.rect.center = (
            random.randint(30, WIDTH - 30),
            random.randint(-300, -50),
        )

    def move_coin(self):
        """Move coin downward; reset when it passes the bottom of the screen."""
        self.rect.y += self.speed
        if self.rect.y > HEIGHT:
            self.random_place()

    def draw_coin(self):
        screen.blit(self.image, self.rect)
        # Draw the point value label above the coin sprite
        label = font_small.render(self.coin_type["label"], True, self.coin_type["color"])
        screen.blit(label, (self.rect.x + 10, self.rect.y - 20))


# ── Player Car ────────────────────────────────────────────────────────────────
class Car(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("images/car.png")
        self.image = pygame.transform.scale(self.image, (120, 150))
        self.rect  = self.image.get_rect()
        self.rect.center = (WIDTH // 2, 620)
        # Reduced hitbox for a fairer feel
        self.hitbox = pygame.Rect(0, 0, 70, 110)
        self.hitbox.center = self.rect.center

    def move_car(self, keys):
        """Move left/right with arrow keys, clamped to screen edges."""
        if keys[K_LEFT]  and self.rect.left  > 10:          self.rect.x -= 10
        if keys[K_RIGHT] and self.rect.right < WIDTH - 10:  self.rect.x += 10
        self.hitbox.center = self.rect.center

    def draw(self):
        screen.blit(self.image, self.rect)


# ── Helpers ───────────────────────────────────────────────────────────────────

# Score at which the second enemy car joins the road
SECOND_ENEMY_AT = 10

# Minimum vertical distance (px) between two enemy cars to avoid stacking
MIN_ENEMY_GAP = 300


def spawn_spaced_enemy(existing_enemies, boost=0):
    """
    Create a new EnemyCar that is at least MIN_ENEMY_GAP pixels away (vertically)
    from every already-active enemy.  Tries up to 20 random placements.
    """
    for _ in range(20):
        candidate = EnemyCar(speed_boost=boost)
        too_close = any(
            abs(candidate.rect.y - e.rect.y) < MIN_ENEMY_GAP
            for e in existing_enemies
        )
        if not too_close:
            return candidate
    return EnemyCar(speed_boost=boost)   # fallback (very unlikely)


def reset_game():
    """Create fresh game objects and return the initial state."""
    player  = Car()
    enemies = [EnemyCar()]              # start with ONE enemy car
    coins   = [Coin(), Coin(), Coin()]  # three weighted coins
    score   = 0
    level   = 1
    boost   = 0   # speed bonus added to enemies each level-up
    return player, enemies, coins, score, level, boost


def show_game_over(score, level):
    """Display the game-over screen and wait for SPACE or ESC."""
    screen.blit(game_over_img, (0, 0))
    final = font.render(f"Score: {score}  Lvl: {level}", True, (255, 255, 255))
    hint  = font_small.render("SPACE – play again   ESC – quit", True, (255, 255, 255))
    screen.blit(final, (WIDTH // 2 - 80, HEIGHT // 2 + 60))
    screen.blit(hint,  (WIDTH // 2 - 140, HEIGHT // 2 + 110))
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  return          # restart
                if event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()


# ── Main game loop ────────────────────────────────────────────────────────────
player, enemies, coins, score, level, boost = reset_game()

running = True
while running:
    screen.blit(bg, (0, 0))   # draw the road background first

    # ── Events ────────────────────────────────────────────────────────────────
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit(); sys.exit()

    # ── Move & draw enemies ────────────────────────────────────────────────────
    for enemy in enemies:
        enemy.move_ecar()
        enemy.draw_ecar()

    # ── Move & draw coins ──────────────────────────────────────────────────────
    for coin in coins:
        coin.move_coin()
        coin.draw_coin()

    # ── Coin collection check ──────────────────────────────────────────────────
    for coin in coins:
        if player.hitbox.colliderect(coin.rect):
            # Add this coin's point value (1 / 3 / 5 depending on rarity)
            score += coin.coin_type["value"]
            coin.random_place()   # respawn the coin with a new random type

    # ── Add 2nd enemy once score reaches SECOND_ENEMY_AT ─────────────────────
    if score >= SECOND_ENEMY_AT and len(enemies) < 2:
        enemies.append(spawn_spaced_enemy(enemies, boost))

    # ── Level-up: increase enemy speed every SPEED_UP_EVERY coins ─────────────
    new_level = score // SPEED_UP_EVERY + 1
    if new_level > level:
        level  = new_level
        boost += 1                       # one extra speed point per level
        for enemy in enemies:
            enemy.apply_boost(boost)     # apply the boost immediately

    # ── Collision with enemy ───────────────────────────────────────────────────
    for enemy in enemies:
        if player.hitbox.colliderect(enemy.hitbox):
            show_game_over(score, level)
            # Reset everything for a fresh game
            player, enemies, coins, score, level, boost = reset_game()
            break

    # ── Player movement ────────────────────────────────────────────────────────
    keys = pygame.key.get_pressed()
    player.move_car(keys)
    player.draw()

    # ── HUD: score & level ─────────────────────────────────────────────────────
    hud = font.render(f"Score: {score}  Lvl: {level}", True, (128, 52, 36))
    screen.blit(hud, hud.get_rect(topright=(WIDTH - 10, 10)))

    # ── Coin legend (top-left) ─────────────────────────────────────────────────
    for i, ct in enumerate(COIN_TYPES):
        legend = font_small.render(
            f"{ct['label']}  weight:{ct['weight']}%", True, ct["color"]
        )
        screen.blit(legend, (10, 10 + i * 22))

    pygame.display.update()
    clock.tick(60)