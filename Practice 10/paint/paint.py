import pygame
pygame.init()

WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint")

# Colors
PINK         = (255, 192, 203)
PURPLE       = (160, 32, 240)
RED          = (200, 0, 0)
GREEN        = (0, 200, 0)
BLUE         = (0, 0, 200)
WHITE        = (255, 255, 255)
ERASER_COLOR = PINK

PEN_RADIUS = 7
font = pygame.font.Font(None, 20)

# We store color, mode, and drawing state in a dictionary.
# This way we can change them anywhere in the code without 'global' issues.
state = {
    "color":     PURPLE,
    "mode":      "pen",
    "drawing":   False,
    "start_pos": None,
}

# We draw on a separate surface so buttons always stay visible on top
canvas = pygame.Surface((WIDTH, HEIGHT))
canvas.fill(PINK)

# Buttons on the left side
button_rects = {
    "Red":    pygame.Rect(10, 10,  70, 30),
    "Green":  pygame.Rect(10, 50,  70, 30),
    "Blue":   pygame.Rect(10, 90,  70, 30),
    "Eraser": pygame.Rect(10, 130, 70, 30),
    "Circle": pygame.Rect(10, 170, 70, 30),
    "Rect":   pygame.Rect(10, 210, 70, 30),
    "Clear":  pygame.Rect(10, 250, 70, 30),
}

def draw_buttons():
    for name, rect in button_rects.items():
        # Highlight the active button with a filled purple background
        active = (
            (name == "Red"    and state["color"] == RED   and state["mode"] == "pen") or
            (name == "Green"  and state["color"] == GREEN and state["mode"] == "pen") or
            (name == "Blue"   and state["color"] == BLUE  and state["mode"] == "pen") or
            (name == "Eraser" and state["mode"] == "eraser") or
            (name == "Circle" and state["mode"] == "circle") or
            (name == "Rect"   and state["mode"] == "rectangle")
        )
        if active:
            pygame.draw.rect(screen, PURPLE, rect)
            label = font.render(name, True, WHITE)
        else:
            pygame.draw.rect(screen, WHITE, rect)
            pygame.draw.rect(screen, PURPLE, rect, 2)
            label = font.render(name, True, PURPLE)
        screen.blit(label, (rect.x + 8, rect.y + 8))

def get_button_clicked(pos):
    for name, rect in button_rects.items():
        if rect.collidepoint(pos):
            return name
    return None

def is_on_button(pos):
    # Returns True if the position is inside any button
    for rect in button_rects.values():
        if rect.collidepoint(pos):
            return True
    return False

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                clicked = get_button_clicked(event.pos)
                # Change color or mode depending on which button was clicked
                if clicked == "Red":
                    state["color"] = RED
                    state["mode"]  = "pen"
                elif clicked == "Green":
                    state["color"] = GREEN
                    state["mode"]  = "pen"
                elif clicked == "Blue":
                    state["color"] = BLUE
                    state["mode"]  = "pen"
                elif clicked == "Eraser":
                    state["mode"] = "eraser"
                elif clicked == "Circle":
                    state["mode"] = "circle"
                elif clicked == "Rect":
                    state["mode"] = "rectangle"
                elif clicked == "Clear":
                    canvas.fill(PINK)
                else:
                    # Start drawing only if user clicked outside the buttons
                    state["start_pos"] = event.pos
                    state["drawing"]   = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if state["drawing"] and state["start_pos"] is not None:
                    end_pos = event.pos
                    # Draw the final shape on the canvas when mouse is released
                    if state["mode"] == "rectangle":
                        x = min(state["start_pos"][0], end_pos[0])
                        y = min(state["start_pos"][1], end_pos[1])
                        w = abs(end_pos[0] - state["start_pos"][0])
                        h = abs(end_pos[1] - state["start_pos"][1])
                        pygame.draw.rect(canvas, state["color"], (x, y, w, h), 2)
                    elif state["mode"] == "circle":
                        cx = (state["start_pos"][0] + end_pos[0]) // 2
                        cy = (state["start_pos"][1] + end_pos[1]) // 2
                        r  = max(abs(end_pos[0] - state["start_pos"][0]),
                                 abs(end_pos[1] - state["start_pos"][1])) // 2
                        pygame.draw.circle(canvas, state["color"], (cx, cy), r, 2)
                state["drawing"]   = False
                state["start_pos"] = None

        elif event.type == pygame.MOUSEMOTION:
            if state["drawing"]:
                x, y = event.pos
                # Pen and eraser draw continuously while the mouse moves
                if state["mode"] == "pen" and not is_on_button((x, y)):
                    pygame.draw.circle(canvas, state["color"], (x, y), PEN_RADIUS)
                elif state["mode"] == "eraser" and not is_on_button((x, y)):
                    pygame.draw.circle(canvas, ERASER_COLOR, (x, y), PEN_RADIUS)

    # Draw canvas first, then buttons on top so they are always visible
    screen.blit(canvas, (0, 0))

    # Show a live preview of the shape while the user is dragging
    if state["drawing"] and state["start_pos"] and state["mode"] in ("rectangle", "circle"):
        cur = pygame.mouse.get_pos()
        if state["mode"] == "rectangle":
            x = min(state["start_pos"][0], cur[0])
            y = min(state["start_pos"][1], cur[1])
            w = abs(cur[0] - state["start_pos"][0])
            h = abs(cur[1] - state["start_pos"][1])
            pygame.draw.rect(screen, state["color"], (x, y, w, h), 2)
        elif state["mode"] == "circle":
            cx = (state["start_pos"][0] + cur[0]) // 2
            cy = (state["start_pos"][1] + cur[1]) // 2
            r  = max(abs(cur[0] - state["start_pos"][0]),
                     abs(cur[1] - state["start_pos"][1])) // 2
            pygame.draw.circle(screen, state["color"], (cx, cy), r, 2)

    draw_buttons()
    pygame.display.flip()

pygame.quit()