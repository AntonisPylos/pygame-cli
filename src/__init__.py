import pygame

if not getattr(pygame, "IS_CE", False):
    raise ImportError(
        "Pygame-CLI requires the Pygame Community Edition (pygame-ce). "
        "Please install it and ensure you are not using legacy pygame."
    )
