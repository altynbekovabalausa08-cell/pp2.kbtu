import pygame
import sys
from pygame.locals import *
import random

clock = pygame.time.Clock()
pygame.init()

width = 500
height = 700
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Racer")

bg = pygame.image.load("images/way.png")
bg = pygame.transform.scale(bg, (width, height))

# Score and level variables
score = 0
level = 1
enemy_speed_boost = 0  # Speed increases as level goes up

font = pygame.font.Font(None, 41)


class EnemyCar(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("images/enemy_car.png")
        self.image = pygame.transform.scale(self.image, (80, 170))
        self.rect = self.image.get_rect()
        self.reset()

    def reset(self):
        # Place enemy at a random x position above the screen
        self.rect.center = (random.randint(50, width - 50), -50)
        self.speed = random.randint(6, 8) + enemy_speed_boost

    def move_ecar(self):
        self.rect.y += self.speed
        # When enemy goes off screen, send it back to the top
        if self.rect.y > height:
            self.reset()

    def draw_ecar(self):
        screen.blit(self.image, self.rect)


class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("images/coin.png")
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.speed = 4
        self.random_place()

    def random_place(self):
        # Place coin at a random position above the screen
        self.rect.center = (random.randint(30, width - 30), random.randint(-300, -50))

    def move_coin(self):
        self.rect.y += self.speed
        if self.rect.y > height:
            self.random_place()

    def draw_coin(self):
        screen.blit(self.image, self.rect)


class Car(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("images/car.png")
        self.image = pygame.transform.scale(self.image, (120, 150))
        self.rect = self.image.get_rect()
        self.rect.center = (width // 2, 620)

    def move_car(self, keys):
        if keys[K_LEFT] and self.rect.left > 10:
            self.rect.x -= 10
        if keys[K_RIGHT] and self.rect.right < width - 10:
            self.rect.x += 10

    def draw(self):
        screen.blit(self.image, self.rect)


# Create player car, 3 enemy cars, and 3 coins
player_car = Car()
enemies = [EnemyCar(), EnemyCar(), EnemyCar()]
coins = [Coin(), Coin(), Coin()]

flag = True
while flag:
    screen.blit(bg, (0, 0))

    for i in pygame.event.get():
        if i.type == pygame.QUIT:
            flag = False
            pygame.quit()
            sys.exit()

    # Move and draw all enemies
    for enemy in enemies:
        enemy.move_ecar()
        enemy.draw_ecar()

    # Move and draw all coins
    for coin in coins:
        coin.move_coin()
        coin.draw_coin()

    # Check if player collected a coin
    for coin in coins:
        if player_car.rect.colliderect(coin.rect):
            score += 1
            coin.random_place()

    # Every 5 coins = new level, enemies get faster
    new_level = score // 5 + 1
    if new_level > level:
        level = new_level
        enemy_speed_boost += 1
        # Apply new speed to all enemies
        for enemy in enemies:
            enemy.speed = random.randint(6, 8) + enemy_speed_boost

    # Check if player hit any enemy car
    for enemy in enemies:
        if player_car.rect.colliderect(enemy.rect):
            h = pygame.image.load("images/game_over.jpeg")
            h = pygame.transform.scale(h, (width, height))
            screen.blit(h, (0, 0))
            # Show final score on game over screen
            final_text = font.render(f"Score: {score}", True, (255, 255, 255))
            screen.blit(final_text, (width // 2 - 60, height // 2 + 60))
            pygame.display.update()
            # Wait for player to close the window
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

    keys = pygame.key.get_pressed()
    player_car.move_car(keys)
    player_car.draw()

    # Show score and level in the top right corner
    score_text = font.render(f"Score: {score}  Lvl: {level}", True, (128, 52, 36))
    score_rect = score_text.get_rect(topright=(width - 10, 10))
    screen.blit(score_text, score_rect)

    pygame.display.update()
    clock.tick(60)
