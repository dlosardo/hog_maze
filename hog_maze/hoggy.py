import pygame
from pygame.locals import (
    QUIT, KEYDOWN, KEYUP, K_UP, K_DOWN,
    K_LEFT, K_RIGHT, MOUSEMOTION,
    MOUSEBUTTONUP, K_SPACE, K_d, K_p
)
import random
import hog_maze.settings as settings
import hog_maze.actor_obj as actor_obj
from hog_maze.game import Game
from hog_maze.util.util_draw import draw_text
from hog_maze.components.animation_component import AnimationComponent
from hog_maze.components.player_input_component import PlayerInputComponent
from hog_maze.components.movable_component import MovableComponent
from hog_maze.components.clickable_component import ClickableComponent
from hog_maze.components.orientation_component import OrientationComponent
from hog_maze.components.ai_component import AIComponent
from hog_maze.components.rilearning_component import RILearningComponent
from hog_maze.states.inventory_state import InventoryState
from hog_maze.states.maze_state import MazeState
from hog_maze.collision import (
    collision_one_to_many, hoggy_collision_walls, collision_many_to_many
)
import hog_maze.debug.debuginfo as debuginfo
import hog_maze.debug.debugmouse as debugmouse
import hog_maze.debug.debugevent as debugevent
import hog_maze.debug.debugmazestate as debugmazestate

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
        self.event_loop(collisions=False)
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


class HoggyGameState(object):

    def __init__(self):
        self.done = False
        self.next_state = None
        self.state_kwargs = {}
        self.level_settings = {}
        self.initialize_state()

    def empty_current_objects(self, game, object_name_list):
        for object_name in object_name_list:
            game.current_objects[object_name].empty()

    def initialize_state(self):
        raise NotImplementedError

    def set_game_objects(self, game, **kwargs):
        raise NotImplementedError

    def draw_game(self, game):
        raise NotImplementedError

    def draw_debug(self):
        raise NotImplementedError

    def handle_keys(self, game, event):
        raise NotImplementedError

    def handle_collisions(self, game):
        pass

    def handle_event_paused(self):
        pass


class HoggyFinishLevelState(HoggyGameState):

    def __init__(self):
        super().__init__()

    def initialize_state(self):
        print("Initialize Finish Level State")
        self.world = pygame.display.set_mode((settings.WINDOW_WIDTH,
                                              settings.WINDOW_HEIGHT))
        self.prior_level_state = None

    def draw_game(self, game):
        self.world.fill(settings.WHITE)
        draw_text(self.world, "Level {} Complete!".format(game.level - 1),
                  45, 350, 100, settings.ORANGE)
        if self.prior_level_state:
            level_state_text = "You picked up {} tomatoes".format(
                self.prior_level_state["hoggy"]["ntomatoes"])
            draw_text(self.world, level_state_text,
                      30, 350, 400, settings.BLUE)
            time_elapsed = self.prior_level_state["time_elapsed"]
            time_text = "You finished in {} minutes and {} seconds".format(
                time_elapsed, time_elapsed)
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
        self.next_state = HoggyMazeLevelState
        self.empty_current_objects(game, ['UI_BUTTONS'])
        game.reset_maze(
            **settings.LEVEL_SETTINGS[game.level][
                'reset_maze'])

    def set_game_objects(self, game, **kwargs):
        self.empty_current_objects(game,
                                   ['MAZE_WALLS', 'PICKUPS',
                                    'HUD', 'UI_BUTTONS',
                                    'AI_HOGS'])

        self.prior_level_state = kwargs['prior_level_state']
        print(self.prior_level_state)
        continue_button = actor_obj.ActorObject(**{
            'x': 300,
            'y': 200,
            'height': settings.SPRITE_SIZE * 2,
            'width': settings.SPRITE_SIZE * 2,
            'in_hud': False,
            'sprite_sheet_key': 2,
            'name_object': 'continue_button',
            'animation': AnimationComponent(),
            'clickable': ClickableComponent(
                'circle', self.next_level,
                **{"game": game})
        })
        game.current_objects['UI_BUTTONS'].add(continue_button)

    def draw_debug(self):
        pass


class HoggyMazeLevelState(HoggyGameState):

    def __init__(self):
        super().__init__()

    def initialize_state(self):
        self.debugscreen = debuginfo.DebugInfo()
        self.debugevent = debugevent.DebugEvent()
        self.debugm = debugmouse.DebugMouse()
        self.debugm.update("", "")
        self.debugmazestate = debugmazestate.DebugMazeState()
        self.world = pygame.display.set_mode((settings.WINDOW_WIDTH +
                                              settings.HUD_OFFSETX,
                                              settings.WINDOW_HEIGHT +
                                              settings.HUD_OFFSETY))
        self.hud = pygame.Surface([settings.WINDOW_WIDTH,
                                   settings.HUD_OFFSETY]).convert()
        self.game_clock = pygame.time.Clock()
        self.level_start_time = self.game_clock.get_time()
        print("START TIME: {}".format(self.level_start_time))

    def add_ai_hoggy(self, game, ai_hoggy_name, x, y,
                     starting_vertex,
                     ai_hoggy_type='default',
                     random_start=False):
        nstates = (self.level_settings['reset_maze']['maze_width']
                   * self.level_settings['reset_maze']['maze_height'])
        ai_hoggy_stats = settings.AI_HOGGY_STARTING_STATS[ai_hoggy_type]
        ai_hoggy = actor_obj.ActorObject(
            **{'x': x - (settings.SPRITE_SIZE / 2),
               'y': y - (settings.SPRITE_SIZE / 2),
               'height': settings.SPRITE_SIZE, 'width': settings.SPRITE_SIZE,
               'sprite_sheet_key': ai_hoggy_stats['sprite_sheet_key'],
               'name_object': ai_hoggy_name,
               'inventory': InventoryState('tomato'),
               'maze': MazeState('maze_state'),
               'animation': AnimationComponent(),
               'orientation': OrientationComponent('horizontal', 'right'),
               'movable': MovableComponent(
                   'ai_hoggy_move', ai_hoggy_stats['speed']),
               'ai': AIComponent(),
               'rilearning':
               RILearningComponent(
                   name_instance="ril_ai_hoggy",
                   gamma=ai_hoggy_stats['gamma'],
                   nstates=nstates,
                   action_space=game.action_space,
                   actions=game.actions,
                   reward_dict=ai_hoggy_stats['reward_dict'],
                   reward_func=game.current_maze.maze_graph.set_rewards_table,
                   pi_a_s_func=game.current_maze.maze_graph.get_pi_a_s)
               })
        if random_start:
            random_state = random.choice(range(nstates))
            starting_vertex = game.current_maze.maze_graph.get_vertex_by_name(
                random_state)
            x, y = game.current_maze.topleft_sprite_center_in_vertex(
                starting_vertex, ai_hoggy)
            ai_hoggy.coords = (x, y)
        self.initialize_ai_hog(game, ai_hoggy, starting_vertex)

    def set_game_objects(self, game, **kwargs):
        self.level_settings = settings.LEVEL_SETTINGS[game.level]
        starting_vertex = game.current_maze.maze_graph.start_vertex
        (x, y) = game.current_maze.center_for_vertex(starting_vertex)
        print("CENTER X: {}, CENTER Y: {}".format(x, y))
        if self.level_settings['new_hoggy']:
            main_player = actor_obj.ActorObject(
                **{'x': x - (settings.SPRITE_SIZE / 2),
                   'y': y - (settings.SPRITE_SIZE / 2),
                   'height': settings.SPRITE_SIZE,
                   'width': settings.SPRITE_SIZE,
                   'sprite_sheet_key':
                   settings.HOGGY_STARTING_STATS['sprite_sheet_key'],
                   'name_object': 'hoggy',
                   'animation': AnimationComponent(),
                   'player_input': PlayerInputComponent(),
                   'orientation': OrientationComponent('horizontal', 'right'),
                   'movable': MovableComponent('hoggy_move',
                                               settings.HOGGY_STARTING_STATS[
                                                   'speed']),
                   'inventory': InventoryState('tomato')
                   })
            print("HOGGY X: {}, HOGGY Y: {}".format(main_player.x,
                                                    main_player.y))
            game.main_player = main_player
        else:
            game.main_player.get_component("PLAYER_INPUT").reset_keys()
        randomize_button = actor_obj.ActorObject(**{
            'x': settings.WINDOW_WIDTH - 200,
            'y': 0,
            'height': settings.SPRITE_SIZE * 2,
            'width': settings.SPRITE_SIZE * 2,
            'in_hud': True,
            'sprite_sheet_key': 2,
            'name_object': 'randomize_button',
            'animation': AnimationComponent(),
            'clickable': ClickableComponent(
                'circle', game.reset_maze,
                **self.level_settings['reset_maze'])
        })
        game.current_objects['UI_BUTTONS'].add(randomize_button)
        for ai_hoggy_name, ai_hoggy_type in self.level_settings[
                'ai_hogs'].items():
            self.add_ai_hoggy(game, ai_hoggy_name, x, y,
                              starting_vertex,
                              ai_hoggy_type=ai_hoggy_type)
        self.set_hud(game)

    def draw_debug(self, game, dt):
        for ai_hoggy in game.current_objects['AI_HOGS']:
            self.debugscreen.update(ai_hoggy, dt)
            self.world.blit(self.debugm.text, (0, 400))
            for i, t in enumerate(self.debugmazestate.text_list):
                self.world.blit(t, (0, 500 + (i * 30)))

    def set_hud(self, game):
        tomato = actor_obj.ActorObject(
            **{'x': 10, 'y': 10,
               'height': settings.TOMATO_STATE['height'],
               'width': settings.TOMATO_STATE['width'],
               'sprite_sheet_key': settings.TOMATO_STATE['sprite_sheet_key'],
               'in_hud': True,
               'name_object': 'hud_tomato'
               })
        game.current_objects['HUD'].add(tomato)

    def draw_to_hud(self, game):
        ntomatoes = game.main_player.get_state(
              'INVENTORY').inventory.get('tomato')
        draw_text(self.hud, "x",
                  24, 55, 28, settings.ORANGE)
        draw_text(self.hud, "{}".format(ntomatoes),
                  40, 75, 30, settings.ORANGE)

    def draw_game(self, game):
        self.world.fill(settings.WHITE)
        game.current_maze.image.fill(settings.WHITE)
        self.hud.fill(settings.BLACK)

        for name, obj in game.current_objects.items():
            for sprite in obj:
                if not sprite.in_hud:
                    game.current_maze.image.blit(sprite.image,
                                                 (sprite.x, sprite.y))
                else:
                    self.hud.blit(sprite.image, (sprite.x, sprite.y))
                    self.draw_to_hud(game)
        self.world.blit(game.current_maze.image,
                        (0, settings.HUD_OFFSETY))
        self.world.blit(self.hud, (0, 0))

    def hoggy_collision_exit(self, game, sprite):
        if sprite.rect.colliderect(game.current_maze.exit_vertex_rect):
            print("HOGGY FOUND EXIT")
            self.game_clock.tick()
            level_state = self.print_level_state(game,
                                                 self.game_clock.get_time())
            self.done = True
            game.level += 1
            game.current_maze = None
            self.next_state = HoggyFinishLevelState
            self.state_kwargs = {'prior_level_state': level_state}

    def print_level_state(self, game, time_elapsed):
        level_state_dict = {}
        for ai_hog in game.current_objects['AI_HOGS']:
            level_state_dict.update({
                ai_hog.name_object: {
                    "ntomatoes": ai_hog.get_state(
                        'INVENTORY').inventory.get('tomato')}
                })
        level_state_dict.update({
            game.main_player.name_object: {
                "ntomatoes": game.main_player.get_state(
                    'INVENTORY').inventory.get('tomato')}
            })
        level_state_dict.update({
            'time_elapsed': time_elapsed})
        return(level_state_dict)

    def handle_collisions(self, game):
        collision_one_to_many(game.current_objects[
            'MAIN_PLAYER'], game.current_objects[
                'MAZE_WALLS'], hoggy_collision_walls,
            game)
        collision_one_to_many(game.current_objects[
            'MAIN_PLAYER'], game.current_objects[
                'PICKUPS'], self.hoggy_collision_tomatoes,
            game)
        collision_many_to_many(game.current_objects[
            'AI_HOGS'], game.current_objects[
                'PICKUPS'], self.hoggy_collision_tomatoes,
            game)
        self.collision_ai_destinations(game.current_objects[
            'AI_HOGS'], game)
        self.hoggy_collision_exit(game, game.current_objects[
            'MAIN_PLAYER'].sprite)

    def hoggy_collision_tomatoes(self, sprite, colliding_pickups, game):
        for pickup in colliding_pickups:
            if pickup.get_component('PICKUPABLE').name_instance == "tomato":
                pickup.get_component('PICKUPABLE').picked_up = True
                sprite.get_state('INVENTORY').add_item(
                    pickup.get_component('PICKUPABLE').name_instance)
                print("pick up tomato")
                vertex = game.current_maze.vertex_from_x_y(
                    pickup.x, pickup.y)
                vertex.has_tomato = False
                vertex.sprite_with_tomato = sprite
                for sp in game.current_objects['AI_HOGS']:
                    sp.get_component('RILEARNING').recalc = True

    def set_next_dest_from_pi_a_s(self, game, sprite):
        next_dest = game.current_maze.next_dest_from_pi_a_s(
            sprite.get_component('RILEARNING').pi_a_s,
            sprite)
        sprite.get_component('AI').destination = next_dest

    def initialize_ai_hog(self, game, sprite, vertex):
        sprite.get_state('MAZE').reset_edge_visits(
            game.current_maze.maze_graph.edges)
        sprite.get_state('MAZE').current_vertex = vertex
        vertex.increment_sprite_visit_count(sprite)
        self.set_next_dest_from_pi_a_s(game, sprite)
        game.add_ai_hoggy(sprite)

    def collision_ai_destinations(self, sprite_group, game):
        for sprite in sprite_group:
            if not sprite.get_state('MAZE').end:
                if sprite.get_component('AI').reached_destination():
                    vertex = game.current_maze.vertex_from_point(
                        sprite.get_component('AI').destination)
                    sprite.get_state('MAZE').current_vertex = vertex
                    if vertex is None:
                        print("Vertex is none, dest is {}".format(
                            sprite.get_component('AI').destination))
                    else:
                        vertex.increment_sprite_visit_count(sprite)
                    if sprite.has_component('RILEARNING'):
                        self.set_next_dest_from_pi_a_s(game, sprite)

    def handle_event_paused(self, game, event):
        if event.type == MOUSEBUTTONUP:
            mousex, mousey = event.pos
            vertex = game.current_maze.vertex_from_x_y(
                mousex - settings.HUD_OFFSETX,
                mousey - settings.HUD_OFFSETY)
            if vertex:
                self.debugmazestate.update(vertex)
                self.draw_game(game)
                self.draw_debug(game, 0)
                pygame.display.update()
        if event.type == KEYUP and event.key == K_p:
            game.is_paused = False

    def handle_keys(self, game, event):
        self.debugevent.update(event)
        if event.type == QUIT:
            return "QUIT"
        if event.type == KEYDOWN:
            if event.key == K_UP:
                game.main_player.get_component('PLAYER_INPUT').set_key_down(
                    'up')
            if event.key == K_DOWN:
                game.main_player.get_component('PLAYER_INPUT').set_key_down(
                    'down')
            if event.key == K_LEFT:
                game.main_player.get_component('PLAYER_INPUT').set_key_down(
                    'left')
            if event.key == K_RIGHT:
                game.main_player.get_component('PLAYER_INPUT').set_key_down(
                    'right')
            if event.key == K_SPACE:
                game.main_player.get_component('PLAYER_INPUT').set_key_down(
                    'eat')
        if event.type == KEYUP:
            if event.key == K_UP:
                game.main_player.get_component('PLAYER_INPUT').set_key_up(
                    'up')
            if event.key == K_DOWN:
                game.main_player.get_component('PLAYER_INPUT').set_key_up(
                    'down')
            if event.key == K_LEFT:
                game.main_player.get_component('PLAYER_INPUT').set_key_up(
                    'left')
            if event.key == K_RIGHT:
                game.main_player.get_component('PLAYER_INPUT').set_key_up(
                    'right')
            if event.key == K_SPACE:
                game.main_player.get_component('PLAYER_INPUT').set_key_up(
                    'eat')
                print("key up eat")
                game.main_player.get_component('PLAYER_INPUT').just_ate = False
            if event.key == K_d:
                settings.IS_DEBUG = not settings.IS_DEBUG
            if event.key == K_p:
                game.is_paused = True
        if event.type == MOUSEMOTION:
            mousex, mousey = event.pos
            self.debugm.update(mousex, mousey)
            return "MOUSEMOTION"
        if event.type == MOUSEBUTTONUP:
            mousex, mousey = event.pos
            vertex = game.current_maze.vertex_from_x_y(
                mousex - settings.HUD_OFFSETX,
                mousey - settings.HUD_OFFSETY)
            if vertex:
                self.debugmazestate.update(vertex)
            return "MOUSEBUTTONUP"
        if event.type in [KEYDOWN, KEYUP]:
            return "player-movement"
        return "no-action"


if __name__ == '__main__':
    hoggy = Hoggy(HoggyMazeLevelState)
    hoggy.main()
