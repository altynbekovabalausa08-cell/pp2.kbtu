import pygame
import math

pygame.init()

# ── Window ─────────────────────────────────────────────────────────────────────
WIDTH  = 900    # wider than original to fit the extra buttons
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint")

# ── Colours ────────────────────────────────────────────────────────────────────
PINK         = (255, 192, 203)
PURPLE       = (160,  32, 240)
RED          = (200,   0,   0)
GREEN        = (0,   200,   0)
BLUE         = (0,     0, 200)
WHITE        = (255, 255, 255)
ERASER_COLOR = PINK          # the eraser paints in the canvas background colour

PEN_RADIUS = 7
font       = pygame.font.Font(None, 18)

# ── Application state ──────────────────────────────────────────────────────────
# Using a dictionary avoids the need for global variables throughout the code.
state = {
    "color":     PURPLE,   # active drawing colour
    "mode":      "pen",    # active tool / shape mode
    "drawing":   False,    # True while the mouse button is held down
    "start_pos": None,     # where the mouse was pressed (for shapes)
}

# The canvas is a separate surface so buttons always stay on top of the drawing.
canvas = pygame.Surface((WIDTH, HEIGHT))
canvas.fill(PINK)

# ── Buttons ────────────────────────────────────────────────────────────────────
# Buttons are placed in a vertical strip on the left side of the screen.
# Each key is a human-readable label; each value is a pygame.Rect.
button_rects = {
    # Colour pickers
    "Red":       pygame.Rect(10, 10,  80, 28),
    "Green":     pygame.Rect(10, 46,  80, 28),
    "Blue":      pygame.Rect(10, 82,  80, 28),
    # Tools
    "Eraser":    pygame.Rect(10, 118, 80, 28),
    # Original shapes
    "Circle":    pygame.Rect(10, 154, 80, 28),
    "Rect":      pygame.Rect(10, 190, 80, 28),
    # New shapes (Practice 9 additions)
    "Square":    pygame.Rect(10, 226, 80, 28),
    "RTriangle": pygame.Rect(10, 262, 80, 28),  # right triangle
    "EqTriangle":pygame.Rect(10, 298, 80, 28),  # equilateral triangle
    "Rhombus":   pygame.Rect(10, 334, 80, 28),
    # Utility
    "Clear":     pygame.Rect(10, 370, 80, 28),
}

# Map button labels to the mode string they activate
BUTTON_MODE_MAP = {
    "Circle":     "circle",
    "Rect":       "rectangle",
    "Square":     "square",
    "RTriangle":  "right_triangle",
    "EqTriangle": "eq_triangle",
    "Rhombus":    "rhombus",
    "Eraser":     "eraser",
}

# Map button labels to the colour they set
BUTTON_COLOR_MAP = {
    "Red":   RED,
    "Green": GREEN,
    "Blue":  BLUE,
}


# ── Helper: draw all buttons ───────────────────────────────────────────────────
def draw_buttons():
    """Render all toolbar buttons; highlight the currently active one."""
    for name, rect in button_rects.items():
        # Decide whether this button represents the currently active tool/colour
        active = False
        if name in BUTTON_COLOR_MAP:
            active = (
                state["mode"] == "pen"
                and state["color"] == BUTTON_COLOR_MAP[name]
            )
        elif name in BUTTON_MODE_MAP:
            active = (state["mode"] == BUTTON_MODE_MAP[name])

        if active:
            # Filled purple background for the selected button
            pygame.draw.rect(screen, PURPLE, rect)
            label = font.render(name, True, WHITE)
        else:
            pygame.draw.rect(screen, WHITE, rect)
            pygame.draw.rect(screen, PURPLE, rect, 2)   # purple border
            label = font.render(name, True, PURPLE)

        screen.blit(label, (rect.x + 4, rect.y + 8))


# ── Helper: hit-test buttons ───────────────────────────────────────────────────
def get_button_clicked(pos):
    """Return the name of the button at pos, or None if none was clicked."""
    for name, rect in button_rects.items():
        if rect.collidepoint(pos):
            return name
    return None


def is_on_button(pos):
    """True if pos overlaps any button (used to prevent drawing under toolbar)."""
    return any(rect.collidepoint(pos) for rect in button_rects.values())


# ── Shape drawing helpers ──────────────────────────────────────────────────────

def draw_square(surface, color, start, end, width=2):
    """
    Draw a square whose one side is defined by the drag length.
    The side length is the larger of dx and dy so the square is always visible.
    """
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    # Use the longer axis as the side length, preserve sign for direction
    side = max(abs(dx), abs(dy))
    x = start[0]
    y = start[1]
    # Keep the square in the drag direction
    w = side if dx >= 0 else -side
    h = side if dy >= 0 else -side
    # Normalise so x,y is the top-left corner
    rx = min(x, x + w)
    ry = min(y, y + h)
    pygame.draw.rect(surface, color, pygame.Rect(rx, ry, side, side), width)


def draw_right_triangle(surface, color, start, end, width=2):
    """
    Draw a right-angle triangle.
    The right angle is at start, with the two legs going to
    (end[0], start[1]) and (start[0], end[1]).
    """
    p1 = start                        # right-angle vertex
    p2 = (end[0],   start[1])         # horizontal leg end
    p3 = (start[0], end[1])           # vertical leg end
    pygame.draw.polygon(surface, color, [p1, p2, p3], width)


def draw_eq_triangle(surface, color, start, end, width=2):
    """
    Draw an equilateral triangle.
    The base runs from start to (end[0], start[1]); the apex is above the
    midpoint at a height of base * sqrt(3) / 2.
    """
    x1, y1 = start
    x2      = end[0]
    base    = x2 - x1

    # Mid-point of the base
    mx = (x1 + x2) / 2
    # Height of an equilateral triangle
    h  = abs(base) * (math.sqrt(3) / 2)

    # Apex is above (or below, depending on drag direction) the base midpoint
    apex_y = y1 - h if end[1] <= start[1] else y1 + h

    p1 = (x1, y1)
    p2 = (x2, y1)
    p3 = (mx, apex_y)
    pygame.draw.polygon(surface, color, [p1, p2, p3], width)


def draw_rhombus(surface, color, start, end, width=2):
    """
    Draw a rhombus (diamond shape) defined by its bounding rectangle.
    The four vertices are the mid-points of the bounding box's sides.
    """
    x = min(start[0], end[0])
    y = min(start[1], end[1])
    w = abs(end[0] - start[0])
    h = abs(end[1] - start[1])
    if w == 0 or h == 0:
        return   # degenerate – nothing to draw

    top    = (x + w // 2, y)         # top vertex
    right  = (x + w,      y + h // 2)
    bottom = (x + w // 2, y + h)     # bottom vertex
    left   = (x,           y + h // 2)
    pygame.draw.polygon(surface, color, [top, right, bottom, left], width)


# ── Unified shape dispatcher ───────────────────────────────────────────────────

def draw_shape(surface, mode, color, start, end, width=2):
    """Dispatch a finalised shape draw to the correct helper function."""
    if mode == "rectangle":
        x = min(start[0], end[0])
        y = min(start[1], end[1])
        w = abs(end[0] - start[0])
        h = abs(end[1] - start[1])
        pygame.draw.rect(surface, color, (x, y, w, h), width)
    elif mode == "circle":
        cx = (start[0] + end[0]) // 2
        cy = (start[1] + end[1]) // 2
        r  = max(abs(end[0] - start[0]), abs(end[1] - start[1])) // 2
        pygame.draw.circle(surface, color, (cx, cy), r, width)
    elif mode == "square":
        draw_square(surface, color, start, end, width)
    elif mode == "right_triangle":
        draw_right_triangle(surface, color, start, end, width)
    elif mode == "eq_triangle":
        draw_eq_triangle(surface, color, start, end, width)
    elif mode == "rhombus":
        draw_rhombus(surface, color, start, end, width)


# Set of modes that require drag-to-define (not free-hand drawing)
SHAPE_MODES = {"rectangle", "circle", "square",
               "right_triangle", "eq_triangle", "rhombus"}

# ── Main loop ──────────────────────────────────────────────────────────────────
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:   # left click only
                clicked = get_button_clicked(event.pos)

                if clicked in BUTTON_COLOR_MAP:
                    # Switch to pen mode with the chosen colour
                    state["color"] = BUTTON_COLOR_MAP[clicked]
                    state["mode"]  = "pen"
                elif clicked in BUTTON_MODE_MAP:
                    # Switch to the tool/shape associated with this button
                    state["mode"] = BUTTON_MODE_MAP[clicked]
                elif clicked == "Clear":
                    canvas.fill(PINK)    # wipe the canvas
                elif clicked is None:
                    # Click was outside the toolbar – start drawing / placing shape
                    state["start_pos"] = event.pos
                    state["drawing"]   = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and state["drawing"] and state["start_pos"]:
                end_pos = event.pos
                # Commit the shape to the permanent canvas on mouse release
                if state["mode"] in SHAPE_MODES:
                    draw_shape(canvas, state["mode"],
                               state["color"], state["start_pos"], end_pos)
                state["drawing"]   = False
                state["start_pos"] = None

        elif event.type == pygame.MOUSEMOTION:
            if state["drawing"]:
                x, y = event.pos
                # Pen and eraser paint continuously as the mouse moves
                if state["mode"] == "pen" and not is_on_button((x, y)):
                    pygame.draw.circle(canvas, state["color"], (x, y), PEN_RADIUS)
                elif state["mode"] == "eraser" and not is_on_button((x, y)):
                    pygame.draw.circle(canvas, ERASER_COLOR, (x, y), PEN_RADIUS)

    # ── Render ─────────────────────────────────────────────────────────────────
    # Draw the permanent canvas first, buttons on top
    screen.blit(canvas, (0, 0))

    # Live preview: show the shape outline while the user is dragging
    if state["drawing"] and state["start_pos"] and state["mode"] in SHAPE_MODES:
        cur = pygame.mouse.get_pos()
        draw_shape(screen, state["mode"], state["color"], state["start_pos"], cur)

    draw_buttons()
    pygame.display.flip()

pygame.quit()