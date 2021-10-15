import hog_maze.settings as settings
import pygame
from hog_maze.game_states.hoggy_level_transition_state import (
    HoggyLevelTransitionState)
from hog_maze.util.util_draw import draw_text
import hog_maze.actor_obj as actor_obj
from hog_maze.components.clickable_component import ClickableComponent
from hog_maze.components.animation_component import AnimationComponent


class HoggyStartScreenState(HoggyLevelTransitionState):

    def __init__(self):
        super().__init__()

    def initialize_state(self):
        print("Initialize Start Screen State")
        self.world = pygame.display.set_mode((settings.WINDOW_WIDTH +
                                              settings.HUD_OFFSETX,
                                              settings.WINDOW_HEIGHT +
                                              settings.HUD_OFFSETY))

    def draw_game(self, game):
        self.world.fill(settings.WHITE)
        draw_text(self.world, "Welcome To Hog Maze",
                  45, 350, 100, settings.BLUE)
        for name, obj in game.current_objects.items():
            for sprite in obj:
                if sprite.name_object != 'hoggy':
                    self.world.blit(sprite.image, (sprite.x, sprite.y))

    def set_game_objects(self, game, **kwargs):
        self.state_kwargs = kwargs
        start_button = actor_obj.ActorObject(**{
            'x': 300,
            'y': 200,
            'height': 45,
            'width': 190,
            'in_hud': False,
            'sprite_sheet_key': 4,
            'name_object': 'start_button',
            'animation': AnimationComponent(),
            'clickable': ClickableComponent(
                'rectangle', self.next_level,
                **{"game": game})
        })
        game.current_objects['UI_BUTTONS'].add(start_button)
