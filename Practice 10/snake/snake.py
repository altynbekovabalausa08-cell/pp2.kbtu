import pygame
import random
from collections import namedtuple

pygame.init()

font = pygame.font.Font(None, 25)
font_big = pygame.font.Font(None, 55)

BLACK  = (0, 0, 0)
RED    = (200, 0, 0)
BLUE1  = (0, 0, 255)
BLUE2  = (0, 100, 255)
WHITE  = (255, 255, 255)
GRAY   = (50, 50, 50)

BLOCK_SIZE = 20
SPEED = 5

Point = namedtuple('Point', 'x, y')


class SnakeGame:
    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        # Start state: snake moves right, placed in the center
        self.direction = "RIGHT"
        self.head = Point(self.w // 2, self.h // 2)
        self.snake = [
            self.head,
            Point(self.head.x - BLOCK_SIZE, self.head.y),
            Point(self.head.x - 2 * BLOCK_SIZE, self.head.y),
        ]
        self.score = 0
        self.level = 1
        self.speed = SPEED
        self.food = None
        self._place_food()

    def _place_food(self):
        # Place food at a random position that is not on the snake
        while True:
            x = random.randint(0, (self.w // BLOCK_SIZE) - 1) * BLOCK_SIZE
            y = random.randint(0, (self.h // BLOCK_SIZE) - 1) * BLOCK_SIZE
            self.food = Point(x, y)
            if self.food not in self.snake:
                break

    def play_step(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                # Change direction, but do not allow going back the opposite way
                if event.key == pygame.K_LEFT and self.direction != "RIGHT":
                    self.direction = "LEFT"
                elif event.key == pygame.K_RIGHT and self.direction != "LEFT":
                    self.direction = "RIGHT"
                elif event.key == pygame.K_UP and self.direction != "DOWN":
                    self.direction = "UP"
                elif event.key == pygame.K_DOWN and self.direction != "UP":
                    self.direction = "DOWN"

        self._move(self.direction)
        self.snake.insert(0, self.head)

        # Check for collision with wall or itself
        if self._is_collision():
            return True, self.score

        if self.head == self.food:
            self.score += 1
            self._place_food()
            self._update_level()  # Check if we move to next level
        else:
            # Remove the tail so the snake does not grow
            self.snake.pop()

        self._update_ui()
        self.clock.tick(self.speed)
        return False, self.score

    def _is_collision(self):
        # Check wall collision (snake goes outside the screen)
        if self.head.x < 0 or self.head.x >= self.w:
            return True
        if self.head.y < 0 or self.head.y >= self.h:
            return True
        # Check self collision (snake head hits its own body)
        if self.head in self.snake[1:]:
            return True
        return False

    def _move(self, direction):
        x = self.head.x
        y = self.head.y
        if direction == "RIGHT":
            x += BLOCK_SIZE
        elif direction == "LEFT":
            x -= BLOCK_SIZE
        elif direction == "UP":
            y -= BLOCK_SIZE
        elif direction == "DOWN":
            y += BLOCK_SIZE
        self.head = Point(x, y)

    def _update_level(self):
        # Every 3 foods = level up and speed increases
        if self.score % 3 == 0:
            self.level += 1
            self.speed += 1

    def _update_ui(self):
        self.display.fill(BLACK)

        # Draw the snake body
        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x + 4, pt.y + 4, 12, 12))

        # Draw the food
        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

        # Show score and level at the top
        text = font.render(f"Score: {self.score}   Level: {self.level}", True, WHITE)
        self.display.blit(text, [10, 10])
        pygame.display.flip()

    def show_game_over(self):
        # Show game over screen inside the pygame window
        self.display.fill(BLACK)
        go_text   = font_big.render("GAME OVER", True, RED)
        sc_text   = font.render(f"Final Score: {self.score}   Level: {self.level}", True, WHITE)
        play_text = font.render("Press SPACE to play again or ESC to quit", True, GRAY)
        self.display.blit(go_text,   (self.w // 2 - 130, self.h // 2 - 60))
        self.display.blit(sc_text,   (self.w // 2 - 100, self.h // 2))
        self.display.blit(play_text, (self.w // 2 - 175, self.h // 2 + 50))
        pygame.display.flip()

        # Wait for player input on the game over screen
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        waiting = False   # Restart the game
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        quit()


if __name__ == '__main__':
    game = SnakeGame()

    while True:
        game_over, score = game.play_step()

        if game_over:
            game.show_game_over()
            game.reset()  # Restart the game after player presses SPACE
