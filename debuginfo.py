import pygame
import settings


class DebugInfo(object):
    def __init__(self):
        self.font = pygame.font.Font(None, 24)
        self.text = None

    def update(self, player, ticks):
        xy = "X: {} Y: {}".format(player.rect.x,
                                  player.rect.y)
        # self.text = self.font.render(
            # "{}, Facing: {}, Ticks: {}".format(
                # xy, player.is_facing, ticks),
            # True, settings.BLACK, settings.WHITE)
        self.text = self.font.render(
            "left: {}, right: {}, up: {}, down: {}".format(
                player.key_dict['left'],
                player.key_dict['right'],
                player.key_dict['up'],
                player.key_dict['down']),
            True, settings.BLACK, settings.WHITE)
