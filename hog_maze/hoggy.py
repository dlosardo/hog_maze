import pygame
import hog_maze.settings as settings
from hog_maze.game import Game

from hog_maze.game_states.hoggy_maze_level_state import HoggyMazeLevelState


COMPONENTS = ['RILEARNING', 'PLAYER_INPUT', 'AI', 'MOVABLE', 'ORIENTATION',
              'ANIMATION', 'CLICKABLE', 'PICKUPABLE']


class Hoggy(object):

    def __init__(self, state):
        self.game_quit = False
        self.game_initialize()
        self.state = state()
        self.game = Game()
        self.state.set_game_objects(self.game)

    def game_initialize(self):
        pygame.init()
        self.fps_clock = pygame.time.Clock()

    def update_components(self, dt, mousex, mousey, event_type):
        for component in COMPONENTS:
            for name, obj in self.game.current_objects.items():
                for sprite in obj:
                    if not sprite.is_dead:
                        if sprite.has_component(component):
                            sprite.get_component(component).update(
                                **{'dt': dt, 'mousex': mousex,
                                   'mousey': mousey,
                                   'event_type': event_type
                                   })
                    if sprite.is_dead:
                        sprite.kill()

    def draw_game(self):
        self.state.draw_game(self.game)

    def draw_debug(self, dt):
        self.state.draw_debug(self.game, dt)

    def handle_collisions(self):
        self.state.handle_collisions(self.game)

    def handle_keys(self, event):
        action = self.state.handle_keys(self.game, event)
        return action

    def handle_event_paused(self, event):
        self.state.handle_event_paused(self.game, event)

    def update_game_state(self):
        if self.state.done:
            self.change_game_state()

    def change_game_state(self):
        print("CHANGE GAME STATE")
        state_kwargs = self.state.state_kwargs
        self.state = self.state.next_state()
        self.state.set_game_objects(self.game, **state_kwargs)

    def event_loop(self, collisions=True):
        dt = self.fps_clock.get_time()
        events = pygame.event.get()
        mousex, mousey = pygame.mouse.get_pos()
        if len(events) == 0:
            events.append("no-action")
        for event in events:
            if event == "no-action":
                event_type = event
            else:
                event_type = self.handle_keys(event)
            if event_type == "QUIT":
                self.game_quit = True
                continue
            self.update_components(dt, mousex, mousey, event_type)
            if collisions:
                self.handle_collisions()

    def game_loop(self):
        while not self.game_quit:
            while self.game.is_paused:
                events = pygame.event.get()
                for event in events:
                    self.handle_event_paused(event)
            self.event_loop()
            self.update_game_state()
            self.draw_game()

            if settings.IS_DEBUG:
                self.draw_debug(0)

            pygame.display.update()
            self.fps_clock.tick(settings.FPS)

    def main(self):
        self.game_loop()
        pygame.quit()


if __name__ == '__main__':
    hoggy = Hoggy(HoggyMazeLevelState)
    hoggy.main()
