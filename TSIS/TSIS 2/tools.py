import pygame
from collections import deque

# Flood fill using BFS — fills area with selected color starting from click point
def flood_fill(surface, x, y, new_color):
    target_color = surface.get_at((x, y))[:3]
    new_color = new_color[:3]
    if target_color == new_color:
        return

    width, height = surface.get_size()
    queue = deque([(x, y)])
    visited = set()

    while queue:
        cx, cy = queue.popleft()
        if (cx, cy) in visited:
            continue
        if cx < 0 or cy < 0 or cx >= width or cy >= height:
            continue
        if surface.get_at((cx, cy))[:3] != target_color:
            continue
        surface.set_at((cx, cy), new_color)
        visited.add((cx, cy))
        queue.extend([(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)])