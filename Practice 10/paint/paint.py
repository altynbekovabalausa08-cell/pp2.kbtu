import pygame
pygame.init()

WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint")

# Colors we use in the app
PINK = (255, 192, 203)
PURPLE = (160, 32, 240)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 0, 200)
WHITE = (255, 255, 255)
ERASER_COLOR = PINK

pen_radius = 7
mode = 'pen'
color = PURPLE
drawing = False
start_pos = None

font = pygame.font.Font(None, 20)

# We draw on a separate surface (canvas), not on the screen directly.
# This fixes the bug: buttons stay visible even when user draws over them.
canvas = pygame.Surface((WIDTH, HEIGHT))
canvas.fill(PINK)

# Buttons placed on the left side
button_rects = {
    "Red":    pygame.Rect(10, 10, 70, 30),
    "Green":  pygame.Rect(10, 50, 70, 30),
    "Blue":   pygame.Rect(10, 90, 70, 30),
    "Eraser": pygame.Rect(10, 130, 70, 30),
    "Circle": pygame.Rect(10, 170, 70, 30),
    "Rect":   pygame.Rect(10, 210, 70, 30),
    "Clear":  pygame.Rect(10, 250, 70, 30),
}

def draw_buttons():
    for name, rect in button_rects.items():
        # Highlight the active button with filled purple
        active = (
            (name == "Red"    and color == RED    and mode == 'pen') or
            (name == "Green"  and color == GREEN  and mode == 'pen') or
            (name == "Blue"   and color == BLUE   and mode == 'pen') or
            (name == "Eraser" and mode == 'eraser') or
            (name == "Circle" and mode == 'circle') or
            (name == "Rect"   and mode == 'rectangle')
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
    # Returns True if the mouse is over any button
    for rect in button_rects.values():
        if rect.collidepoint(pos):
            return True
    return False

def clear_screen():
    canvas.fill(PINK)

flag = True
while flag:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            flag = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                clicked_button = get_button_clicked(event.pos)
                # Change color or mode based on which button is clicked
                if clicked_button == "Red":
                    color = RED
                    mode = 'pen'
                elif clicked_button == "Green":
                    color = GREEN
                    mode = 'pen'
                elif clicked_button == "Blue":
                    color = BLUE
                    mode = 'pen'
                elif clicked_button == "Eraser":
                    mode = 'eraser'
                elif clicked_button == "Circle":
                    mode = 'circle'
                elif clicked_button == "Rect":
                    mode = 'rectangle'
                elif clicked_button == "Clear":
                    clear_screen()
                else:
                    # Start drawing only if user clicked outside the buttons
                    start_pos = event.pos
                    drawing = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if drawing and start_pos is not None:
                    end_pos = event.pos
                    # Shapes are drawn on canvas when the mouse button is released
                    if mode == 'rectangle':
                        x = min(start_pos[0], end_pos[0])
                        y = min(start_pos[1], end_pos[1])
                        w = abs(end_pos[0] - start_pos[0])
                        h = abs(end_pos[1] - start_pos[1])
                        pygame.draw.rect(canvas, color, (x, y, w, h), 2)
                    elif mode == 'circle':
                        center = ((start_pos[0] + end_pos[0]) // 2,
                                  (start_pos[1] + end_pos[1]) // 2)
                        r = max(abs(end_pos[0] - start_pos[0]),
                                abs(end_pos[1] - start_pos[1])) // 2
                        pygame.draw.circle(canvas, color, center, r, 2)
                drawing = False
                start_pos = None

        elif event.type == pygame.MOUSEMOTION:
            if drawing:
                x, y = event.pos
                # Pen and eraser draw on canvas while mouse moves (not on buttons)
                if mode == 'pen' and not is_on_button((x, y)):
                    pygame.draw.circle(canvas, color, (x, y), pen_radius)
                elif mode == 'eraser' and not is_on_button((x, y)):
                    pygame.draw.circle(canvas, ERASER_COLOR, (x, y), pen_radius)

    # First draw the canvas (all user drawings), then buttons on top
    screen.blit(canvas, (0, 0))

    # Show a live preview of rectangle/circle while the user is still dragging
    if drawing and start_pos is not None and mode in ('rectangle', 'circle'):
        cur = pygame.mouse.get_pos()
        if mode == 'rectangle':
            x = min(start_pos[0], cur[0])
            y = min(start_pos[1], cur[1])
            w = abs(cur[0] - start_pos[0])
            h = abs(cur[1] - start_pos[1])
            pygame.draw.rect(screen, color, (x, y, w, h), 2)
        elif mode == 'circle':
            center = ((start_pos[0] + cur[0]) // 2,
                      (start_pos[1] + cur[1]) // 2)
            r = max(abs(cur[0] - start_pos[0]),
                    abs(cur[1] - start_pos[1])) // 2
            pygame.draw.circle(screen, color, center, r, 2)

    draw_buttons()
    pygame.display.flip()

pygame.quit()
