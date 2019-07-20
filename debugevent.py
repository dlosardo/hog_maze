import pygame
from pygame.locals import (
    QUIT, KEYDOWN, KEYUP, K_UP, K_DOWN,
    K_LEFT, K_RIGHT, MOUSEMOTION,
    MOUSEBUTTONUP
)
import settings


class DebugEvent(object):
    def __init__(self):
        self.font = pygame.font.Font(None, 24)
        self.text = None

    def update(self, event):
        key = None
        if event.type in (KEYUP, KEYDOWN):
            key = event.key
        t = "Event: {}, {}".format(
            event.type, key)
        self.text = self.font.render(
            t, True, settings.BLACK, settings.WHITE)
