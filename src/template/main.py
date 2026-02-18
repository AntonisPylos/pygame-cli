from game import Game
import asyncio

WINDOW_SIZE = (600, 600)
MAX_FPS = 60


async def main():
    game = Game(WINDOW_SIZE, MAX_FPS)
    await game.run()


if __name__ == "__main__":
    asyncio.run(main())
