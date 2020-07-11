import pygame
import random
import numpy as np
from pygame.locals import (
    QUIT, KEYDOWN, KEYUP, K_UP, K_DOWN,
    K_LEFT, K_RIGHT, MOUSEMOTION,
    MOUSEBUTTONUP, K_SPACE, K_d, K_p
)
import hog_maze.settings as settings
import hog_maze.actor_obj as actor_obj
from hog_maze.util.util_draw import draw_text
from hog_maze.components.animation_component import AnimationComponent
from hog_maze.components.player_input_component import PlayerInputComponent
from hog_maze.components.movable_component import MovableComponent
from hog_maze.components.clickable_component import ClickableComponent
from hog_maze.components.orientation_component import OrientationComponent
from hog_maze.components.pickupable_component import PickupableComponent
from hog_maze.states.inventory_state import InventoryState
from hog_maze.states.maze_state import MazeState
from hog_maze.maze.maze_game import MazeGame
import hog_maze.debug.debuginfo as debuginfo
import hog_maze.debug.debugmouse as debugmouse
import hog_maze.debug.debugevent as debugevent
import hog_maze.debug.debugmazestate as debugmazestate

from IPython.display import clear_output
from time import sleep

MOVE_AI_HOGGY_TIMEOUT = 1000
AI_HOGGY_MOVE = pygame.USEREVENT + 1
RELOADED_EVENT = pygame.USEREVENT + 2

COMPONENTS = ['PLAYER_INPUT', 'MOVABLE', 'ORIENTATION',
              'ANIMATION', 'CLICKABLE', 'PICKUPABLE']

settings.IS_DEBUG = True


def update_components(dt, mousex, mousey, event_type):
    for component in COMPONENTS:
        for name, obj in GAME.current_objects.items():
            for sprite in obj:
                if not sprite.is_dead:
                    if sprite.has_component(component):
                        sprite.get_component(component).update(
                            **{'dt': dt,
                               'mousex': mousex,
                               'mousey': mousey,
                               'event_type': event_type
                               })
                if sprite.is_dead:
                    sprite.kill()


def draw_game():
    WORLD.fill(settings.WHITE)
    GAME.current_maze.image.fill(settings.WHITE)
    GAME.hud.fill(settings.BLACK)

    for name, obj in GAME.current_objects.items():
        for sprite in obj:
            if not sprite.in_hud:
                GAME.current_maze.image.blit(sprite.image,
                                             (sprite.x, sprite.y)
                                             )
            else:
                GAME.hud.blit(sprite.image,
                              (sprite.x, sprite.y))
                ntomatoes = GAME.main_player.get_state(
                      'INVENTORY').inventory.get('tomato')
                draw_text(GAME.hud, "x",
                          24, 55, 28, settings.ORANGE)
                draw_text(GAME.hud, "{}".format(ntomatoes),
                          40, 75, 30, settings.ORANGE)
    WORLD.blit(GAME.current_maze.image,
               (0, settings.HUD_OFFSETY))
    WORLD.blit(GAME.hud,
               (0, 0))


def draw_debug(dt):
    DEBUGSCREEN.update(GAME.ai_hoggy, dt)
    # for i, t in enumerate(DEBUGSCREEN.text_list):
    # WORLD.blit(t, (0, 465 + (i * 30)))
    # WORLD.blit(DEBUGM.text, (0, 400))
    # WORLD.blit(DEBUGEVENT.text, (0, 440))
    for i, t in enumerate(DEBUGMAZESTATE.text_list):
        WORLD.blit(t, (0, 500 + (i * 30)))


class Game():
    def __init__(self):
        self.current_objects = {}
        self.current_objects.update(
            {'MAIN_PLAYER': actor_obj.ActorObjectGroupSingle(
                'MAIN_PLAYER')})
        self.current_objects.update(
            {'MAZE_WALLS': actor_obj.ActorObjectGroup(
                'MAZE_WALL')})
        self.current_objects.update(
            {'UI_BUTTONS': actor_obj.ActorObjectGroup(
                'UI_BUTTON')})
        self.current_objects.update(
            {'PICKUPS': actor_obj.ActorObjectGroup(
                'PICKUP')})
        self.current_objects.update(
            {'AI_HOGGY': actor_obj.ActorObjectGroupSingle(
                'AI_HOGGY')})
        self.current_objects.update(
            {'HUD': actor_obj.ActorObjectGroup(
                'HUD')})
        self.current_maze = None
        self.reset_maze(**settings.maze_starting_state)
        self.hud = pygame.Surface([settings.WINDOW_WIDTH,
                                   settings.HUD_OFFSETY]
                                  ).convert()
        self.hud_rect = self.hud.get_rect()
        self.set_hud()
        self.is_paused = False
        self.nstates = (self.current_maze.maze_width *
                        self.current_maze.maze_height)
        self.action_space = 4
        self.actions = [MazeGame.NORTH,
                        MazeGame.SOUTH,
                        MazeGame.EAST,
                        MazeGame.WEST]
        self.rewards_table = self.current_maze.maze_graph.set_rewards_table(
            self.actions)
        self.alpha = 0.3
        self.gamma = 0.9
        self.epsilon = 0.1
        self.q_n = np.zeros([
            self.nstates, self.action_space
        ])

    @property
    def main_player(self):
        return self.current_objects['MAIN_PLAYER'].sprite

    @main_player.setter
    def main_player(self, main_player_sprite):
        self.current_objects['MAIN_PLAYER'].add(
            main_player_sprite)

    @property
    def ai_hoggy(self):
        return self.current_objects['AI_HOGGY'].sprite

    @ai_hoggy.setter
    def ai_hoggy(self, ai_hoggy_sprite):
        self.current_objects['AI_HOGGY'].add(
            ai_hoggy_sprite)

    def update_qn_for_state_action(self, state, action):
        self.q_n[state][action] = self.q_n[state][action] + self.alpha * (
            self.reward_for_state_action(
                state, action) - self.q_n[state][action])

    def update_qn_for_state_action_1(self, state, action):
        self.q_n[state][action] = (1 - self.alpha)*self.q_n[
            state][action] + self.alpha*(self.reward_for_state_action(
                state, action) + self.gamma*np.max(
                    self.q_n[self.next_state_for_state_action(
                        state, action)]))

    def update_qn_for_state_action_2(self, state, action):
        self.cum_reward = 0
        self.q_n[state][action] = (1 - self.alpha)*self.q_n[
            state][action] + self.alpha*(self.reward_for_state_action(
                state, action) + self.gamma*self.expected_reward(
                    state, action, False))

    def expected_reward(self, state, action, end):
        if end:
            return self.reward_for_state_action(
                state, action)
        elif self.cum_reward < -100:
            return self.reward_for_state_action(
                state, action)
        else:
            (p, next_state,
             reward, end) = self.rewards_table[state][action][0]
            self.cum_reward += reward
            return reward + self.gamma * self.expected_reward(
                next_state, self.epsilon_greedy(next_state), end)

    def max_action(self, state):
        max_est = np.max(self.q_n[state])
        if np.sum([m == max_est for m in self.q_n[state]]) > 1:
            action = np.random.choice(
                np.where(max_est == self.q_n[state])[0])
        else:
            action = np.argmax(self.q_n[state])
        return action

    def epsilon_greedy(self, state):
        if random.uniform(0, 1) < self.epsilon:
            # Explore action space
            action = self.current_maze.random_action(self.actions)
        else:
            # Exploit learned values
            action = self.max_action(state)
        return action

    def reward_for_state_action(self, state, action):
        return self.rewards_table[state][action][0][2]

    def next_state_for_state_action(self, state, action):
        return self.rewards_table[state][action][0][1]

    def train_ai_hoggy(self):
        state = 0
        self.current_maze.set_state(state, self.ai_hoggy)
        self.ai_hoggy.get_state('MAZE').end = False
        while not self.ai_hoggy.get_state('MAZE').end:
            clear_output(wait=True)
            # get current state?
            if random.uniform(0, 1) < self.epsilon:
                # Explore action space
                action = self.current_maze.random_action(self.actions)
            else:
                # Exploit learned values
                action = self.max_action(state)
            # need to update q_n somewhere here
            (p, next_state,
             reward, end) = self.rewards_table[state][action][0]
            self.update_qn_for_state_action_2(state, action)
            self.ai_hoggy.get_state('MAZE').rewards += reward
            self.ai_hoggy.get_state('MAZE').end = end
            self.current_maze.set_state(next_state,
                                        self.ai_hoggy)
            state = next_state
            self.print_maze_path()
            sleep(.1)

    def reset_maze(self, maze_width, maze_height,
                   area_width, area_height,
                   wall_scale, starting_vertex_name=0):
        if self.current_maze:
            self.current_maze.reset()
            self.main_player.x = self.main_player.start_x
            self.main_player.y = self.main_player.start_y
        else:
            self.current_maze = MazeGame(maze_width, maze_height,
                                         area_width, area_height,
                                         wall_scale)
        self.current_maze.set_maze(starting_vertex_name)
        self.current_objects['PICKUPS'].empty()
        self.current_objects['MAZE_WALLS'].empty()
        self.current_objects['MAZE_WALLS'].add(
            self.current_maze.maze_walls)
        self.place_tomatoes()
        if self.current_objects['AI_HOGGY']:
            self.ai_hoggy.get_state(
                'MAZE').reset_maze_state(
                    self.current_maze.maze_graph.edges)
            self.ai_hoggy.set_pos(
                self.ai_hoggy.start_x,
                self.ai_hoggy.start_y)
            self.ai_hoggy.get_state(
                'MAZE').current_vertex = self.current_maze.vertex_from_x_y(
                    self.ai_hoggy.x,
                    self.ai_hoggy.y)
            self.ai_hoggy.get_state(
                'INVENTORY').reset_inventory_state()
        # self.current_maze.maze_graph.traverse_graph(starting_vertex_name)

    def place_tomatoes(self):
        cubby_vertices = self.current_maze.maze_graph.all_cubby_vertices()
        if len(cubby_vertices) > 0:
            for cubby_vertex in cubby_vertices:
                tomato = actor_obj.ActorObject(
                    **{'x': 0, 'y': 0, 'height': 32, 'width': 32,
                       'sprite_sheet_key': 3,
                       'name_object': 'tomato',
                       'animation': AnimationComponent(is_animating=True),
                       'pickupable': PickupableComponent('tomato')
                       })
                x, y = self.current_maze.topleft_sprite_center_in_vertex(
                    cubby_vertex, tomato)
                tomato.set_pos(x, y)
                # print("ADDING TOMATO TO VERTEX {}".format(cubby_vertex))
                cubby_vertex.has_tomato = True
                self.current_objects['PICKUPS'].add(tomato)

    def set_hud(self):
        tomato = actor_obj.ActorObject(
            **{'x': 10, 'y': 10, 'height': 32, 'width': 32,
               'sprite_sheet_key': 3,
               'in_hud': True,
               'name_object': 'hud_tomato'
               })
        self.current_objects['HUD'].add(tomato)

    def print_maze_path(self):
        maze_path = ""
        top_layer = ""
        bottom_layer = ""
        (ai_hoggy_row, ai_hoggy_col) = self.ai_hoggy.get_state('MAZE').coord
        for row in range(0, self.current_maze.maze_height):
            maze_path_below = ""
            maze_path_above = ""
            for col in range(0, self.current_maze.maze_width):
                current_vertex = self.current_maze.maze_graph.maze_layout[
                    row][col]
                data = " "
                if current_vertex.has_tomato:
                    data = "T"
                if current_vertex.sprite_visits[self.ai_hoggy.name_object]:
                    data = "#"
                if ai_hoggy_row == row and ai_hoggy_col == col:
                    data = "H"
                if not current_vertex.is_right_vertex:
                    wall = self.current_maze.maze_graph.\
                            east_structure_from_vertex(current_vertex)
                    if (current_vertex.is_left_vertex) and (
                         not current_vertex.is_top_vertex):
                        if current_vertex.is_exit_vertex:
                            maze_path_below += "  {} {} ".format(data, wall)
                        else:
                            maze_path_below += "| {} {} ".format(data, wall)
                    elif (current_vertex.is_top_vertex and
                          current_vertex.is_left_vertex):
                        maze_path_below += "  {} {} ".format(data, wall)
                    else:
                        maze_path_below += "{} {} ".format(data, wall)
                    if current_vertex.is_top_vertex:
                        if current_vertex.is_exit_vertex:
                            top_layer += "  --"
                        else:
                            top_layer += "----"
                if current_vertex.is_right_vertex:
                    if current_vertex.is_exit_vertex:
                        maze_path_below += "{}".format(data)
                    else:
                        maze_path_below += "{}|".format(data)
                    if row == 0:
                        if current_vertex.is_exit_vertex:
                            top_layer += "    "
                        else:
                            top_layer += "----"
                if not current_vertex.is_top_vertex:
                    wall = self.current_maze.maze_graph.\
                            north_structure_from_vertex(current_vertex)
                    if current_vertex.is_left_vertex:
                        if current_vertex.is_exit_vertex:
                            if wall == self.current_maze.maze_graph.HWALL:
                                maze_path_above += "-  -"
                            elif wall == self.current_maze.maze_graph.EMPTY:
                                maze_path_above += "    "
                        else:
                            if wall == self.current_maze.maze_graph.HWALL:
                                maze_path_above += "|---"
                            elif wall == self.current_maze.maze_graph.EMPTY:
                                maze_path_above += "|   "
                    elif current_vertex.is_right_vertex:
                        if current_vertex.is_exit_vertex:
                            if wall == self.current_maze.maze_graph.HWALL:
                                maze_path_above += "--  "
                            elif wall == self.current_maze.maze_graph.EMPTY:
                                maze_path_above += "    "
                        else:
                            if wall == self.current_maze.maze_graph.HWALL:
                                maze_path_above += "---|"
                            elif wall == self.current_maze.maze_graph.EMPTY:
                                maze_path_above += "   |"
                    else:
                        if wall == self.current_maze.maze_graph.HWALL:
                            maze_path_above += "----"
                        elif wall == self.current_maze.maze_graph.EMPTY:
                            maze_path_above += "    "
                    if current_vertex.is_bottom_vertex:
                        if current_vertex.is_exit_vertex and (
                            current_vertex.is_left_vertex or
                            current_vertex.is_right_vertex
                        ):
                            bottom_layer += "    "
                        elif (current_vertex.is_left_vertex or
                              current_vertex.is_right_vertex):
                            bottom_layer += "----"
                        elif current_vertex.is_exit_vertex:
                            bottom_layer += "-  -"
                        else:
                            bottom_layer += "----"
            maze_path_above += "\n"
            maze_path_above += maze_path_below
            maze_path += maze_path_above
            maze_path += "\n"
        maze_path += bottom_layer
        top_layer += maze_path
        print(top_layer)


def reset_maze(**kwargs):
    GAME.reset_maze(**kwargs)


def collision_one_to_many(single_group, sprite_group,
                          callback):
    # collision detection between single_group and sprite_group
    colliding_shapes = pygame.sprite.spritecollide(
        single_group.sprite, sprite_group, False)
    callback(single_group.sprite, colliding_shapes)


def hoggy_collision_walls(sprite, colliding_shapes):
    for shape in colliding_shapes:
        # Moving right; Hit the left side of the wall
        if sprite.get_component('MOVABLE').velocity['x'] > 0:
            sprite.rect.right = shape.rect.left
        # Moving left; Hit right side of the wall
        elif sprite.get_component('MOVABLE').velocity['x'] < 0:
            sprite.rect.left = shape.rect.right
        # Moving up; Hit bottom of the wall
        elif sprite.get_component('MOVABLE').velocity['y'] < 0:
            sprite.rect.top = shape.rect.bottom
        # Moving down; Hit top of the wall
        elif sprite.get_component('MOVABLE').velocity['y'] > 0:
            sprite.rect.bottom = shape.rect.top


def hoggy_collision_tomatoes(sprite, colliding_pickups):
    for pickup in colliding_pickups:
        if pickup.get_component('PICKUPABLE').name_instance == "tomato":
            pickup.get_component('PICKUPABLE').picked_up = True
            sprite.get_state('INVENTORY').add_item(
                pickup.get_component('PICKUPABLE').name_instance)
            vertex = GAME.current_maze.vertex_from_x_y(
                pickup.x, pickup.y)
            # print("VERTEX WITH TOMATO: {}".format(vertex))
            vertex.has_tomato = False
            vertex.sprite_with_tomato = sprite
            if sprite.name_object == 'ai_hoggy':
                sprite.get_state('MAZE').rewards += 5


def handle_collisions():
    collision_one_to_many(GAME.current_objects[
        'MAIN_PLAYER'], GAME.current_objects[
            'MAZE_WALLS'], hoggy_collision_walls)
    collision_one_to_many(GAME.current_objects[
        'MAIN_PLAYER'], GAME.current_objects[
            'PICKUPS'], hoggy_collision_tomatoes)
    collision_one_to_many(GAME.current_objects[
        'AI_HOGGY'], GAME.current_objects[
            'PICKUPS'], hoggy_collision_tomatoes)


def game_initialize():
    global WORLD
    global FPS_CLOCK
    global DEBUGSCREEN
    global DEBUGEVENT
    global DEBUGM
    global DEBUGMAZESTATE

    pygame.init()

    DEBUGSCREEN = debuginfo.DebugInfo()
    DEBUGEVENT = debugevent.DebugEvent()
    DEBUGM = debugmouse.DebugMouse()
    DEBUGM.update("", "")
    DEBUGMAZESTATE = debugmazestate.DebugMazeState()
    WORLD = pygame.display.set_mode((settings.WINDOW_WIDTH +
                                     settings.HUD_OFFSETX,
                                     settings.WINDOW_HEIGHT +
                                     settings.HUD_OFFSETY))
    FPS_CLOCK = pygame.time.Clock()
    pygame.time.set_timer(AI_HOGGY_MOVE, MOVE_AI_HOGGY_TIMEOUT)


def game_new():
    global GAME
    GAME = Game()
    starting_vertex = GAME.current_maze.maze_graph.maze_layout[
        0][0]
    (x, y) = GAME.current_maze.center_for_vertex(starting_vertex)
    main_player = actor_obj.ActorObject(
        **{'x': x - (32 / 2),
           'y': y - (32 / 2),
           'height': 32, 'width': 32,
           'sprite_sheet_key': 0,
           'name_object': 'hoggy',
           'animation': AnimationComponent(),
           'player_input': PlayerInputComponent(),
           'orientation': OrientationComponent('horizontal', 'right'),
           'movable': MovableComponent('hoggy_move', 6),
           'inventory': InventoryState('tomato')
           })
    randomize_button = actor_obj.ActorObject(**{
        'x': settings.WINDOW_WIDTH - 200,
        'y': 0,
        'height': 64, 'width': 64,
        'in_hud': True,
        'sprite_sheet_key': 2,
        'name_object': 'randomize_button',
        'animation': AnimationComponent(),
        'clickable': ClickableComponent('circle', reset_maze,
                                        **settings.maze_starting_state)
    })
    ai_hoggy = actor_obj.ActorObject(
        **{'x': x - (32 / 2),
           'y': y - (32 / 2),
           'height': 32, 'width': 32,
           'sprite_sheet_key': 0,
           'name_object': 'ai_hoggy',
           'inventory': InventoryState('tomato'),
           'maze': MazeState('maze_state')
           })
    ai_hoggy.get_state('MAZE').reset_edge_visits(
        GAME.current_maze.maze_graph.edges)
    ai_hoggy.get_state(
        'MAZE').current_vertex = starting_vertex
    starting_vertex.increment_sprite_visit_count(ai_hoggy)
    GAME.main_player = main_player
    GAME.ai_hoggy = ai_hoggy
    GAME.current_objects['UI_BUTTONS'].add(randomize_button)


def handle_keys(event):
    DEBUGEVENT.update(event)
    if event.type == QUIT:
        return "QUIT"
    if event.type == KEYDOWN:
        if event.key == K_UP:
            GAME.main_player.get_component('PLAYER_INPUT').set_key_down('up')
        if event.key == K_DOWN:
            GAME.main_player.get_component('PLAYER_INPUT').set_key_down('down')
        if event.key == K_LEFT:
            GAME.main_player.get_component('PLAYER_INPUT').set_key_down('left')
        if event.key == K_RIGHT:
            GAME.main_player.get_component('PLAYER_INPUT').set_key_down(
                'right')
        if event.key == K_SPACE:
            GAME.main_player.get_component('PLAYER_INPUT').set_key_down('eat')
    if event.type == KEYUP:
        if event.key == K_UP:
            GAME.main_player.get_component('PLAYER_INPUT').set_key_up('up')
        if event.key == K_DOWN:
            GAME.main_player.get_component('PLAYER_INPUT').set_key_up('down')
        if event.key == K_LEFT:
            GAME.main_player.get_component('PLAYER_INPUT').set_key_up('left')
        if event.key == K_RIGHT:
            GAME.main_player.get_component('PLAYER_INPUT').set_key_up('right')
        if event.key == K_SPACE:
            GAME.main_player.get_component('PLAYER_INPUT').set_key_up('eat')
            GAME.main_player.get_component('PLAYER_INPUT').just_ate = False
        if event.key == K_d:
            settings.IS_DEBUG = not settings.IS_DEBUG
        if event.key == K_p:
            GAME.is_paused = True
    if event.type == MOUSEMOTION:
        mousex, mousey = event.pos
        DEBUGM.update(mousex, mousey)
        return "MOUSEMOTION"
    if event.type == MOUSEBUTTONUP:
        mousex, mousey = event.pos
        vertex = GAME.current_maze.vertex_from_x_y(
            mousex - settings.HUD_OFFSETX,
            mousey - settings.HUD_OFFSETY)
        if vertex:
            DEBUGMAZESTATE.update(vertex)
        return "MOUSEBUTTONUP"
    if event.type in [KEYDOWN, KEYUP]:
        return "player-movement"
    if event.type == AI_HOGGY_MOVE:
        if not GAME.ai_hoggy.get_state('MAZE').end:
            GAME.current_maze.step_for_sprite(
                GAME.ai_hoggy)
    if event.type == RELOADED_EVENT:
        # when the reload timer runs out, reset it
        # print("reloading")
        pygame.time.set_timer(RELOADED_EVENT, 0)
    return "no-action"


def game_loop():
    game_quit = False
    while not game_quit:
        while GAME.is_paused:
            events = pygame.event.get()
            for event in events:
                if event.type == MOUSEBUTTONUP:
                    mousex, mousey = event.pos
                    vertex = GAME.current_maze.vertex_from_x_y(
                        mousex - settings.HUD_OFFSETX,
                        mousey - settings.HUD_OFFSETY)
                    if vertex:
                        DEBUGMAZESTATE.update(vertex)
                        draw_game()
                        draw_debug(0)
                        pygame.display.update()
                if event.type == KEYUP and event.key == K_p:
                    GAME.is_paused = False
        dt = FPS_CLOCK.get_time()
        events = pygame.event.get()
        mousex, mousey = pygame.mouse.get_pos()
        # print([pygame.event.event_name(e.type) for e in events])
        if len(events) == 0:
            events.append("no-action")
        for event in events:
            if event == "no-action":
                event_type = event
            else:
                # print(pygame.event.event_name(event.type))
                event_type = handle_keys(event)
            if event_type == "QUIT":
                game_quit = True
                continue
            update_components(dt, mousex, mousey, event_type)
            handle_collisions()
        draw_game()

        if settings.IS_DEBUG:
            draw_debug(dt)
        # print(GAME.current_maze.maze_graph.exit_direction)

        pygame.display.update()
        FPS_CLOCK.tick(settings.FPS)


def main():
    game_initialize()
    game_new()
    game_loop()
    pygame.quit()


if __name__ == '__main__':
    main()