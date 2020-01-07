import pygame
import settings


class DebugInfo(object):
    def __init__(self):
        self.font = pygame.font.Font(None, 24)
        self.text = None
        self.text_list = []

    def update(self, sprite, ticks):
        self.text_list = []
        xy = "X: {} Y: {}".format(sprite.x,
                                  sprite.y)
        if sprite.name_object == 'hoggy':
            self.text_list.append(self.font.render(
                "left: {}, right: {}, up: {}, down: {}, tomatoes: {}\nxy: {}".format(
                    sprite.component_dict['PLAYER_INPUT'].key_dict['left'],
                    sprite.component_dict['PLAYER_INPUT'].key_dict['right'],
                    sprite.component_dict['PLAYER_INPUT'].key_dict['up'],
                    sprite.component_dict['PLAYER_INPUT'].key_dict['down'],
                    sprite.get_state('INVENTORY').inventory.get('tomato'),
                    xy),
                True, settings.BLACK, settings.WHITE))
        elif sprite.name_object == 'ai_hoggy':
            current_vertex = sprite.get_state('MAZE').current_vertex
            sprite_with_tomato = "None"
            if current_vertex.sprite_with_tomato:
                sprite_with_tomato = current_vertex.sprite_with_tomato.name_object
            text = "rewards: {}, tomatoes: {}\nxy: {}\nWALL NORTH: {},"\
                    "WALL SOUTH: {}, WALL EAST: {} WALL WEST: {}\n"\
                    "HAS TOMATO: {}, SPRITE WITH TOMATO: {}".format(
                        sprite.get_state('MAZE').rewards,
                        sprite.get_state('INVENTORY').inventory.get('tomato'),
                        xy, current_vertex.north_wall, current_vertex.south_wall,
                        current_vertex.east_wall, current_vertex.west_wall,
                        current_vertex.has_tomato,
                        sprite_with_tomato)
            lines = text.splitlines()
            for l in lines:
                self.text_list.append(self.font.render(
                    l, True, settings.BLACK, settings.WHITE))
