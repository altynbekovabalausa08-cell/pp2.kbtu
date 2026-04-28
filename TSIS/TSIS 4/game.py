import pygame
import random
import json
import os
from config import *


# ─── helpers ────────────────────────────────────────────────────────────────

def load_settings():
    defaults = {"snake_color": list(GREEN), "grid": True, "sound": False}
    if os.path.exists("settings.json"):
        with open("settings.json") as f:
            return json.load(f)
    return defaults


def save_settings(settings):
    with open("settings.json", "w") as f:
        json.dump(settings, f)


def draw_cell(surf, col, row, color):
    pygame.draw.rect(surf, color, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1))


def draw_text(surf, text, size, color, cx, cy):
    font = pygame.font.SysFont("Arial", size)
    img = font.render(text, True, color)
    surf.blit(img, img.get_rect(center=(cx, cy)))


def draw_label(surf, text, color, col, row):
    font = pygame.font.Font(None, 14)
    img = font.render(text, True, color)
    x = col * CELL_SIZE + CELL_SIZE // 2
    y = row * CELL_SIZE - 5
    rect = img.get_rect(center=(x, y))
    surf.blit(img, rect)


def random_cell(occupied):
    while True:
        c = random.randint(0, COLS - 1)
        r = random.randint(0, ROWS - 1)
        if (c, r) not in occupied:
            return c, r


def draw_gradient_background(surf):
    """Рисует вертикальный градиент от тёмно-синего к чёрному."""
    for y in range(SCREEN_HEIGHT):
        ratio = 1.0 - (y / SCREEN_HEIGHT)
        color = (int(20 * ratio), int(20 * ratio), int(60 + 80 * ratio))
        pygame.draw.line(surf, color, (0, y), (SCREEN_WIDTH, y))


# ─── Food ───────────────────────────────────────────────────────────────────

class Food:
    def __init__(self, occupied):
        roll = random.random()
        cumul = 0
        for pts, col, chance in FOOD_WEIGHTS:
            cumul += chance
            if roll < cumul:
                self.points = pts
                self.color = col
                break
        self.pos = random_cell(occupied)
        self.born = pygame.time.get_ticks()

    def expired(self):
        return pygame.time.get_ticks() - self.born > FOOD_LIFETIME

    def draw(self, surf):
        draw_cell(surf, *self.pos, self.color)
        if self.points == 1:
            draw_label(surf, "+1", WHITE, *self.pos)
        elif self.points == 3:
            draw_label(surf, "+3", YELLOW, *self.pos)
        else:
            draw_label(surf, "+5", YELLOW, *self.pos)


class PoisonFood:
    color = DARK_RED

    def __init__(self, occupied):
        self.pos = random_cell(occupied)
        self.born = pygame.time.get_ticks()

    def expired(self):
        return pygame.time.get_ticks() - self.born > FOOD_LIFETIME

    def draw(self, surf):
        draw_cell(surf, *self.pos, self.color)
        draw_label(surf, "-2", WHITE, *self.pos)


# ─── Power-up ────────────────────────────────────────────────────────────────

POWERUP_TYPES = ["speed", "slow", "shield"]
POWERUP_COLORS = {"speed": YELLOW, "slow": BLUE, "shield": PURPLE}
POWERUP_LABELS = {"speed": "SPD", "slow": "SLW", "shield": "SHD"}


class PowerUp:
    def __init__(self, occupied):
        self.kind = random.choice(POWERUP_TYPES)
        self.color = POWERUP_COLORS[self.kind]
        self.pos = random_cell(occupied)
        self.born = pygame.time.get_ticks()

    def expired(self):
        return pygame.time.get_ticks() - self.born > POWERUP_LIFETIME

    def draw(self, surf):
        x = self.pos[0] * CELL_SIZE + CELL_SIZE // 2
        y = self.pos[1] * CELL_SIZE + CELL_SIZE // 2
        r = CELL_SIZE // 2 - 1
        pygame.draw.polygon(surf, self.color,
                            [(x, y - r), (x + r, y), (x, y + r), (x - r, y)])
        label = POWERUP_LABELS[self.kind]
        font = pygame.font.Font(None, 12)
        img = font.render(label, True, WHITE)
        rect = img.get_rect(center=(x, y + r - 3))
        surf.blit(img, rect)


# ─── GameSession ─────────────────────────────────────────────────────────────

class GameSession:
    def __init__(self, personal_best, settings):
        self.settings = settings
        self.personal_best = personal_best
        self.snake_color = tuple(settings["snake_color"])

        cx, cy = COLS // 2, ROWS // 2
        self.body = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction = (1, 0)
        self.next_dir = (1, 0)

        self.score = 0
        self.level = 1
        self.food_eaten = 0

        self.obstacles = []
        self.food = None
        self.poison = None
        self.powerup = None
        self.active_effect = None
        self.effect_end_time = 0
        self.shield_used = False

        self.last_powerup_spawn_time = pygame.time.get_ticks()

        self._spawn_food()
        self._maybe_spawn_poison()

    def _occupied(self):
        cells = set(self.body) | set(self.obstacles)
        if self.food:
            cells.add(self.food.pos)
        if self.poison:
            cells.add(self.poison.pos)
        if self.powerup:
            cells.add(self.powerup.pos)
        return cells

    def _spawn_food(self):
        self.food = Food(self._occupied())

    def _maybe_spawn_poison(self):
        if self.poison is None and random.random() < 0.4:
            self.poison = PoisonFood(self._occupied())

    def _maybe_spawn_powerup(self):
        if self.powerup is None and random.random() < 0.3:
            self.powerup = PowerUp(self._occupied())

    def _auto_spawn_powerup(self):
        now = pygame.time.get_ticks()
        if self.powerup is None and (now - self.last_powerup_spawn_time >= 10000):
            self.powerup = PowerUp(self._occupied())
            self.last_powerup_spawn_time = now

    def _spawn_obstacles(self):
        count = self.level * 2
        head = self.body[0]
        new_obs = []
        attempts = 0
        while len(new_obs) < count and attempts < 500:
            attempts += 1
            c = random.randint(0, COLS - 1)
            r = random.randint(0, ROWS - 1)
            if abs(c - head[0]) <= 3 and abs(r - head[1]) <= 3:
                continue
            cell = (c, r)
            if cell in set(self.body) or cell in new_obs:
                continue
            new_obs.append(cell)
        self.obstacles = new_obs

    def level_up(self):
        self.level += 1
        self.food_eaten = 0
        if self.level >= 3:
            self._spawn_obstacles()

    def current_fps(self):
        fps = BASE_FPS + (self.level - 1) * SPEED_PER_LEVEL
        now = pygame.time.get_ticks()

        if self.active_effect == "speed" and now < self.effect_end_time:
            fps += 4
        elif self.active_effect == "slow" and now < self.effect_end_time:
            fps = max(2, fps - 4)
        elif self.active_effect in ("speed", "slow") and now >= self.effect_end_time:
            self.active_effect = None
        return fps

    def change_direction(self, new_dir):
        if (new_dir[0] + self.direction[0], new_dir[1] + self.direction[1]) != (0, 0):
            self.next_dir = new_dir

    def _rescue_with_shield(self):
        """Перемещает змею в безопасное место, сохраняя прогресс."""
        # Убираем эффект щита (он использован)
        self.active_effect = None
        self.shield_used = True

        # Ищем свободную клетку для головы
        occupied_set = set(self.body) | set(self.obstacles)
        # Стараемся разместить голову не слишком далеко от центра
        safe_cells = []
        for r in range(ROWS):
            for c in range(COLS):
                if (c, r) not in occupied_set:
                    # Добавляем вес к центру
                    dist = abs(c - COLS//2) + abs(r - ROWS//2)
                    safe_cells.append((dist, (c, r)))
        if not safe_cells:
            return False  # нет свободных клеток – игра всё равно закончится
        safe_cells.sort(key=lambda x: x[0])
        new_head = safe_cells[0][1]

        old_head = self.body[0]
        dx = new_head[0] - old_head[0]
        dy = new_head[1] - old_head[1]
        new_body = [(x + dx, y + dy) for (x, y) in self.body]
        # Проверка, не пересекаются ли новые сегменты с препятствиями или между собой
        # Если пересекаются – пробуем другую позицию
        if any((c, r) in self.obstacles for (c, r) in new_body) or len(set(new_body)) != len(new_body):
            # Рекурсивно пробуем другие безопасные клетки
            for _, cell in safe_cells[1:]:
                dx = cell[0] - old_head[0]
                dy = cell[1] - old_head[1]
                new_body = [(x + dx, y + dy) for (x, y) in self.body]
                if not any((c, r) in self.obstacles for (c, r) in new_body) and len(set(new_body)) == len(new_body):
                    self.body = new_body
                    return True
                
            return False
        else:
            self.body = new_body
            return True

    def update(self):
        now = pygame.time.get_ticks()

        # Сброс эффекта shield по таймеру (если не был использован)
        if self.active_effect == "shield" and now >= self.effect_end_time:
            self.active_effect = None

        self._auto_spawn_powerup()

        self.direction = self.next_dir
        hx, hy = self.body[0]
        dx, dy = self.direction
        new_head = (hx + dx, hy + dy)

        collision = False
        # Проверка на смертельное столкновение
        if not (0 <= new_head[0] < COLS and 0 <= new_head[1] < ROWS):
            collision = True
        elif new_head in self.body[1:]:
            collision = True
        elif new_head in self.obstacles:
            collision = True

        if collision:
            if self.active_effect == "shield" and not self.shield_used:
                # Щит спасает: телепортируем змею в безопасное место
                if self._rescue_with_shield():
                    # После спасения не двигаемся в этом кадре, но игра продолжается
                    return True
                else:
                    # Телепортация не удалась – всё равно смерть
                    return False
            else:
                return False

        # ---- Нормальное движение ----
        self.body.insert(0, new_head)

        # Еда
        if self.food and new_head == self.food.pos:
            self.score += self.food.points
            self.food_eaten += 1
            self.food = None
            self._spawn_food()
            self._maybe_spawn_poison()
            self._maybe_spawn_powerup()
            if self.food_eaten >= FOOD_PER_LEVEL:
                self.level_up()
        # Яд
        elif self.poison and new_head == self.poison.pos:
            self.poison = None
            self.score = max(0, self.score - 2)
            for _ in range(2):
                if len(self.body) > 1:
                    self.body.pop()
            if len(self.body) <= 1:
                return False
            self._maybe_spawn_poison()
        # Power-up
        elif self.powerup and new_head == self.powerup.pos:
            self.active_effect = self.powerup.kind
            self.effect_end_time = pygame.time.get_ticks() + POWERUP_EFFECT
            self.shield_used = False   # новый щит — новый шанс
            self.powerup = None
        else:
            self.body.pop()

        # Удаление просроченных предметов
        if self.food and self.food.expired():
            self._spawn_food()
        if self.poison and self.poison.expired():
            self.poison = None
        if self.powerup and self.powerup.expired():
            self.powerup = None

        return True

    def draw(self, surf):
        draw_gradient_background(surf)

        if self.settings.get("grid"):
            for c in range(COLS):
                pygame.draw.line(surf, DARK_GRAY, (c * CELL_SIZE, 0), (c * CELL_SIZE, SCREEN_HEIGHT))
            for r in range(ROWS):
                pygame.draw.line(surf, DARK_GRAY, (0, r * CELL_SIZE), (SCREEN_WIDTH, r * CELL_SIZE))

        for ob in self.obstacles:
            draw_cell(surf, *ob, GRAY)

        if self.food:
            self.food.draw(surf)
        if self.poison:
            self.poison.draw(surf)
        if self.powerup:
            self.powerup.draw(surf)

        for i, seg in enumerate(self.body):
            color = WHITE if i == 0 else self.snake_color
            draw_cell(surf, *seg, color)

        # Визуальный эффект щита (круг вокруг головы)
        if self.active_effect == "shield" and not self.shield_used:
            head = self.body[0]
            shield_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(shield_surf, (*PURPLE, 128), (CELL_SIZE // 2, CELL_SIZE // 2), CELL_SIZE // 2 + 2)
            surf.blit(shield_surf, (head[0] * CELL_SIZE, head[1] * CELL_SIZE))

        # Цветной оверлей для speed и slow
        if self.active_effect and self.active_effect != "shield":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            if self.active_effect == "speed":
                overlay.fill((255, 220, 0, 40))
            elif self.active_effect == "slow":
                overlay.fill((0, 120, 255, 40))
            surf.blit(overlay, (0, 0))

        font = pygame.font.SysFont("Arial", 16)
        surf.blit(font.render(f"Score:{self.score}  Lv:{self.level}  Best:{self.personal_best}", True, WHITE), (4, 4))

        if self.active_effect:
            remaining = max(0, self.effect_end_time - pygame.time.get_ticks()) // 1000
            c = POWERUP_COLORS.get(self.active_effect, WHITE)
            surf.blit(font.render(f"{self.active_effect.upper()} {remaining}s", True, c), (4, 22))