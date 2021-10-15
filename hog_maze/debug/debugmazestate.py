import pygame
import hog_maze.settings as settings


class DebugMazeState(object):
    def __init__(self):
        self.font = pygame.font.Font(None, 30)
        self.text = None
        self.text_list = []

    def update(self, vertex, seed):
        self.text = vertex.text_state(seed)
        self.text_list = []
        lines = self.text.splitlines()
        for l in lines:
            self.text_list.append(self.font.render(
                l, True, settings.BLACK, settings.WHITE))
