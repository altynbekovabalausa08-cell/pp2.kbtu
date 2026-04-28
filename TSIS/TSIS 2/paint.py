import pygame
import sys
from datetime import datetime
from tools import flood_fill

pygame.init()

# Window and canvas setup
WIDTH, HEIGHT = 1100, 700
TOOLBAR_W = 160
CANVAS_X = TOOLBAR_W
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint App")

# Separate canvas surface — shapes are drawn here permanently
canvas = pygame.Surface((WIDTH - TOOLBAR_W, HEIGHT))
canvas.fill((255, 255, 255))

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 14)
font_big = pygame.font.SysFont("Arial", 20)

# Available colors shown as buttons in toolbar
COLORS = [
    (0,0,0), (255,255,255), (255,0,0), (0,200,0),
    (0,0,255), (255,165,0), (255,255,0), (128,0,128),
    (0,200,200), (255,105,180), (139,69,19), (128,128,128),
]

# Tool list
TOOLS = ["Pencil", "Line", "Rect", "Circle", "Fill", "Eraser", "Text",
         "Square", "R.Tri", "Eq.Tri", "Rhombus"]

# Brush sizes: small, medium, large
SIZES = [2, 5, 10]

# App state
state = {
    "tool": "Pencil",
    "color": (0, 0, 0),
    "size": 2,
    "drawing": False,
    "start": None,
    "prev": None,
    # text tool state
    "text_pos": None,
    "text_str": "",
    "text_active": False,
}

def draw_toolbar():
    pygame.draw.rect(screen, (230, 230, 230), (0, 0, TOOLBAR_W, HEIGHT))

    # Color buttons
    y = 10
    screen.blit(font.render("Colors:", True, (0,0,0)), (8, y))
    y += 20
    for i, c in enumerate(COLORS):
        x = 8 + (i % 4) * 36
        row = i // 4
        rect = pygame.Rect(x, y + row * 36, 30, 30)
        pygame.draw.rect(screen, c, rect)
        pygame.draw.rect(screen, (0,0,0), rect, 2)
        # highlight selected color
        if c == state["color"]:
            pygame.draw.rect(screen, (255,255,0), rect, 3)

    y += (len(COLORS) // 4) * 36 + 10

    # Tool buttons
    screen.blit(font.render("Tools:", True, (0,0,0)), (8, y))
    y += 20
    for tool in TOOLS:
        rect = pygame.Rect(8, y, TOOLBAR_W - 16, 26)
        # highlight active tool
        color = (100, 149, 237) if tool == state["tool"] else (200, 200, 200)
        pygame.draw.rect(screen, color, rect, border_radius=4)
        pygame.draw.rect(screen, (0,0,0), rect, 1, border_radius=4)
        screen.blit(font.render(tool, True, (0,0,0)), (rect.x + 6, rect.y + 6))
        y += 30

    # Brush size buttons — 1, 2, 3 keys or click
    screen.blit(font.render("Size (1/2/3):", True, (0,0,0)), (8, y))
    y += 20
    labels = ["S", "M", "L"]
    for i, (sz, lb) in enumerate(zip(SIZES, labels)):
        rect = pygame.Rect(8 + i * 48, y, 40, 26)
        color = (100, 149, 237) if state["size"] == sz else (200, 200, 200)
        pygame.draw.rect(screen, color, rect, border_radius=4)
        pygame.draw.rect(screen, (0,0,0), rect, 1, border_radius=4)
        screen.blit(font.render(lb, True, (0,0,0)), (rect.x + 14, rect.y + 6))
    y += 36

    # Clear canvas button
    rect = pygame.Rect(8, y, TOOLBAR_W - 16, 30)
    pygame.draw.rect(screen, (220, 80, 80), rect, border_radius=4)
    pygame.draw.rect(screen, (0,0,0), rect, 1, border_radius=4)
    screen.blit(font.render("Clear All", True, (255,255,255)), (rect.x + 20, rect.y + 8))

    # Ctrl+S hint
    screen.blit(font.render("Ctrl+S = Save", True, (80,80,80)), (8, HEIGHT - 24))

def get_toolbar_click(mx, my):
    """Check what toolbar element was clicked, return action string or None."""
    # Color buttons
    y = 30
    for i, c in enumerate(COLORS):
        x = 8 + (i % 4) * 36
        row = i // 4
        rect = pygame.Rect(x, y + row * 36, 30, 30)
        if rect.collidepoint(mx, my):
            return ("color", c)

    y += (len(COLORS) // 4) * 36 + 30
    for tool in TOOLS:
        rect = pygame.Rect(8, y, TOOLBAR_W - 16, 26)
        if rect.collidepoint(mx, my):
            return ("tool", tool)
        y += 30

    # Size buttons
    y2 = y + 20
    for i, sz in enumerate(SIZES):
        rect = pygame.Rect(8 + i * 48, y2, 40, 26)
        if rect.collidepoint(mx, my):
            return ("size", sz)

    # Clear button
    rect = pygame.Rect(8, y2 + 36, TOOLBAR_W - 16, 30)
    if rect.collidepoint(mx, my):
        return ("clear", None)

    return None

def canvas_pos(mx, my):
    """Convert screen coords to canvas coords."""
    return mx - CANVAS_X, my

def draw_shape_preview(surface, tool, start, end, color, size):
    """Draw live preview of shape while dragging (before mouse release)."""
    x1, y1 = start
    x2, y2 = end
    if tool == "Line":
        pygame.draw.line(surface, color, start, end, size)
    elif tool == "Rect":
        rect = pygame.Rect(min(x1,x2), min(y1,y2), abs(x2-x1), abs(y2-y1))
        pygame.draw.rect(surface, color, rect, size)
    elif tool == "Circle":
        r = int(((x2-x1)**2 + (y2-y1)**2) ** 0.5)
        pygame.draw.circle(surface, color, start, r, size)
    elif tool == "Square":
        side = min(abs(x2-x1), abs(y2-y1))
        rect = pygame.Rect(x1, y1, side, side)
        pygame.draw.rect(surface, color, rect, size)
    elif tool == "R.Tri":
        # right angle at start point
        pts = [start, (x1, y2), (x2, y2)]
        pygame.draw.polygon(surface, color, pts, size)
    elif tool == "Eq.Tri":
        mid_x = (x1 + x2) // 2
        pts = [(mid_x, y1), (x1, y2), (x2, y2)]
        pygame.draw.polygon(surface, color, pts, size)
    elif tool == "Rhombus":
        mid_x = (x1 + x2) // 2
        mid_y = (y1 + y2) // 2
        pts = [(mid_x, y1), (x2, mid_y), (mid_x, y2), (x1, mid_y)]
        pygame.draw.polygon(surface, color, pts, size)

def save_canvas():
    """Save canvas as PNG with timestamp so files don't overwrite each other."""
    name = f"canvas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    pygame.image.save(canvas, name)
    print(f"Saved: {name}")

running = True
while running:
    clock.tick(60)
    mx, my = pygame.mouse.get_pos()
    on_canvas = mx >= CANVAS_X  # True if mouse is on drawing area

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Keyboard shortcuts
        if event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()

            # Ctrl+S to save
            if event.key == pygame.K_s and (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]):
                save_canvas()

            # Size shortcuts
            if event.key == pygame.K_1: state["size"] = SIZES[0]
            if event.key == pygame.K_2: state["size"] = SIZES[1]
            if event.key == pygame.K_3: state["size"] = SIZES[2]

            # Text tool input
            if state["text_active"]:
                if event.key == pygame.K_RETURN:
                    # Render text permanently onto canvas
                    surf = font_big.render(state["text_str"], True, state["color"])
                    canvas.blit(surf, state["text_pos"])
                    state["text_active"] = False
                    state["text_str"] = ""
                    state["text_pos"] = None
                elif event.key == pygame.K_ESCAPE:
                    state["text_active"] = False
                    state["text_str"] = ""
                    state["text_pos"] = None
                elif event.key == pygame.K_BACKSPACE:
                    state["text_str"] = state["text_str"][:-1]
                else:
                    state["text_str"] += event.unicode

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not on_canvas:
                # Toolbar click
                action = get_toolbar_click(mx, my)
                if action:
                    kind, val = action
                    if kind == "color":
                        state["color"] = val
                    elif kind == "tool":
                        state["tool"] = val
                        state["text_active"] = False
                    elif kind == "size":
                        state["size"] = val
                    elif kind == "clear":
                        canvas.fill((255, 255, 255))
            else:
                cx, cy = canvas_pos(mx, my)
                tool = state["tool"]

                if tool == "Fill":
                    flood_fill(canvas, cx, cy, state["color"])
                elif tool == "Text":
                    # Click sets text cursor position
                    state["text_pos"] = (cx, cy)
                    state["text_active"] = True
                    state["text_str"] = ""
                else:
                    state["drawing"] = True
                    state["start"] = (cx, cy)
                    state["prev"] = (cx, cy)

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if state["drawing"] and on_canvas:
                cx, cy = canvas_pos(mx, my)
                tool = state["tool"]
                # On release: draw shape permanently onto canvas
                if tool in ("Line", "Rect", "Circle", "Square", "R.Tri", "Eq.Tri", "Rhombus"):
                    draw_shape_preview(canvas, tool, state["start"], (cx, cy),
                                       state["color"], state["size"])
            state["drawing"] = False
            state["start"] = None
            state["prev"] = None

        if event.type == pygame.MOUSEMOTION:
            if state["drawing"] and on_canvas:
                cx, cy = canvas_pos(mx, my)
                tool = state["tool"]

                if tool == "Pencil":
                    # Draw line segment from last position to current — creates smooth freehand
                    pygame.draw.line(canvas, state["color"], state["prev"], (cx, cy), state["size"])
                    state["prev"] = (cx, cy)

                elif tool == "Eraser":
                    # Eraser draws white over canvas
                    pygame.draw.circle(canvas, (255,255,255), (cx, cy), state["size"] * 3)
                    state["prev"] = (cx, cy)

    # Draw everything
    screen.fill((200, 200, 200))
    screen.blit(canvas, (CANVAS_X, 0))

    # Live preview while dragging shape tools
    if state["drawing"] and state["tool"] in ("Line", "Rect", "Circle", "Square", "R.Tri", "Eq.Tri", "Rhombus"):
        cx, cy = canvas_pos(mx, my)
        # Draw preview on a temp copy so canvas stays clean until mouse release
        preview = canvas.copy()
        draw_shape_preview(preview, state["tool"], state["start"], (cx, cy),
                           state["color"], state["size"])
        screen.blit(preview, (CANVAS_X, 0))

    # Show live text while typing
    if state["text_active"] and state["text_pos"]:
        surf = font_big.render(state["text_str"] + "|", True, state["color"])
        screen.blit(surf, (CANVAS_X + state["text_pos"][0], state["text_pos"][1]))

    draw_toolbar()
    pygame.display.flip()

pygame.quit()
sys.exit()