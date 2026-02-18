import pygame
import asyncio


class Game:
    def __init__(self, size, fps):
        pygame.init()
        self.size = size
        self.max_fps = fps

    def start(self):
        self.display = pygame.display.set_mode(self.size)
        self.clock = pygame.time.Clock()
        self.fps = 0
        self.dt = 0
        self.running = True

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

        self.display.fill("yellow")

        pygame.display.flip()

        self.dt = self.clock.tick(self.max_fps) / 1000

    def exit(self):
        self.running = False

    async def run(self):
        self.start()
        while self.running:
            self.update()
            await asyncio.sleep(0)
        self.exit()
