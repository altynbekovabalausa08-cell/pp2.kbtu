import pygame
import sys
import random
from pygame.locals import *

# ── Bootstrap ─────────────────────────────────────────────────────────────────
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
pygame.mixer.set_num_channels(16)
pygame.display.set_caption("Racer — TSIS-3")

from racer import (
    Car, EnemyCar, Coin, PowerUp, Obstacle,
    WIDTH, HEIGHT, LANES, DIFFICULTY_PARAMS, COIN_TYPES,
    SECOND_ENEMY_AT, THIRD_ENEMY_AT, MIN_ENEMY_GAP,
    spawn_spaced_enemy, _load_image,
)
from ui import show_main_menu, show_username_entry, show_settings, show_leaderboard, show_game_over
from persistence import load_settings, save_settings, save_score

# ── Display & clock ───────────────────────────────────────────────────────────
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock  = pygame.time.Clock()

# ── Assets ────────────────────────────────────────────────────────────────────
bg_img       = _load_image("assets/way.png",       (WIDTH, HEIGHT), (40, 44, 60))
game_over_bg = _load_image("assets/game_over.png", (WIDTH, HEIGHT), (20, 10, 10))

# ── Sound loader ──────────────────────────────────────────────────────────────
def _load_sound(path: str):
    try:
        s = pygame.mixer.Sound(path)
        return s
    except Exception as e:
        print(f"[SOUND] Could not load {path}: {e}")
        return None

snd_crash   = _load_sound("assets/crash.mp3")
snd_powerup = _load_sound("assets/powerup.mp3")

def _play_bg_music(volume: int):
    if volume == 0:
        pygame.mixer.music.stop()
        return
    try:
        pygame.mixer.music.load("assets/bg_music.mp3")
        pygame.mixer.music.set_volume(volume / 100)
        pygame.mixer.music.play(-1)
    except Exception:
        pass

def _play_sfx(sound, volume: int):
    if sound and volume > 0:
        sound.set_volume(volume / 100)
        sound.play()

# ── HUD fonts ─────────────────────────────────────────────────────────────────
font_hud   = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)
font_pw    = pygame.font.Font(None, 28)

# ── Game state factory ────────────────────────────────────────────────────────
def reset_game(settings: dict) -> dict:
    diff   = settings.get("difficulty", "normal")
    params = DIFFICULTY_PARAMS[diff]
    player   = Car(car_color=settings.get("car_color", "default"))
    enemies  = [EnemyCar(speed_boost=0, difficulty=diff)]
    coins    = [Coin(base_speed=params["base_speed"]) for _ in range(3)]
    powerup  = PowerUp(base_speed=params["base_speed"] - 1)
    obstacle = Obstacle(base_speed=params["base_speed"])
    return {
        "player":          player,
        "enemies":         enemies,
        "coins":           coins,
        "powerup":         powerup,
        "obstacle":        obstacle,
        "score":           0,
        "distance":        0,
        "coins_collected": 0,
        "level":           1,
        "boost":           0,
        "diff":            diff,
        "params":          params,
        "oil_slick":       False,
        "oil_timer":       0.0,
        "drift_dir":       0,
        "damage_flash":    0.0,
        "repair_active":   False,      # активна ли защита от препятствий
        "repair_timer":    0.0,        # оставшееся время (сек)
        "repair_text":     0,          # для надписи "REPAIRED!"
    }

def draw_hud(screen: pygame.Surface, state: dict, username: str):
    player = state["player"]
    W = screen.get_width()
    hud = font_hud.render(f"Score: {state['score']}   Lvl: {state['level']}", True, (255, 200, 80))
    screen.blit(hud, hud.get_rect(topright=(W - 8, 8)))
    dist = font_small.render(f"Dist: {state['distance']} m   Coins: {state['coins_collected']}", True, (160, 180, 200))
    screen.blit(dist, dist.get_rect(topright=(W - 8, 44)))
    name = font_small.render(username, True, (120, 130, 150))
    screen.blit(name, (8, 8))

    if player.nitro_active:
        _draw_status(screen, f"NITRO  {player.nitro_timer:.1f}s", (255, 220, 0))
    if player.shield_active:
        _draw_status(screen, "SHIELD ACTIVE", (0, 200, 255), y=HEIGHT - 58)
    if state["oil_slick"]:
        _draw_status(screen, "SLIPPING!", (80, 60, 200), y=HEIGHT - 88)
    if state["repair_active"]:
        # показываем таймер ремонта (зелёный)
        _draw_status(screen, f"REPAIR {state['repair_timer']:.1f}s", (0, 255, 0), y=HEIGHT - 88)

    for i, ct in enumerate(COIN_TYPES):
        lt = font_small.render(f"{ct['label']}  ({ct['weight']}%)", True, ct["color"])
        screen.blit(lt, (8, 28 + i * 20))

    # Отображение надписи "REPAIRED!"
    if state.get("repair_text", 0) > 0:
        txt = font_pw.render("REPAIRED!", True, (0, 255, 0))
        r = txt.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        bg = pygame.Surface((r.width + 16, r.height + 6), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 180))
        screen.blit(bg, (r.x - 8, r.y - 3))
        screen.blit(txt, r)
        state["repair_text"] -= 1

def _draw_status(screen, msg, color, y=HEIGHT - 30):
    txt = font_pw.render(msg, True, color)
    r = txt.get_rect(centerx=WIDTH // 2, y=y)
    bg = pygame.Surface((r.width + 16, r.height + 6), pygame.SRCALPHA)
    bg.fill((0, 0, 0, 140))
    screen.blit(bg, (r.x - 8, r.y - 3))
    screen.blit(txt, r)

def draw_damage_flash(screen, state):
    if state["damage_flash"] > 0:
        alpha = int(min(state["damage_flash"] / 0.3, 1.0) * 160)
        fl = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        fl.fill((220, 30, 30, alpha))
        screen.blit(fl, (0, 0))
        state["damage_flash"] -= 1/60

# ── Game loop ─────────────────────────────────────────────────────────────────
def run_game(settings: dict, username: str) -> tuple:
    state = reset_game(settings)
    params = state["params"]
    SUE = params["speed_up_every"]
    road_y = 0
    road_speed = params["base_speed"] + 2
    sfx_vol = settings.get("sfx_volume", 80)

    while True:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                return state["score"], state["distance"], state["coins_collected"], state["level"]

        player = state["player"]

        # Обновление таймера ремонта
        if state["repair_active"]:
            state["repair_timer"] -= dt
            if state["repair_timer"] <= 0:
                state["repair_active"] = False
                state["repair_timer"] = 0.0

        # Road scroll
        road_y = (road_y + road_speed) % HEIGHT
        screen.blit(bg_img, (0, road_y - HEIGHT))
        screen.blit(bg_img, (0, road_y))

        state["distance"] += 1
        if state["distance"] % 60 == 0:
            state["score"] += 1

        keys = pygame.key.get_pressed()
        if state["oil_slick"]:
            state["oil_timer"] -= dt
            if state["oil_timer"] <= 0:
                state["oil_slick"] = False
                state["drift_dir"] = 0

        player.move_car(keys, oil_slick=state["oil_slick"], drift_dir=state["drift_dir"])
        player.update_power(dt)

        if state["damage_flash"] > 0:
            state["damage_flash"] = max(0.0, state["damage_flash"] - dt)

        # Enemies
        for enemy in state["enemies"]:
            enemy.move_ecar()
            enemy.draw_ecar(screen)

        # Coins
        for coin in state["coins"]:
            coin.move_coin()
            coin.draw_coin(screen)
            if player.hitbox.colliderect(coin.rect):
                state["score"] += coin.coin_type["value"]
                state["coins_collected"] += coin.coin_type["value"]
                coin.random_place()

        # Power-up
        pu = state["powerup"]
        pu.update_pos(dt)
        pu.draw_powerup(screen)
        if player.hitbox.colliderect(pu.rect):
            player.activate_powerup(pu.kind)
            _play_sfx(snd_powerup, sfx_vol)
            if pu.kind == "repair":
                # Активируем защиту от препятствий на 5 секунд
                state["repair_active"] = True
                state["repair_timer"] = 5.0
                # Очищаем текущее скольжение
                state["oil_slick"] = False
                state["oil_timer"] = 0.0
                state["drift_dir"] = 0
                state["damage_flash"] = 0.0
                player.repair_pending = False
                # Визуальный эффект
                state["repair_text"] = 60   # надпись на 1 сек
            pu._place()

        # Obstacle
        obs = state["obstacle"]
        obs.move_obstacle()
        obs.draw_obstacle(screen)
        if player.hitbox.colliderect(obs.rect):
            # Если активен repair, препятствие просто удаляется без последствий
            if state["repair_active"]:
                obs._pick()   # убираем препятствие
                # продолжаем, не нанося урон и не создавая скольжения
            else:
                if obs.otype["kind"] == "oil":
                    if not state["oil_slick"]:
                        state["oil_slick"] = True
                        state["oil_timer"] = 2.5
                        state["drift_dir"] = random.choice([-1, 1])
                        obs._pick()
                elif obs.otype["kind"] in ("pothole", "barrier"):
                    if player.shield_active:
                        player.shield_active = False
                        state["damage_flash"] = 0.2
                        obs._pick()
                    else:
                        _play_sfx(snd_crash, sfx_vol)
                        save_score(username, state["score"], state["distance"] // 60)
                        return state["score"], state["distance"] // 60, state["coins_collected"], state["level"]

        # Spawn extra enemies
        diff = state["diff"]
        if state["score"] >= SECOND_ENEMY_AT and len(state["enemies"]) < 2:
            state["enemies"].append(spawn_spaced_enemy(state["enemies"], state["boost"], diff))
        if state["score"] >= THIRD_ENEMY_AT and len(state["enemies"]) < 3:
            state["enemies"].append(spawn_spaced_enemy(state["enemies"], state["boost"], diff))

        # Level scaling
        new_level = state["score"] // SUE + 1
        if new_level > state["level"]:
            state["level"] = new_level
            state["boost"] += 1
            road_speed = params["base_speed"] + 2 + state["boost"]
            for enemy in state["enemies"]:
                enemy.apply_boost(state["boost"])
            obs.base_speed = params["base_speed"] + state["boost"] // 2
            pu.speed = max(3, params["base_speed"] - 1 + state["boost"] // 3)
            if random.random() < min(0.3 + state["boost"] * 0.05, 0.7):
                obs._pick()

        # Enemy collision (враги не блокируются repair)
        for enemy in state["enemies"]:
            if player.hitbox.colliderect(enemy.hitbox):
                if player.shield_active:
                    player.shield_active = False
                    state["damage_flash"] = 0.4
                    enemy.reset()
                else:
                    _play_sfx(snd_crash, sfx_vol)
                    save_score(username, state["score"], state["distance"] // 60)
                    return state["score"], state["distance"] // 60, state["coins_collected"], state["level"]

        player.draw(screen)
        draw_damage_flash(screen, state)
        draw_hud(screen, state, username)
        pygame.display.update()

# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    settings = load_settings()
    username = settings.get("username", "")
    _play_bg_music(settings.get("music_volume", 40))

    while True:
        choice = show_main_menu(screen, clock)

        if choice == "quit":
            pygame.quit(); sys.exit()
        elif choice == "leaderboard":
            show_leaderboard(screen, clock)
        elif choice == "settings":
            old_mvol = settings.get("music_volume", 40)
            settings = show_settings(screen, clock, settings)
            save_settings(settings)
            new_mvol = settings.get("music_volume", 40)
            if new_mvol != old_mvol:
                _play_bg_music(new_mvol)
        elif choice == "play":
            if not username:
                username = show_username_entry(screen, clock, settings.get("username", ""))
                settings["username"] = username
                save_settings(settings)
            while True:
                score, distance, coins_total, level = run_game(settings, username)
                action = show_game_over(screen, clock, score, distance, coins_total, level)
                if action == "retry":
                    continue
                break

if __name__ == "__main__":
    main()