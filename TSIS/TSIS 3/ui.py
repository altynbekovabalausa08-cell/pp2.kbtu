import pygame
import sys
from pygame.locals import *
from persistence import load_leaderboard, save_settings, load_settings

# ── Palette ───────────────────────────────────────────────────────────────────
C_BG      = (10,  12,  20)
C_ROAD    = (30,  34,  48)
C_ACCENT  = (255, 180,   0)
C_WHITE   = (240, 240, 240)
C_GREY    = (130, 130, 150)
C_RED     = (230,  60,  60)
C_GREEN   = ( 60, 200, 120)
C_BLUE    = ( 60, 140, 255)
C_PANEL   = ( 22,  26,  40)


# ── Drawing helpers ───────────────────────────────────────────────────────────

def _font(size: int) -> pygame.font.Font:
    return pygame.font.Font(None, size)


def _draw_rounded_rect(surf: pygame.Surface, color, rect, radius: int = 12):
    pygame.draw.rect(surf, color, rect, border_radius=radius)


def _draw_button(surf: pygame.Surface, rect, label: str, active: bool = False,
                 fg=C_WHITE, bg=C_ROAD, active_bg=C_ACCENT, active_fg=C_BG,
                 font_size: int = 34) -> pygame.Rect:
    col    = active_bg if active else bg
    fcol   = active_fg if active else fg
    _draw_rounded_rect(surf, col, rect, 10)
    pygame.draw.rect(surf, C_ACCENT, rect, 2, border_radius=10)
    f      = _font(font_size)
    txt    = f.render(label, True, fcol)
    surf.blit(txt, txt.get_rect(center=rect.center))
    return rect


def _title(surf: pygame.Surface, text: str, y: int, size: int = 72, color=C_ACCENT):
    f   = _font(size)
    txt = f.render(text, True, color)
    surf.blit(txt, txt.get_rect(centerx=surf.get_width() // 2, y=y))


def _subtitle(surf: pygame.Surface, text: str, y: int, size: int = 28, color=C_GREY):
    f   = _font(size)
    txt = f.render(text, True, color)
    surf.blit(txt, txt.get_rect(centerx=surf.get_width() // 2, y=y))


def _road_bg(surf: pygame.Surface):
    """Draw a simple road background for menu screens."""
    surf.fill(C_BG)
    # Road strip
    pygame.draw.rect(surf, C_ROAD, (80, 0, surf.get_width() - 160, surf.get_height()))
    # Lane dashes
    for y in range(0, surf.get_height(), 60):
        pygame.draw.rect(surf, (60, 65, 80), (surf.get_width() // 2 - 4, y, 8, 36))


# ── Main Menu ─────────────────────────────────────────────────────────────────

def show_main_menu(screen: pygame.Surface, clock: pygame.time.Clock) -> str:
    """
    Blocking call.  Returns one of: 'play' | 'leaderboard' | 'settings' | 'quit'
    """
    W, H   = screen.get_size()
    buttons = {
        "play":        pygame.Rect(W // 2 - 140, 260, 280, 52),
        "leaderboard": pygame.Rect(W // 2 - 140, 330, 280, 52),
        "settings":    pygame.Rect(W // 2 - 140, 400, 280, 52),
        "quit":        pygame.Rect(W // 2 - 140, 470, 280, 52),
    }
    labels = {
        "play":        "PLAY",
        "leaderboard": "LEADERBOARD",
        "settings":    "SETTINGS",
        "quit":        "QUIT",
    }
    hover = None

    while True:
        _road_bg(screen)
        _title(screen,    "RACER",       90)
        _subtitle(screen, "TSIS-3 Edition", 170, 32, C_GREY)
        # Decorative speed lines
        for i, lx in enumerate([20, 460]):
            for j in range(4):
                pygame.draw.line(screen, C_ACCENT,
                                 (lx, 200 + j * 80), (lx, 240 + j * 80), 3)

        mx, my = pygame.mouse.get_pos()
        hover  = None
        for key, rect in buttons.items():
            is_hov = rect.collidepoint(mx, my)
            if is_hov:
                hover = key
            _draw_button(screen, rect, labels[key], active=is_hov)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                for key, rect in buttons.items():
                    if rect.collidepoint(event.pos):
                        return key
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit(); sys.exit()

        clock.tick(60)


# ── Username Entry ────────────────────────────────────────────────────────────

def show_username_entry(screen: pygame.Surface, clock: pygame.time.Clock,
                        default_name: str = "") -> str:
    """
    Blocking input screen.  Returns the entered username (non-empty).
    """
    W, H = screen.get_size()
    name = list(default_name)
    btn_ok = pygame.Rect(W // 2 - 80, 420, 160, 50)
    error  = ""

    while True:
        _road_bg(screen)
        _title(screen, "ENTER NAME", 140, 56)
        _subtitle(screen, "Your name will be saved to the leaderboard.", 210, 24)

        # Input box
        box = pygame.Rect(W // 2 - 160, 270, 320, 52)
        _draw_rounded_rect(screen, C_PANEL, box, 10)
        pygame.draw.rect(screen, C_ACCENT, box, 2, border_radius=10)
        f   = _font(38)
        txt = f.render("".join(name) + "|", True, C_WHITE)
        screen.blit(txt, txt.get_rect(midleft=(box.left + 12, box.centery)))

        if error:
            ef  = _font(24)
            et  = ef.render(error, True, C_RED)
            screen.blit(et, et.get_rect(centerx=W // 2, y=340))

        mx, my = pygame.mouse.get_pos()
        _draw_button(screen, btn_ok, "START ▶", btn_ok.collidepoint(mx, my),
                     active_bg=C_GREEN, active_fg=C_BG)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_BACKSPACE:
                    if name:
                        name.pop()
                    error = ""
                elif event.key in (K_RETURN, K_KP_ENTER):
                    if name:
                        return "".join(name)
                    error = "Please enter a name!"
                elif event.key == K_ESCAPE:
                    return default_name or "Player"
                else:
                    ch = event.unicode
                    if ch.isprintable() and len(name) < 18:
                        name.append(ch)
                    error = ""
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if btn_ok.collidepoint(event.pos):
                    if name:
                        return "".join(name)
                    error = "Please enter a name!"

        clock.tick(60)


# ── Settings Screen ───────────────────────────────────────────────────────────

def _draw_volume_slider(surf, label, rect_bg, value, color=C_ACCENT):
    """Draw a labelled horizontal volume slider (0–100). Returns the bar rect."""
    sf = _font(26)
    surf.blit(sf.render(label, True, C_GREY), (rect_bg.x, rect_bg.y - 26))
    # Track
    pygame.draw.rect(surf, (50, 55, 70), rect_bg, border_radius=6)
    # Fill
    fill_w = int(rect_bg.width * value / 100)
    if fill_w > 0:
        fill_r = pygame.Rect(rect_bg.x, rect_bg.y, fill_w, rect_bg.height)
        pygame.draw.rect(surf, color, fill_r, border_radius=6)
    # Knob
    knob_x = rect_bg.x + fill_w
    pygame.draw.circle(surf, C_WHITE, (knob_x, rect_bg.centery), 10)
    # Value text
    vf = _font(22)
    vt = vf.render(f"{value}%", True, C_WHITE)
    surf.blit(vt, (rect_bg.right + 10, rect_bg.centery - 10))
    return rect_bg


def show_settings(screen: pygame.Surface, clock: pygame.time.Clock,
                  settings: dict) -> dict:
    """
    Blocking settings screen.  Mutates and returns the settings dict.
    Separate volume sliders for music and SFX.
    """
    W, H  = screen.get_size()

    CAR_COLORS    = ["default", "red", "blue", "green"]
    COLOR_DISPLAY = {"default": C_WHITE, "red": C_RED, "blue": C_BLUE, "green": C_GREEN}
    DIFFICULTIES  = ["easy", "normal", "hard"]

    # Ensure volume keys exist with defaults
    if "music_volume" not in settings:
        settings["music_volume"] = 40
    if "sfx_volume" not in settings:
        settings["sfx_volume"] = 80

    btn_back  = pygame.Rect(W // 2 - 100, H - 80, 200, 46)
    btn_col_l = pygame.Rect(W // 2 - 140, 430,     40, 40)
    btn_col_r = pygame.Rect(W // 2 + 100, 430,     40, 40)
    btn_dif_l = pygame.Rect(W // 2 - 140, 510,     40, 40)
    btn_dif_r = pygame.Rect(W // 2 + 100, 510,     40, 40)

    # Slider rects
    SL_W = 200
    sl_music = pygame.Rect(W // 2 - 100, 220, SL_W, 14)
    sl_sfx   = pygame.Rect(W // 2 - 100, 300, SL_W, 14)

    col_idx  = CAR_COLORS.index(settings.get("car_color", "default"))
    dif_idx  = DIFFICULTIES.index(settings.get("difficulty", "normal"))
    dragging = None   # 'music' | 'sfx' | None

    def _val_from_x(x):
        return max(0, min(100, int((x - sl_music.x) / SL_W * 100)))

    while True:
        _road_bg(screen)
        _title(screen, "SETTINGS", 60, 58)

        sf = _font(28)
        cf = _font(26)

        # ── Music volume ──
        _draw_volume_slider(screen, "Music Volume", sl_music,
                            settings["music_volume"], C_ACCENT)

        # ── SFX volume ──
        _draw_volume_slider(screen, "SFX Volume", sl_sfx,
                            settings["sfx_volume"], C_GREEN)

        # ── Car color ──
        screen.blit(sf.render("Car Color:", True, C_GREY), (W // 2 - 140, 400))
        cur_col = CAR_COLORS[col_idx]
        _draw_button(screen, btn_col_l, "<", False, font_size=26)
        _draw_button(screen, btn_col_r, ">", False, font_size=26)
        ctxt = cf.render(cur_col.upper(), True, COLOR_DISPLAY[cur_col])
        screen.blit(ctxt, ctxt.get_rect(centerx=W // 2, centery=btn_col_l.centery))

        # ── Difficulty ──
        screen.blit(sf.render("Difficulty:", True, C_GREY), (W // 2 - 140, 480))
        cur_dif = DIFFICULTIES[dif_idx]
        _draw_button(screen, btn_dif_l, "<", False, font_size=26)
        _draw_button(screen, btn_dif_r, ">", False, font_size=26)
        dif_colors = {"easy": C_GREEN, "normal": C_ACCENT, "hard": C_RED}
        dtxt = cf.render(cur_dif.upper(), True, dif_colors[cur_dif])
        screen.blit(dtxt, dtxt.get_rect(centerx=W // 2, centery=btn_dif_l.centery))

        mx, my = pygame.mouse.get_pos()
        _draw_button(screen, btn_back, "< BACK", btn_back.collidepoint(mx, my),
                     active_bg=C_ACCENT, active_fg=C_BG)

        # Drag feedback
        if dragging == 'music':
            settings["music_volume"] = _val_from_x(mx)
        elif dragging == 'sfx':
            settings["sfx_volume"] = _val_from_x(mx)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                save_settings(settings)
                return settings
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                # Expand hit area for sliders
                sl_music_hit = sl_music.inflate(0, 20)
                sl_sfx_hit   = sl_sfx.inflate(0, 20)
                if sl_music_hit.collidepoint(pos):
                    dragging = 'music'
                    settings["music_volume"] = _val_from_x(pos[0])
                elif sl_sfx_hit.collidepoint(pos):
                    dragging = 'sfx'
                    settings["sfx_volume"] = _val_from_x(pos[0])
                elif btn_col_l.collidepoint(pos):
                    col_idx = (col_idx - 1) % len(CAR_COLORS)
                    settings["car_color"] = CAR_COLORS[col_idx]
                elif btn_col_r.collidepoint(pos):
                    col_idx = (col_idx + 1) % len(CAR_COLORS)
                    settings["car_color"] = CAR_COLORS[col_idx]
                elif btn_dif_l.collidepoint(pos):
                    dif_idx = (dif_idx - 1) % len(DIFFICULTIES)
                    settings["difficulty"] = DIFFICULTIES[dif_idx]
                elif btn_dif_r.collidepoint(pos):
                    dif_idx = (dif_idx + 1) % len(DIFFICULTIES)
                    settings["difficulty"] = DIFFICULTIES[dif_idx]
                elif btn_back.collidepoint(pos):
                    save_settings(settings)
                    return settings
            if event.type == MOUSEBUTTONUP and event.button == 1:
                dragging = None

        clock.tick(60)


# ── Leaderboard Screen ────────────────────────────────────────────────────────

def show_leaderboard(screen: pygame.Surface, clock: pygame.time.Clock):
    """Blocking leaderboard screen."""
    W, H    = screen.get_size()
    board   = load_leaderboard()
    btn_back = pygame.Rect(W // 2 - 100, H - 80, 200, 46)
    RANK_COLORS = [(255, 215, 0), (192, 192, 192), (205, 127, 50)]  # gold / silver / bronze

    while True:
        _road_bg(screen)
        _title(screen, "TOP SCORES", 40, 52)

        if not board:
            _subtitle(screen, "No scores yet. Play a game!", H // 2, 30, C_GREY)
        else:
            header_f = _font(24)
            row_f    = _font(28)
            y0       = 110
            row_h    = 46
            # Header
            for col_x, col_lbl in [(55, "#"), (120, "NAME"), (340, "SCORE"), (440, "DIST")]:
                ht = header_f.render(col_lbl, True, C_GREY)
                screen.blit(ht, (col_x, y0))
            pygame.draw.line(screen, C_GREY, (40, y0 + 28), (W - 40, y0 + 28), 1)

            for i, entry in enumerate(board[:10]):
                y     = y0 + 36 + i * row_h
                bg_c  = (28, 32, 46) if i % 2 == 0 else (22, 26, 38)
                pygame.draw.rect(screen, bg_c, (40, y, W - 80, row_h - 2), border_radius=6)

                rank_c = RANK_COLORS[i] if i < 3 else C_WHITE
                rank_t = row_f.render(f"{i+1}", True, rank_c)
                name_t = row_f.render(entry.get("name", "?")[:14], True, C_WHITE)
                scr_t  = row_f.render(str(entry.get("score", 0)), True, C_ACCENT)
                dist_t = row_f.render(f"{entry.get('distance', 0)}m", True, C_GREY)

                screen.blit(rank_t, (55,  y + 8))
                screen.blit(name_t, (120, y + 8))
                screen.blit(scr_t,  (340, y + 8))
                screen.blit(dist_t, (440, y + 8))

        mx, my = pygame.mouse.get_pos()
        _draw_button(screen, btn_back, "◀  BACK", btn_back.collidepoint(mx, my),
                     active_bg=C_ACCENT, active_fg=C_BG)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                return
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if btn_back.collidepoint(event.pos):
                    return

        clock.tick(60)


# ── Game Over Screen ──────────────────────────────────────────────────────────

def show_game_over(screen: pygame.Surface, clock: pygame.time.Clock,
                   score: int, distance: int, coins: int, level: int) -> str:
    """
    Blocking game-over screen.
    Returns 'retry' | 'menu'
    """
    W, H     = screen.get_size()
    btn_retry = pygame.Rect(W // 2 - 150, 460, 130, 50)
    btn_menu  = pygame.Rect(W // 2 + 20,  460, 130, 50)

    while True:
        _road_bg(screen)

        # Dim overlay
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        screen.blit(overlay, (0, 0))

        _title(screen, "GAME OVER", 100, 72, C_RED)

        panel = pygame.Rect(W // 2 - 180, 210, 360, 220)
        _draw_rounded_rect(screen, C_PANEL, panel, 16)
        pygame.draw.rect(screen, C_ACCENT, panel, 2, border_radius=16)

        sf = _font(30)
        stats = [
            ("Score",    str(score),       C_ACCENT),
            ("Distance", f"{distance} m",  C_BLUE),
            ("Coins",    str(coins),        (255, 215, 0)),
            ("Level",    str(level),        C_GREEN),
        ]
        for i, (lbl, val, col) in enumerate(stats):
            y   = panel.y + 22 + i * 50
            lt  = sf.render(lbl + ":", True, C_GREY)
            vt  = sf.render(val,       True, col)
            screen.blit(lt, (panel.x + 20,  y))
            screen.blit(vt, (panel.right - vt.get_width() - 20, y))

        mx, my = pygame.mouse.get_pos()
        _draw_button(screen, btn_retry, "RETRY",     btn_retry.collidepoint(mx, my),
                     active_bg=C_GREEN,  active_fg=C_BG)
        _draw_button(screen, btn_menu,  "MENU",      btn_menu.collidepoint(mx, my),
                     active_bg=C_ACCENT, active_fg=C_BG)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_SPACE:  return "retry"
                if event.key == K_ESCAPE: return "menu"
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if btn_retry.collidepoint(event.pos): return "retry"
                if btn_menu.collidepoint(event.pos):  return "menu"

        clock.tick(60)