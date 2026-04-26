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

game_over_img = pygame.image.load("images/game_over.jpeg")
game_over_img = pygame.transform.scale(game_over_img, (width, height))

font = pygame.font.Font(None, 41)


class EnemyCar(pygame.sprite.Sprite):
    def __init__(self, speed_boost=0):
        super().__init__()
        self.image = pygame.image.load("images/enemy_car.png")
        self.image = pygame.transform.scale(self.image, (80, 170))
        self.rect = self.image.get_rect()
        # Smaller hitbox so collision only happens when cars truly overlap
        self.hitbox = pygame.Rect(0, 0, 48, 110)
        self.speed_boost = speed_boost
        self.reset()

    def reset(self):
        self.rect.center = (random.randint(60, width - 60), -50)
        self.speed = random.randint(6, 8) + self.speed_boost
        self.hitbox.center = self.rect.center

    def move_ecar(self):
        self.rect.y += self.speed
        # Keep the small hitbox centered on the image every frame
        self.hitbox.center = self.rect.center
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
        # Smaller hitbox for the player car too
        self.hitbox = pygame.Rect(0, 0, 70, 110)
        self.hitbox.center = self.rect.center

    def move_car(self, keys):
        if keys[K_LEFT] and self.rect.left > 10:
            self.rect.x -= 10
        if keys[K_RIGHT] and self.rect.right < width - 10:
            self.rect.x += 10
        self.hitbox.center = self.rect.center

    def draw(self):
        screen.blit(self.image, self.rect)


def reset_game():
    # Reset all game objects and variables to start a new game
    player_car = Car()
    enemies = [EnemyCar(), EnemyCar()]   # 2 enemies instead of 3
    coins = [Coin(), Coin(), Coin()]
    return player_car, enemies, coins, 0, 1, 0


def show_game_over(score, level):
    screen.blit(game_over_img, (0, 0))
    final_text = font.render(f"Score: {score}  Lvl: {level}", True, (255, 255, 255))
    screen.blit(final_text, (width // 2 - 80, height // 2 + 60))
    hint = pygame.font.Font(None, 28).render("SPACE - play again   ESC - quit", True, (255, 255, 255))
    screen.blit(hint, (width // 2 - 140, height // 2 + 110))
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()


player_car, enemies, coins, score, level, enemy_speed_boost = reset_game()

flag = True
while flag:
    screen.blit(bg, (0, 0))

    for i in pygame.event.get():
        if i.type == pygame.QUIT:
            flag = False
            pygame.quit()
            sys.exit()

    for enemy in enemies:
        enemy.move_ecar()
        enemy.draw_ecar()

    for coin in coins:
        coin.move_coin()
        coin.draw_coin()

    # Check coin collection
    for coin in coins:
        if player_car.hitbox.colliderect(coin.rect):
            score += 1
            coin.random_place()

    # Every 5 coins = new level, enemies get faster
    new_level = score // 5 + 1
    if new_level > level:
        level = new_level
        enemy_speed_boost += 1
        for enemy in enemies:
            enemy.speed = random.randint(6, 8) + enemy_speed_boost

    # Use small hitboxes for collision — feels fair to the player
    for enemy in enemies:
        if player_car.hitbox.colliderect(enemy.hitbox):
            show_game_over(score, level)
            player_car, enemies, coins, score, level, enemy_speed_boost = reset_game()
            break

    keys = pygame.key.get_pressed()
    player_car.move_car(keys)
    player_car.draw()

    score_text = font.render(f"Score: {score}  Lvl: {level}", True, (128, 52, 36))
    score_rect = score_text.get_rect(topright=(width - 10, 10))
    screen.blit(score_text, score_rect)

    pygame.display.update()
    clock.tick(60)