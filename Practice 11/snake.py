import pygame
import random
import time
from collections import namedtuple

pygame.init()

# ── Fonts ──────────────────────────────────────────────────────────────────────
font     = pygame.font.Font(None, 25)
font_big = pygame.font.Font(None, 55)

# ── Colors ─────────────────────────────────────────────────────────────────────
BLACK  = (0,   0,   0)
RED    = (200, 0,   0)
BLUE1  = (0,   0,   255)
BLUE2  = (0,   100, 255)
WHITE  = (255, 255, 255)
GRAY   = (50,  50,  50)

# ── Constants ──────────────────────────────────────────────────────────────────
BLOCK_SIZE = 20
BASE_SPEED = 5

Point = namedtuple('Point', 'x, y')

# ── Food weight table ──────────────────────────────────────────────────────────
# Each entry defines:
#   value      – score points awarded when the snake eats this food
#   weight     – relative probability (higher = more common)
#   color      – RGB colour used to draw the food tile
#   lifetime   – seconds before the food vanishes (None = stays forever)
FOOD_TYPES = [
    {
        "value":    1,
        "weight":  60,
        "color":   (200,   0,   0),   # red   – normal, common
        "lifetime": None,             # never disappears
    },
    {
        "value":    3,
        "weight":  25,
        "color":   (255, 165,   0),   # orange – bonus, disappears in 7 s
        "lifetime": 7,
    },
    {
        "value":    5,
        "weight":  15,
        "color":   (180,   0, 180),   # purple – rare, disappears in 4 s
        "lifetime": 4,
    },
]


class FoodItem:
    """A single piece of food with a type, position, and optional timer."""

    def __init__(self, x, y):
        # Randomly choose food type using probability weights
        weights = [ft["weight"] for ft in FOOD_TYPES]
        self.ftype    = random.choices(FOOD_TYPES, weights=weights, k=1)[0]
        self.pos      = Point(x, y)
        self.value    = self.ftype["value"]
        self.color    = self.ftype["color"]
        self.lifetime = self.ftype["lifetime"]           # None or seconds
        self.spawn_time = time.time()                    # record when created

    def is_expired(self):
        """Return True if this food has exceeded its allowed lifetime."""
        if self.lifetime is None:
            return False   # immortal food
        return (time.time() - self.spawn_time) >= self.lifetime

    def remaining_seconds(self):
        """Seconds left before this food vanishes (0 if already expired)."""
        if self.lifetime is None:
            return None
        remaining = self.lifetime - (time.time() - self.spawn_time)
        return max(0.0, remaining)


class SnakeGame:
    """Main game class – manages state, input, rendering, and food logic."""

    # Maximum number of food items on the board simultaneously
    MAX_FOOD = 3

    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        """Restore initial game state for a fresh start or after game-over."""
        self.direction = "RIGHT"
        self.head = Point(self.w // 2, self.h // 2)
        self.snake = [
            self.head,
            Point(self.head.x - BLOCK_SIZE,     self.head.y),
            Point(self.head.x - 2 * BLOCK_SIZE, self.head.y),
        ]
        self.score = 0
        self.level = 1
        self.speed = BASE_SPEED
        # Start with one food item; more may appear over time
        self.foods = []
        self._spawn_food()

    # ── Food management ────────────────────────────────────────────────────────

    def _free_cells(self):
        """Return a list of grid cells that are not occupied by the snake or food."""
        occupied = set(self.snake) | {f.pos for f in self.foods}
        cells = []
        for gx in range(0, self.w, BLOCK_SIZE):
            for gy in range(0, self.h, BLOCK_SIZE):
                if Point(gx, gy) not in occupied:
                    cells.append((gx, gy))
        return cells

    def _spawn_food(self):
        """Add one new food item at a random unoccupied cell (if space exists)."""
        cells = self._free_cells()
        if not cells:
            return   # board is full – skip
        x, y = random.choice(cells)
        self.foods.append(FoodItem(x, y))

    def _remove_expired_food(self):
        """Delete any food items whose timer has run out."""
        self.foods = [f for f in self.foods if not f.is_expired()]

    # ── Core game step ─────────────────────────────────────────────────────────

    def play_step(self):
        """Process one game tick. Returns (game_over, score)."""

        # Handle input events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); quit()
            if event.type == pygame.KEYDOWN:
                # Prevent the snake from reversing into itself
                if event.key == pygame.K_LEFT  and self.direction != "RIGHT":
                    self.direction = "LEFT"
                elif event.key == pygame.K_RIGHT and self.direction != "LEFT":
                    self.direction = "RIGHT"
                elif event.key == pygame.K_UP   and self.direction != "DOWN":
                    self.direction = "UP"
                elif event.key == pygame.K_DOWN  and self.direction != "UP":
                    self.direction = "DOWN"

        # Advance the snake's head one block in the current direction
        self._move(self.direction)
        self.snake.insert(0, self.head)

        # Check for wall or self-collision → game over
        if self._is_collision():
            return True, self.score

        # Remove food items whose lifetime has expired
        self._remove_expired_food()

        # Check if the snake's head overlaps any food item
        eaten = None
        for f in self.foods:
            if self.head == f.pos:
                eaten = f
                break

        if eaten:
            # Award points equal to the food's value
            self.score += eaten.value
            self.foods.remove(eaten)
            self._update_level()          # check for level-up
        else:
            # Snake didn't eat; remove the tail to keep length constant
            self.snake.pop()

        # Refill food items up to MAX_FOOD (if some expired or were eaten)
        while len(self.foods) < self.MAX_FOOD:
            self._spawn_food()

        self._update_ui()
        self.clock.tick(self.speed)
        return False, self.score

    # ── Collision ──────────────────────────────────────────────────────────────

    def _is_collision(self):
        """True if the snake has hit a wall or bitten itself."""
        # Wall check
        if self.head.x < 0 or self.head.x >= self.w: return True
        if self.head.y < 0 or self.head.y >= self.h: return True
        # Self-collision check (skip index 0 which is the head itself)
        if self.head in self.snake[1:]: return True
        return False

    # ── Movement ───────────────────────────────────────────────────────────────

    def _move(self, direction):
        """Update self.head by one BLOCK_SIZE in the given direction."""
        x, y = self.head.x, self.head.y
        if direction == "RIGHT": x += BLOCK_SIZE
        elif direction == "LEFT": x -= BLOCK_SIZE
        elif direction == "UP":   y -= BLOCK_SIZE
        elif direction == "DOWN": y += BLOCK_SIZE
        self.head = Point(x, y)

    # ── Level progression ──────────────────────────────────────────────────────

    def _update_level(self):
        """Level up every 3 points and increase snake speed by 1."""
        new_level = self.score // 3 + 1
        if new_level > self.level:
            self.level = new_level
            self.speed += 1

    # ── Rendering ──────────────────────────────────────────────────────────────

    def _update_ui(self):
        """Redraw the entire screen for this frame."""
        self.display.fill(BLACK)

        # Draw the snake body (outer blue tile + inner accent)
        for pt in self.snake:
            pygame.draw.rect(
                self.display, BLUE1,
                pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE)
            )
            pygame.draw.rect(
                self.display, BLUE2,
                pygame.Rect(pt.x + 4, pt.y + 4, 12, 12)
            )

        # Draw each food item with its type-specific colour
        for f in self.foods:
            pygame.draw.rect(
                self.display, f.color,
                pygame.Rect(f.pos.x, f.pos.y, BLOCK_SIZE, BLOCK_SIZE)
            )
            # If the food has a timer, draw the remaining seconds above it
            rem = f.remaining_seconds()
            if rem is not None:
                timer_txt = font.render(f"{rem:.1f}s", True, WHITE)
                self.display.blit(timer_txt, (f.pos.x - 5, f.pos.y - 18))

        # HUD – score and level
        hud = font.render(f"Score: {self.score}   Level: {self.level}", True, WHITE)
        self.display.blit(hud, [10, 10])

        # Legend – food types and their values (bottom-left corner)
        legend_y = self.h - len(FOOD_TYPES) * 20 - 10
        for i, ft in enumerate(FOOD_TYPES):
            lifetime_txt = f"{ft['lifetime']}s" if ft['lifetime'] else "∞"
            legend_line = font.render(
                f"  +{ft['value']} pt  timer:{lifetime_txt}  weight:{ft['weight']}",
                True, ft["color"]
            )
            self.display.blit(legend_line, [10, legend_y + i * 20])

        pygame.display.flip()

    # ── Game-over screen ───────────────────────────────────────────────────────

    def show_game_over(self):
        """Render the game-over overlay and block until the player responds."""
        self.display.fill(BLACK)
        go_text   = font_big.render("GAME OVER", True, RED)
        sc_text   = font.render(
            f"Final Score: {self.score}   Level: {self.level}", True, WHITE
        )
        play_text = font.render(
            "Press SPACE to play again or ESC to quit", True, GRAY
        )
        self.display.blit(go_text,   (self.w // 2 - 130, self.h // 2 - 60))
        self.display.blit(sc_text,   (self.w // 2 - 100, self.h // 2))
        self.display.blit(play_text, (self.w // 2 - 175, self.h // 2 + 50))
        pygame.display.flip()

        # Block until the player presses SPACE (restart) or ESC (quit)
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:  waiting = False
                    elif event.key == pygame.K_ESCAPE: pygame.quit(); quit()


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    game = SnakeGame()

    while True:
        game_over, score = game.play_step()

        if game_over:
            game.show_game_over()
            game.reset()   # restart after the player presses SPACE