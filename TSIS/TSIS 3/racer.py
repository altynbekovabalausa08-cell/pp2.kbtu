import pygame
import random
from pygame.locals import *

WIDTH = 500
HEIGHT = 700

LANES = [110, 250, 390]

COIN_TYPES = [
    {"value": 1, "weight": 60, "label": "+1", "color": (255, 215, 0)},
    {"value": 3, "weight": 30, "label": "+3", "color": (192, 192, 192)},
    {"value": 5, "weight": 10, "label": "+5", "color": (255, 100, 100)},
]

POWERUP_TYPES = ["nitro", "shield", "repair"]

POWERUP_META = {
    "nitro":  {"label": "NITRO",  "color": (255, 200, 0),   "duration": 4.0, "img": "assets/Nitro.png"},
    "shield": {"label": "SHIELD", "color": (0,   200, 255), "duration": None, "img": "assets/shield.png"},
    "repair": {"label": "REPAIR", "color": (0,   220, 120), "duration": 0,   "img": "assets/heal.png"},
}

DIFFICULTY_PARAMS = {
    "easy":   {"base_speed": 4, "enemy_speed_range": (4, 6),  "speed_up_every": 8,  "obstacle_freq": 0.003},
    "normal": {"base_speed": 5, "enemy_speed_range": (6, 8),  "speed_up_every": 5,  "obstacle_freq": 0.005},
    "hard":   {"base_speed": 7, "enemy_speed_range": (8, 11), "speed_up_every": 3,  "obstacle_freq": 0.009},
}

SECOND_ENEMY_AT = 10
THIRD_ENEMY_AT = 25
MIN_ENEMY_GAP = 280
POWERUP_LIFETIME = 8.0

_font_cache = {}

def get_font(size: int):
    if size not in _font_cache:
        _font_cache[size] = pygame.font.Font(None, size)
    return _font_cache[size]

_img_cache = {}

def _load_image(path: str, size: tuple, fallback_color=(200, 50, 50)):
    key = (path, size)
    if key in _img_cache:
        return _img_cache[key]
    try:
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.scale(img, size)
    except:
        img = pygame.Surface(size, pygame.SRCALPHA)
        img.fill((*fallback_color, 200))
    _img_cache[key] = img
    return img

class Car(pygame.sprite.Sprite):
    COLOR_TINTS = {
        "default": None,
        "red":   (255, 80, 80),
        "blue":  (80, 120, 255),
        "green": (80, 220, 120),
    }

    def __init__(self, car_color: str = "default"):
        super().__init__()
        # Увеличили размер машины
        base = _load_image("assets/car.png", (140, 170), (80, 80, 200))
        if car_color != "default" and car_color in self.COLOR_TINTS:
            tint = pygame.Surface(base.get_size(), pygame.SRCALPHA)
            r, g, b = self.COLOR_TINTS[car_color]
            tint.fill((r, g, b, 90))
            base = base.copy()
            base.blit(tint, (0, 0))
        self.image = base
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, 600)
        # Хитбокс увеличен
        self.hitbox = pygame.Rect(0, 0, 85, 130)
        self.hitbox.center = self.rect.center

        self.nitro_active = False
        self.nitro_timer = 0.0
        self.shield_active = False
        self.repair_pending = False
        self.base_speed = 10

        self._shield_icon = _load_image("assets/shield.png", (36, 36), (0, 200, 255))

    @property
    def move_speed(self):
        return self.base_speed + (6 if self.nitro_active else 0)

    def move_car(self, keys, oil_slick=False, drift_dir=0):
        spd = self.move_speed
        if oil_slick:
            spd = max(2, spd // 3)
            if keys[K_LEFT] and self.rect.left > 10:
                self.rect.x -= spd
            if keys[K_RIGHT] and self.rect.right < WIDTH - 10:
                self.rect.x += spd
            if drift_dir < 0 and self.rect.left > 10:
                self.rect.x -= 2
            if drift_dir > 0 and self.rect.right < WIDTH - 10:
                self.rect.x += 2
        else:
            if keys[K_LEFT] and self.rect.left > 10:
                self.rect.x -= spd
            if keys[K_RIGHT] and self.rect.right < WIDTH - 10:
                self.rect.x += spd
        self.hitbox.center = self.rect.center

    def update_power(self, dt):
        if self.nitro_active:
            self.nitro_timer -= dt
            if self.nitro_timer <= 0:
                self.nitro_active = False

    def activate_powerup(self, kind):
        self.nitro_active = False
        self.nitro_timer = 0.0
        self.shield_active = False
        self.repair_pending = False
        if kind == "nitro":
            self.nitro_active = True
            self.nitro_timer = POWERUP_META["nitro"]["duration"]
        elif kind == "shield":
            self.shield_active = True
        elif kind == "repair":
            self.repair_pending = True

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        if self.shield_active:
            border = self.rect.inflate(8, 8)
            pygame.draw.rect(screen, (0, 200, 255), border, 3, border_radius=8)
            screen.blit(self._shield_icon, (self.rect.right - 20, self.rect.top - 14))
        if self.nitro_active:
            try:
                boost_img = _load_image("assets/Nitro.png", (70, 70), (255, 160, 0))
            except:
                boost_img = pygame.Surface((70, 70), pygame.SRCALPHA)
                boost_img.fill((255, 200, 0, 200))
            screen.blit(boost_img, (self.rect.centerx - 35, self.rect.bottom - 10))

class EnemyCar(pygame.sprite.Sprite):
    COLORS = [(200, 50, 50), (50, 50, 200), (50, 200, 50), (200, 150, 50)]

    def __init__(self, speed_boost=0, difficulty="normal"):
        super().__init__()
        self.image = _load_image("assets/enemy_car.png", (80, 170), random.choice(self.COLORS))
        self.rect = self.image.get_rect()
        self.hitbox = pygame.Rect(0, 0, 48, 110)
        self.speed_boost = speed_boost
        self.diff_params = DIFFICULTY_PARAMS[difficulty]
        self.reset()

    def reset(self):
        self.rect.centerx = random.choice(LANES)
        self.rect.y = random.randint(-300, -60)
        lo, hi = self.diff_params["enemy_speed_range"]
        self.speed = random.randint(lo, hi) + self.speed_boost
        self.hitbox.center = self.rect.center

    def apply_boost(self, boost):
        self.speed_boost = boost
        lo, hi = self.diff_params["enemy_speed_range"]
        self.speed = random.randint(lo, hi) + self.speed_boost

    def move_ecar(self):
        self.rect.y += self.speed
        self.hitbox.center = self.rect.center
        if self.rect.y > HEIGHT + 200:
            self.reset()

    def draw_ecar(self, screen):
        screen.blit(self.image, self.rect)

class Coin(pygame.sprite.Sprite):
    def __init__(self, base_speed=5):
        super().__init__()
        self.base_image = _load_image("assets/coin.png", (44, 44), (255, 200, 0))
        self.rect = self.base_image.get_rect()
        self.speed = base_speed
        self._pick_type()
        self.random_place()

    def _pick_type(self):
        weights = [ct["weight"] for ct in COIN_TYPES]
        self.coin_type = random.choices(COIN_TYPES, weights=weights, k=1)[0]
        self.image = self.base_image.copy()
        tint = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
        r, g, b = self.coin_type["color"]
        tint.fill((r, g, b, 100))
        self.image.blit(tint, (0, 0))

    def random_place(self):
        self._pick_type()
        self.rect.centerx = random.choice(LANES)
        self.rect.y = random.randint(-500, -60)

    def move_coin(self):
        self.rect.y += self.speed
        if self.rect.y > HEIGHT + 20:
            self.random_place()

    def draw_coin(self, screen):
        screen.blit(self.image, self.rect)
        font = get_font(24)
        label = font.render(self.coin_type["label"], True, self.coin_type["color"])
        screen.blit(label, (self.rect.x + 4, self.rect.y - 18))

class PowerUp(pygame.sprite.Sprite):
    _icons = {}

    def __init__(self, base_speed=4):
        super().__init__()
        self.speed = base_speed
        self.lifetime = POWERUP_LIFETIME
        self.image = pygame.Surface((64, 64), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self._place()

    @classmethod
    def _get_icon(cls, kind):
        if kind not in cls._icons:
            path = POWERUP_META[kind]["img"]
            try:
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, (58, 58))
            except:
                img = pygame.Surface((58, 58), pygame.SRCALPHA)
                img.fill(POWERUP_META[kind]["color"] + (200,))
            if kind == "nitro":
                font = pygame.font.Font(None, 22)
                text = font.render("Nitro", True, (255, 255, 255))
                text_rect = text.get_rect(center=(img.get_width()//2, img.get_height()//2 + 12))
                bg = pygame.Surface((text.get_width()+4, text.get_height()+2), pygame.SRCALPHA)
                bg.fill((0,0,0,150))
                img.blit(bg, (text_rect.x-2, text_rect.y-1))
                img.blit(text, text_rect)
            cls._icons[kind] = img
        return cls._icons[kind]

    def _place(self):
        self.rect.centerx = random.choice(LANES)
        self.rect.y = random.randint(-600, -80)
        self.lifetime = POWERUP_LIFETIME
        self.kind = random.choice(POWERUP_TYPES)
        self.meta = POWERUP_META[self.kind]
        self.image = pygame.Surface((64, 64), pygame.SRCALPHA)
        icon = self._get_icon(self.kind)
        self.image.blit(icon, (3, 3))
        r, g, b = self.meta["color"]
        pygame.draw.circle(self.image, (r, g, b, 180), (32, 32), 32, 3)

    def update_pos(self, dt):
        self.rect.y += self.speed
        self.lifetime -= dt
        if self.rect.y > HEIGHT + 20 or self.lifetime <= 0:
            self._place()
            return True
        return False

    def draw_powerup(self, screen):
        screen.blit(self.image, self.rect)
        bar_w = int(64 * max(0, self.lifetime / POWERUP_LIFETIME))
        pygame.draw.rect(screen, (60, 60, 60), (self.rect.x, self.rect.bottom + 2, 64, 4))
        pygame.draw.rect(screen, self.meta["color"], (self.rect.x, self.rect.bottom + 2, bar_w, 4))

OBSTACLE_KINDS = [
    {"kind": "oil",     "img": "assets/oil.png",      "color": (30, 20, 80, 180), "label": "OIL", "slow": True, "damage": False, "size": (72, 60)},
    {"kind": "pothole", "img": "assets/obstacle.png", "color": (60, 40, 20, 200), "label": "HOLE", "slow": False, "damage": True,  "size": (60, 40)},
]

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, base_speed=4):
        super().__init__()
        self.base_speed = base_speed
        self._pick()

    def _pick(self):
        self.otype = random.choice(OBSTACLE_KINDS)
        w, h = self.otype["size"]
        self.image = _load_image(self.otype["img"], (w, h), self.otype["color"][:3])
        self.rect = self.image.get_rect()
        self.rect.centerx = random.choice(LANES)
        self.rect.y = random.randint(-400, -60)
        self.speed = self.base_speed + random.randint(0, 2)

    def move_obstacle(self):
        self.rect.y += self.speed
        if self.rect.y > HEIGHT + 20:
            self._pick()

    def draw_obstacle(self, screen):
        screen.blit(self.image, self.rect)

def spawn_spaced_enemy(existing_enemies, boost=0, difficulty="normal"):
    for _ in range(20):
        candidate = EnemyCar(speed_boost=boost, difficulty=difficulty)
        too_close = any(abs(candidate.rect.y - e.rect.y) < MIN_ENEMY_GAP for e in existing_enemies)
        if not too_close:
            return candidate
    return EnemyCar(speed_boost=boost, difficulty=difficulty)