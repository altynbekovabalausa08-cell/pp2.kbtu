import pygame


class MovingBallGame:
    def __init__(self):
        pygame.init()

        self.width = 700
        self.height = 500
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Moving Ball Game")

        self.clock = pygame.time.Clock()
        self.running = True

        self.white = (255, 255, 255)
        self.red = (220, 40, 40)
        self.black = (20, 20, 20)

        self.radius = 25
        self.step = 20

        self.x = self.width // 2
        self.y = self.height // 2

        self.font = pygame.font.SysFont("arial", 24)

    def move_ball(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy

        if self.radius <= new_x <= self.width - self.radius:
            self.x = new_x

        if self.radius <= new_y <= self.height - self.radius:
            self.y = new_y

    def draw(self):
        self.screen.fill(self.white)

        pygame.draw.circle(self.screen, self.red, (self.x, self.y), self.radius)

        info = self.font.render("Use arrow keys to move the ball. Each move = 20 px", True, self.black)
        self.screen.blit(info, (20, 20))

        coords = self.font.render(f"Position: ({self.x}, {self.y})", True, self.black)
        self.screen.blit(coords, (20, 55))

        pygame.display.flip()

    def handle_keydown(self, key):
        if key == pygame.K_UP:
            self.move_ball(0, -self.step)
        elif key == pygame.K_DOWN:
            self.move_ball(0, self.step)
        elif key == pygame.K_LEFT:
            self.move_ball(-self.step, 0)
        elif key == pygame.K_RIGHT:
            self.move_ball(self.step, 0)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event.key)

    def run(self):
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(60)

        pygame.quit()