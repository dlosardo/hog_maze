from pygame.locals import MOUSEMOTION, QUIT, MOUSEBUTTONUP
from hog_maze.game_states.hoggy_game_state import HoggyGameState


class HoggyLevelTransitionState(HoggyGameState):

    def __init__(self):
        super().__init__()

    def other_listeners(self, game):
        pass

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

    def draw_debug(self, game, dt):
        pass
