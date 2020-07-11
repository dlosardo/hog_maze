import pygame
import hog_maze.settings as settings


class DebugMouse(object):
    def __init__(self):
        self.font = pygame.font.Font(None, 24)
        self.text = None

    def update(self, mousex, mousey):
        xy = "Mouse X: {} Mouse Y: {}".format(
            mousex, mousey)
        self.text = self.font.render(
            xy, True, settings.BLACK, settings.WHITE)
