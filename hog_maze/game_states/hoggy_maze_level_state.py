import pygame
from pygame.locals import (
    QUIT, KEYDOWN, KEYUP, K_UP, K_DOWN,
    K_LEFT, K_RIGHT, MOUSEMOTION,
    MOUSEBUTTONUP, K_SPACE, K_d, K_p, K_v, K_a
)
import random
import hog_maze.settings as settings
import hog_maze.actor_obj as actor_obj
from hog_maze.util.util_draw import draw_text
from hog_maze.game_states.hoggy_game_state import HoggyGameState
from hog_maze.states.inventory_state import InventoryState
from hog_maze.states.maze_state import MazeState
from hog_maze.components.animation_component import AnimationComponent
from hog_maze.components.orientation_component import OrientationComponent
from hog_maze.components.ai_component import AIComponent
from hog_maze.components.player_input_component import PlayerInputComponent
from hog_maze.components.movable_component import MovableComponent
from hog_maze.components.rilearning_component import RILearningComponent
from hog_maze.components.clickable_component import ClickableComponent
from hog_maze.collision import (
    collision_one_to_many, hoggy_collision_walls, collision_many_to_many
)
import hog_maze.debug.debuginfo as debuginfo
import hog_maze.debug.debugmouse as debugmouse
import hog_maze.debug.debugevent as debugevent
import hog_maze.debug.debugmazestate as debugmazestate


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
        self.level_clock = pygame.time.Clock()
        self.level_start_time = self.level_clock.get_time()

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
               'inventory': InventoryState('ai_hoggy_inventory'),
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
                   pi_a_s_func=game.current_maze.maze_graph.get_pi_a_s,
                   nrows=game.current_maze.maze_height,
                   ncols=game.current_maze.maze_width)
               })
        ai_hoggy.get_state('INVENTORY').add_inventory_type('tomato', 0)
        if random_start:
            random.seed(settings.MAZE_SEED)
            random_state = random.choice(range(nstates))
            starting_vertex = game.current_maze.maze_graph.get_vertex_by_name(
                random_state)
            x, y = game.current_maze.topleft_sprite_center_in_vertex(
                starting_vertex, ai_hoggy)
            ai_hoggy.coords = (x, y)
        self.initialize_ai_hog(game, ai_hoggy, starting_vertex)

    def set_game_objects(self, game, **kwargs):
        self.state_kwargs = kwargs
        self.level_settings = settings.LEVEL_SETTINGS[game.level]
        game.reset_maze(**self.level_settings['reset_maze'])
        game.print_maze_path()
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
                   'inventory': InventoryState('main_player_inventory')
                   })
            main_player.get_state('INVENTORY').add_inventory_type('tomato', 0)
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
        # for ai_hoggy in game.current_objects['AI_HOGS']:
        # self.debugscreen.update(ai_hoggy, dt)
        # for i, t in enumerate(self.debugscreen.text_list):
        # self.world.blit(t, (0, 500 + (i * 30)))
        self.world.blit(self.debugm.text, (0, 400))
        for i, t in enumerate(self.debugmazestate.text_list):
            self.world.blit(t, (0, 500 + (i * 30)))
        # self.debugscreen.update(game.main_player, dt)
        # for i, t in enumerate(self.debugscreen.text_list):
            # self.world.blit(t, (0, 500 + (i * 30)))

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
              'INVENTORY').get_total_for_item('tomato')
        draw_text(self.hud, "x",
                  24, 55, 28, settings.ORANGE)
        draw_text(self.hud, "{}".format(ntomatoes),
                  40, 75, 30, settings.ORANGE)
        draw_text(self.hud, "SEED: {}".format(game.current_maze.seed),
                  30, 175, 20, settings.GREEN)

    def draw_game(self, game):
        self.world.fill(settings.WHITE)
        game.current_maze.image.fill(settings.WHITE)
        self.hud.fill(settings.BLACK)

        for name, obj in game.current_objects.items():
            if (name == 'ARROWS') and (not settings.SHOW_ARROWS):
                continue
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
            self.level_clock.tick()
            level_state = self.set_level_state(game,
                                               self.level_clock.get_time())
            print(f"LEVEL STATE {level_state}")
            self.done = True
            game.level += 1
            game.current_maze = None
            from hog_maze.game_states.hoggy_finish_level_state import (
                HoggyFinishLevelState)
            self.next_state = HoggyFinishLevelState
            self.state_kwargs = {'prior_level_state': level_state}
            self.empty_current_objects(game,
                                       ['MAZE_WALLS', 'PICKUPS',
                                        'HUD', 'UI_BUTTONS',
                                        'AI_HOGS', 'ARROWS'])

    def set_level_state(self, game, time_elapsed):
        level_state_dict = {}
        for ai_hog in game.current_objects['AI_HOGS']:
            level_state_dict.update({
                ai_hog.name_object: {
                    "ntomatoes": ai_hog.get_state(
                        'INVENTORY').get_total_for_item('tomato'),
                    "ntomatoes_removed": ai_hog.get_state(
                        'INVENTORY').get_nremoved_for_item('tomato')
                }
            })
        level_state_dict.update({
            game.main_player.name_object: {
                "ntomatoes": game.main_player.get_state(
                    'INVENTORY').get_total_for_item('tomato'),
                "ntomatoes_removed": game.main_player.get_state(
                    'INVENTORY').get_nremoved_for_item('tomato')
            }
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
                    if not sp.get_state('MAZE').end:
                        sp.get_component('RILEARNING').recalc = True
                        sp.get_component('RILEARNING').converged = True

    def set_next_dest_from_pi_a_s(self, game, sprite):
        next_dest = game.current_maze.next_dest_from_pi_a_s(
            sprite.get_component('RILEARNING').pi_a_s,
            sprite)
        sprite.get_component('AI').destination = next_dest

    def set_next_dest_from_value_matrix(self, game, sprite):
        next_dest = game.current_maze.next_dest_from_value_matrix(
            sprite.get_component('RILEARNING').V,
            sprite, True, .5)
        sprite.get_component('AI').destination = next_dest

    def initialize_ai_hog(self, game, sprite, vertex):
        sprite.get_state('MAZE').reset_edge_visits(
            game.current_maze.maze_graph.edges)
        sprite.get_state('MAZE').current_vertex = vertex
        vertex.increment_sprite_visit_count(sprite)
        self.set_next_dest_from_pi_a_s(game, sprite)
        if sprite.name_object == 'ai_hoggy':
            game.current_maze.set_arrows(
                sprite.get_component('RILEARNING').pi_a_s)
            game.current_objects['ARROWS'].add(
                game.current_maze.arrows)
        # self.set_next_dest_from_value_matrix(game, sprite)
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
                        # print("update from reaching dest")
                        self.set_next_dest_from_pi_a_s(game, sprite)
                        # self.set_next_dest_from_value_matrix(game, sprite)

    def handle_event_paused(self, game, event):
        if event.type == MOUSEBUTTONUP:
            mousex, mousey = event.pos
            vertex = game.current_maze.vertex_from_x_y(
                mousex - settings.HUD_OFFSETX,
                mousey - settings.HUD_OFFSETY)
            if vertex:
                self.debugmazestate.update(vertex, game.current_maze.seed)
                self.draw_game(game)
                self.draw_debug(game, 0)
                pygame.display.update()
        if event.type == KEYUP and event.key == K_p:
            game.is_paused = False

    def other_listeners(self, game):
        for sp in game.current_objects['AI_HOGS']:
            if not sp.get_state('MAZE').end:
                if sp.get_component('RILEARNING').just_updated:
                    sp.get_component('RILEARNING').just_updated = False
                    print("update from other_listeners")
                    # self.set_next_dest_from_value_matrix(game, sp)
                    self.set_next_dest_from_pi_a_s(game, sp)
                    if sp.name_object == 'ai_hoggy':
                        game.current_objects['ARROWS'].empty()
                        game.current_maze.set_arrows(
                            sp.get_component('RILEARNING').pi_a_s)
                        game.current_objects['ARROWS'].add(
                            game.current_maze.arrows)

    def handle_keys(self, game, event):
        self.debugevent.update(event)
        if event.type == QUIT:
            return "QUIT"
        if (event.type == KEYUP) and (event.key == K_p):
            game.is_paused = True
            return "pause-event"
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
                print("key down eat")
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
            if event.key == K_v:
                for ai_hoggy in game.current_objects['AI_HOGS']:
                    print(ai_hoggy.name_object)
                    print(settings.r31(ai_hoggy.get_component('RILEARNING').V))
                    print(ai_hoggy.get_component('RILEARNING').pi_a_s)
                    ai_hoggy.get_component('RILEARNING').print_pi_a_s()
            if event.key == K_a:
                settings.SHOW_ARROWS = not settings.SHOW_ARROWS

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
                self.debugmazestate.update(vertex, game.current_maze.seed)
            return "MOUSEBUTTONUP"
        if event.type in [KEYDOWN, KEYUP]:
            if event.key == K_v or event.key == K_a or event.key == K_SPACE:
                return "OTHER"
            else:
                return "player-movement"
        return "no-action"
