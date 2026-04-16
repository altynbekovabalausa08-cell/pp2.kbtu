import math
from datetime import datetime
from pathlib import Path

import pygame


class MickeyClock:
    def __init__(self):
        pygame.init()

        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Mickey's Clock Application")

        self.clock = pygame.time.Clock()
        self.running = True

        self.center = (self.width // 2, self.height // 2)
        self.background_color = (245, 245, 245)
        self.black = (20, 20, 20)
        self.red = (220, 50, 50)
        self.blue = (70, 120, 220)

        self.base_path = Path(__file__).resolve().parent
        self.images_path = self.base_path / "images"

        self.font = pygame.font.SysFont("arial", 28)
        self.small_font = pygame.font.SysFont("arial", 22)

        self.clock_face = self.load_image("clock.png", (500, 500))
        self.right_hand = self.load_image("right_hand.png", (170, 35))
        self.left_hand = self.load_image("left_hand.png", (170, 35))

    def load_image(self, filename, size):
        """
        Tries to load an image.
        If image is missing, creates a simple fallback surface.
        """
        file_path = self.images_path / filename

        if file_path.exists():
            image = pygame.image.load(str(file_path)).convert_alpha()
            image = pygame.transform.smoothscale(image, size)
            return image

        # Fallback image so that the program still works without external files
        surface = pygame.Surface(size, pygame.SRCALPHA)

        if "clock" in filename:
            pygame.draw.circle(surface, (255, 255, 255), (size[0] // 2, size[1] // 2), min(size) // 2 - 10)
            pygame.draw.circle(surface, self.black, (size[0] // 2, size[1] // 2), min(size) // 2 - 10, 4)
            for i in range(12):
                angle = math.radians(i * 30 - 90)
                x1 = size[0] // 2 + int(math.cos(angle) * 190)
                y1 = size[1] // 2 + int(math.sin(angle) * 190)
                x2 = size[0] // 2 + int(math.cos(angle) * 220)
                y2 = size[1] // 2 + int(math.sin(angle) * 220)
                pygame.draw.line(surface, self.black, (x1, y1), (x2, y2), 4)
        else:
            # hand fallback
            color = self.red if "right" in filename else self.blue
            pygame.draw.rect(surface, color, (15, size[1] // 2 - 6, size[0] - 30, 12), border_radius=6)
            pygame.draw.circle(surface, self.black, (20, size[1] // 2), 12)
            pygame.draw.circle(surface, self.black, (size[0] - 15, size[1] // 2), 8)

        return surface

    def get_angles(self):
        """
        Returns current minute and second hand angles.
        """
        now = datetime.now()
        minutes = now.minute
        seconds = now.second

        minute_angle = -(minutes * 6 + seconds * 0.1)
        second_angle = -(seconds * 6)

        return minute_angle, second_angle, now

    def rotate_hand(self, image, angle):
        """
        Rotates a hand image around its center.
        """
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_rect = rotated_image.get_rect(center=self.center)
        return rotated_image, rotated_rect

    def draw_center_pin(self):
        pygame.draw.circle(self.screen, self.black, self.center, 10)
        pygame.draw.circle(self.screen, (240, 200, 0), self.center, 5)

    def draw_digital_time(self, now):
        """
        Draws digital text time in MM:SS format.
        """
        time_text = now.strftime("%M:%S")
        rendered = self.font.render(f"Current time: {time_text}", True, self.black)
        rect = rendered.get_rect(center=(self.width // 2, 40))
        self.screen.blit(rendered, rect)

    def draw_labels(self):
        """
        Draws explanatory labels for teacher/demo.
        """
        label1 = self.small_font.render("Right hand = minute hand", True, self.red)
        label2 = self.small_font.render("Left hand = second hand", True, self.blue)

        self.screen.blit(label1, (20, self.height - 70))
        self.screen.blit(label2, (20, self.height - 40))

    def draw(self):
        self.screen.fill(self.background_color)

        face_rect = self.clock_face.get_rect(center=self.center)
        self.screen.blit(self.clock_face, face_rect)

        minute_angle, second_angle, now = self.get_angles()

        rotated_right, right_rect = self.rotate_hand(self.right_hand, minute_angle)
        rotated_left, left_rect = self.rotate_hand(self.left_hand, second_angle)

        self.screen.blit(rotated_right, right_rect)
        self.screen.blit(rotated_left, left_rect)

        self.draw_center_pin()
        self.draw_digital_time(now)
        self.draw_labels()

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def run(self):
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(60)

        pygame.quit()