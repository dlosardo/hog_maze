import pygame
import settings


class DebugInfo(object):
    def __init__(self):
        self.font = pygame.font.Font(None, 24)
        self.text = None

    def update(self, player, ticks):
        xy = "X: {} Y: {}".format(player.x,
                                  player.y)
        # self.text = self.font.render(
            # "{}, Facing: {}, Ticks: {}".format(
                # xy, "",
                # # player.is_facing,
                # ticks),
            # True, settings.BLACK, settings.WHITE)
        self.text = self.font.render(
            "left: {}, right: {}, up: {}, down: {}, tomatoes: {}\nxy: {}".format(
                player.component_dict['PLAYER_INPUT'].key_dict['left'],
                player.component_dict['PLAYER_INPUT'].key_dict['right'],
                player.component_dict['PLAYER_INPUT'].key_dict['up'],
                player.component_dict['PLAYER_INPUT'].key_dict['down'],
                player.get_state('INVENTORY').inventory.get('tomato'),
            xy),
            True, settings.BLACK, settings.WHITE)
