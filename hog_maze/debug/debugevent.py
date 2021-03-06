import pygame
from pygame.locals import (
    QUIT, KEYDOWN, KEYUP, K_UP, K_DOWN,
    K_LEFT, K_RIGHT, MOUSEMOTION,
    MOUSEBUTTONUP
)
import hog_maze.settings as settings


class DebugEvent(object):
    def __init__(self):
        self.font = pygame.font.Font(None, 24)
        self.text = None

    def update(self, event):
        key = None
        if event.type in (KEYUP, KEYDOWN):
            key = event.key
        t = "Event: {}, {}".format(
            pygame.event.event_name(event.type), key)
        self.text = self.font.render(
            t, True, settings.BLACK, settings.WHITE)
