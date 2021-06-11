import pygame
from pygame.locals import MOUSEMOTION, QUIT, MOUSEBUTTONUP
import math
import hog_maze.settings as settings
from hog_maze.util.util_draw import draw_text
import hog_maze.actor_obj as actor_obj
from hog_maze.game_states.hoggy_game_state import HoggyGameState
from hog_maze.components.clickable_component import ClickableComponent
from hog_maze.components.animation_component import AnimationComponent


class HoggyFinishLevelState(HoggyGameState):

    def __init__(self):
        super().__init__()
        self.TOMATO_TEXT = "You have {} tomatoes"

    def initialize_state(self):
        print("Initialize Finish Level State")
        self.world = pygame.display.set_mode((settings.WINDOW_WIDTH,
                                              settings.WINDOW_HEIGHT))
        self.prior_level_state = None

    def other_listeners(self, game):
        pass

    def draw_game(self, game):
        self.world.fill(settings.WHITE)
        draw_text(self.world, "Level {} Complete!".format(game.level - 1),
                  45, 350, 100, settings.ORANGE)
        if self.prior_level_state:
            ntomatoes = self.prior_level_state["hoggy"]["ntomatoes"]
            level_state_text = self.TOMATO_TEXT.format(ntomatoes)
            if ntomatoes == 1:
                level_state_text = level_state_text.replace("es", "")
            draw_text(self.world, level_state_text,
                      30, 350, 400, settings.BLUE)
            time_elapsed = self.prior_level_state["time_elapsed"]
            time_text = "You finished in {} minutes and {} seconds".format(
                math.floor(time_elapsed / 1000 / 60),
                math.floor((time_elapsed / 1000) % 60))
            draw_text(self.world, time_text,
                      30, 350, 500, settings.BLUE)
        for name, obj in game.current_objects.items():
            for sprite in obj:
                if sprite.name_object != 'hoggy':
                    self.world.blit(sprite.image, (sprite.x, sprite.y))

    def handle_keys(self, game, event):
        if event.type == QUIT:
            return "QUIT"
        if event.type == MOUSEMOTION:
            mousex, mousey = event.pos
            return "MOUSEMOTION"
        if event.type == MOUSEBUTTONUP:
            mousex, mousey = event.pos
            return "MOUSEBUTTONUP"
        return "no-action"

    def next_level(self, game):
        self.done = True
        from hog_maze.game_states.hoggy_maze_level_state import (
            HoggyMazeLevelState)
        self.next_state = HoggyMazeLevelState
        self.empty_current_objects(game, ['UI_BUTTONS'])

    def set_game_objects(self, game, **kwargs):
        self.state_kwargs = kwargs
        self.prior_level_state = self.state_kwargs['prior_level_state']
        continue_button = actor_obj.ActorObject(**{
            'x': 300,
            'y': 200,
            'height': 45,
            'width': 190,
            'in_hud': False,
            'sprite_sheet_key': 4,
            'name_object': 'continue_button',
            'animation': AnimationComponent(),
            'clickable': ClickableComponent(
                'rectangle', self.next_level,
                **{"game": game})
        })
        game.current_objects['UI_BUTTONS'].add(continue_button)

    def draw_debug(self):
        pass
