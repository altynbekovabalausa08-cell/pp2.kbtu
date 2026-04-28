import pygame
import sys
import db
from game import GameSession, draw_text, load_settings, save_settings
from config import *


# ─── Button helper ────────────────────────────────────────────────────────────

class Button:
    def __init__(self, text, cx, cy, w=160, h=40):
        self.rect = pygame.Rect(0, 0, w, h)
        self.rect.center = (cx, cy)
        self.text = text

    def draw(self, surf):
        pygame.draw.rect(surf, (60, 60, 60), self.rect, border_radius=6)
        pygame.draw.rect(surf, WHITE, self.rect, 2, border_radius=6)
        draw_text(surf, self.text, 20, WHITE, *self.rect.center)

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)


# ─── Username entry screen ────────────────────────────────────────────────────

def screen_username(screen, clock):
    """Let player type a username. Returns the entered string."""
    name = ""
    font = pygame.font.SysFont("Arial", 28)
    while True:
        screen.fill(BLACK)
        draw_text(screen, "Enter your username:", 26, WHITE, SCREEN_WIDTH // 2, 200)
        # show typed text with blinking cursor
        pygame.draw.rect(screen, (40, 40, 40), (100, 240, 400, 44))
        pygame.draw.rect(screen, WHITE, (100, 240, 400, 44), 2)
        txt = font.render(name + "|", True, GREEN)
        screen.blit(txt, (110, 248))
        draw_text(screen, "Press ENTER to confirm", 18, GRAY, SCREEN_WIDTH // 2, 310)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    return name.strip()
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 20 and event.unicode.isprintable():
                    name += event.unicode
        clock.tick(30)


# ─── Main menu ────────────────────────────────────────────────────────────────

def screen_menu(screen, clock):
    """Show main menu. Returns chosen action string."""
    btn_play   = Button("Play",        SCREEN_WIDTH // 2, 260)
    btn_leader = Button("Leaderboard", SCREEN_WIDTH // 2, 320)
    btn_set    = Button("Settings",    SCREEN_WIDTH // 2, 380)
    btn_quit   = Button("Quit",        SCREEN_WIDTH // 2, 440)
    buttons    = [btn_play, btn_leader, btn_set, btn_quit]

    while True:
        screen.fill(BLACK)
        draw_text(screen, "🐍 SNAKE", 54, GREEN, SCREEN_WIDTH // 2, 140)
        for b in buttons:
            b.draw(screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if btn_play.clicked(event):   return "play"
            if btn_leader.clicked(event): return "leaderboard"
            if btn_set.clicked(event):    return "settings"
            if btn_quit.clicked(event):
                pygame.quit(); sys.exit()
        clock.tick(30)


# ─── Game over screen ─────────────────────────────────────────────────────────

def screen_gameover(screen, clock, score, level, best):
    btn_retry = Button("Retry",     SCREEN_WIDTH // 2, 360)
    btn_menu  = Button("Main Menu", SCREEN_WIDTH // 2, 420)

    while True:
        screen.fill(BLACK)
        draw_text(screen, "GAME OVER", 48, RED,   SCREEN_WIDTH // 2, 160)
        draw_text(screen, f"Score : {score}", 26, WHITE, SCREEN_WIDTH // 2, 240)
        draw_text(screen, f"Level : {level}", 26, WHITE, SCREEN_WIDTH // 2, 278)
        draw_text(screen, f"Best  : {best}",  26, YELLOW, SCREEN_WIDTH // 2, 316)
        btn_retry.draw(screen)
        btn_menu.draw(screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if btn_retry.clicked(event): return "retry"
            if btn_menu.clicked(event):  return "menu"
        clock.tick(30)


# ─── Leaderboard screen ───────────────────────────────────────────────────────

def screen_leaderboard(screen, clock):
    btn_back = Button("Back", SCREEN_WIDTH // 2, 560)
    rows = db.get_top10()   # [(rank, username, score, level, date), ...]

    while True:
        screen.fill(BLACK)
        draw_text(screen, "TOP 10", 36, YELLOW, SCREEN_WIDTH // 2, 30)
        font = pygame.font.SysFont("Arial", 16)

        # table header
        header = f"{'#':<4} {'Name':<14} {'Score':<8} {'Lv':<5} {'Date'}"
        screen.blit(font.render(header, True, GRAY), (30, 70))
        pygame.draw.line(screen, GRAY, (30, 90), (570, 90))

        # table rows
        for i, (rank, uname, score, lvl, date) in enumerate(rows):
            line = f"{rank:<4} {uname:<14} {score:<8} {lvl:<5} {date}"
            color = YELLOW if i == 0 else WHITE
            screen.blit(font.render(line, True, color), (30, 100 + i * 40))

        btn_back.draw(screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if btn_back.clicked(event): return
        clock.tick(30)


# ─── Settings screen ──────────────────────────────────────────────────────────

COLOR_OPTIONS = [GREEN, (0, 150, 255), (255, 165, 0), (220, 0, 220)]
COLOR_NAMES   = ["Green", "Blue", "Orange", "Purple"]

def screen_settings(screen, clock, settings):
    btn_grid  = Button("Grid: ON" if settings["grid"] else "Grid: OFF",   SCREEN_WIDTH // 2, 240)
    btn_sound = Button("Sound: ON" if settings["sound"] else "Sound: OFF", SCREEN_WIDTH // 2, 300)
    btn_save  = Button("Save & Back", SCREEN_WIDTH // 2, 460)

    # find current color index
    cur_color_idx = 0
    for i, c in enumerate(COLOR_OPTIONS):
        if list(c) == settings["snake_color"]:
            cur_color_idx = i

    while True:
        screen.fill(BLACK)
        draw_text(screen, "SETTINGS", 36, WHITE, SCREEN_WIDTH // 2, 80)

        # toggle buttons
        btn_grid.draw(screen)
        btn_sound.draw(screen)

        # color picker — row of colored squares
        draw_text(screen, "Snake Color:", 20, WHITE, SCREEN_WIDTH // 2, 360)
        for i, col in enumerate(COLOR_OPTIONS):
            x = 120 + i * 90
            pygame.draw.rect(screen, col, (x, 380, 60, 30))
            if i == cur_color_idx:
                pygame.draw.rect(screen, WHITE, (x, 380, 60, 30), 3)

        btn_save.draw(screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if btn_grid.clicked(event):
                settings["grid"] = not settings["grid"]
                btn_grid.text = "Grid: ON" if settings["grid"] else "Grid: OFF"

            if btn_sound.clicked(event):
                settings["sound"] = not settings["sound"]
                btn_sound.text = "Sound: ON" if settings["sound"] else "Sound: OFF"

            # check color squares
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i in range(len(COLOR_OPTIONS)):
                    x = 120 + i * 90
                    if pygame.Rect(x, 380, 60, 30).collidepoint(event.pos):
                        cur_color_idx = i
                        settings["snake_color"] = list(COLOR_OPTIONS[i])

            if btn_save.clicked(event):
                save_settings(settings)
                return

        clock.tick(30)


# ─── Play loop ────────────────────────────────────────────────────────────────

def run_game(screen, clock, player_id, settings):
    """One full game. Returns (score, level)."""
    best = db.get_personal_best(player_id)
    session = GameSession(best, settings)

    running = True
    while running:
        # dynamic FPS (changes with power-ups / level)
        clock.tick(session.current_fps())

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:    session.change_direction((0, -1))
                if event.key == pygame.K_DOWN:  session.change_direction((0,  1))
                if event.key == pygame.K_LEFT:  session.change_direction((-1, 0))
                if event.key == pygame.K_RIGHT: session.change_direction(( 1, 0))

        alive = session.update()
        session.draw(screen)
        pygame.display.flip()

        if not alive:
            running = False

    return session.score, session.level


# ─── Entry point ──────────────────────────────────────────────────────────────

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Snake TSIS4")
    clock = pygame.time.Clock()

    # init DB tables (safe to call every run)
    try:
        db.init_db()
        db_ok = True
    except Exception as e:
        print("DB error:", e)
        db_ok = False

    settings = load_settings()

    # ask username once per session
    username  = screen_username(screen, clock)
    player_id = db.get_or_create_player(username) if db_ok else 0

    while True:
        action = screen_menu(screen, clock)

        if action == "play":
            while True:
                score, level = run_game(screen, clock, player_id, settings)

                # save to DB
                if db_ok:
                    db.save_session(player_id, score, level)
                    best = db.get_personal_best(player_id)
                else:
                    best = score

                choice = screen_gameover(screen, clock, score, level, best)
                if choice == "menu":
                    break
                # choice == "retry": loop again

        elif action == "leaderboard":
            if db_ok:
                screen_leaderboard(screen, clock)
            else:
                draw_text(screen, "No DB connection", 28, RED, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                pygame.display.flip()
                pygame.time.wait(2000)

        elif action == "settings":
            screen_settings(screen, clock, settings)


if __name__ == "__main__":
    main()