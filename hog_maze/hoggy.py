import pygame
from pygame.locals import (
    QUIT, KEYDOWN, KEYUP, K_UP, K_DOWN,
    K_LEFT, K_RIGHT, MOUSEMOTION,
    MOUSEBUTTONUP, K_SPACE, K_d, K_p,
    K_c
)
import hog_maze.settings as settings
import hog_maze.actor_obj as actor_obj
from hog_maze.game import Game
from hog_maze.components.animation_component import AnimationComponent
from hog_maze.components.player_input_component import PlayerInputComponent
from hog_maze.components.movable_component import MovableComponent
from hog_maze.components.clickable_component import ClickableComponent
from hog_maze.components.orientation_component import OrientationComponent
from hog_maze.components.ai_component import AIComponent
from hog_maze.components.rilearning_component import RILearningComponent
from hog_maze.states.inventory_state import InventoryState
from hog_maze.states.maze_state import MazeState
import hog_maze.debug.debuginfo as debuginfo
import hog_maze.debug.debugmouse as debugmouse
import hog_maze.debug.debugevent as debugevent
import hog_maze.debug.debugmazestate as debugmazestate

MOVE_AI_HOGGY_TIMEOUT = 1000
AI_HOGGY_MOVE = pygame.USEREVENT + 1
RELOADED_EVENT = pygame.USEREVENT + 2

COMPONENTS = ['RILEARNING', 'PLAYER_INPUT', 'AI', 'MOVABLE', 'ORIENTATION',
              'ANIMATION', 'CLICKABLE', 'PICKUPABLE']


def update_components(dt, mousex, mousey, event_type):
    for component in COMPONENTS:
        for name, obj in GAME.current_objects.items():
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


def draw_game():
    WORLD.fill(settings.WHITE)
    GAME.current_maze.image.fill(settings.WHITE)
    GAME.hud.fill(settings.BLACK)

    for name, obj in GAME.current_objects.items():
        for sprite in obj:
            if not sprite.in_hud:
                GAME.current_maze.image.blit(sprite.image,
                                             (sprite.x, sprite.y))
            else:
                GAME.hud.blit(sprite.image, (sprite.x, sprite.y))
                GAME.draw_to_hud()
    WORLD.blit(GAME.current_maze.image, (0, settings.HUD_OFFSETY))
    WORLD.blit(GAME.hud, (0, 0))


def draw_debug(dt):
    DEBUGSCREEN.update(GAME.ai_hoggy, dt)
    # for i, t in enumerate(DEBUGSCREEN.text_list):
    # WORLD.blit(t, (0, 465 + (i * 30)))
    WORLD.blit(DEBUGM.text, (0, 400))
    # WORLD.blit(DEBUGEVENT.text, (0, 440))
    for i, t in enumerate(DEBUGMAZESTATE.text_list):
        WORLD.blit(t, (0, 500 + (i * 30)))


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
            print("pick up tomato")
            vertex = GAME.current_maze.vertex_from_x_y(
                pickup.x, pickup.y)
            vertex.has_tomato = False
            vertex.sprite_with_tomato = sprite
            for sp in GAME.current_objects['AI_HOGGY']:
                sp.get_component('RILEARNING').recalc = True


def collision_ai_destinations(sprite_group):
    for sprite in sprite_group:
        if not sprite.get_state('MAZE').end:
            if sprite.get_component('AI').reached_destination():
                if sprite.has_component('RILEARNING'):
                    current_vertex = GAME.current_maze.vertex_from_x_y(
                        *sprite.coords)
                    next_dest = GAME.current_maze.next_dest_from_pi_a_s(
                        sprite.get_component('RILEARNING').pi_a_s,
                        current_vertex, sprite)
                    sprite.get_component('AI').destination = next_dest


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
    collision_ai_destinations(GAME.current_objects[
        'AI_HOGGY'])


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
    # pygame.time.set_timer(AI_HOGGY_MOVE, MOVE_AI_HOGGY_TIMEOUT)


def game_new():
    global GAME
    GAME = Game()
    starting_vertex = GAME.current_maze.maze_graph.start_vertex
    (x, y) = GAME.current_maze.center_for_vertex(starting_vertex)
    print("CENTER X: {}, CENTER Y: {}".format(x, y))
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
                                       settings.HOGGY_STARTING_STATS['speed']),
           'inventory': InventoryState('tomato')
           })

    print("HOGGY X: {}, HOGGY Y: {}".format(main_player.x,
                                            main_player.y))
    randomize_button = actor_obj.ActorObject(**{
        'x': settings.WINDOW_WIDTH - 200,
        'y': 0,
        'height': settings.SPRITE_SIZE * 2,
        'width': settings.SPRITE_SIZE * 2,
        'in_hud': True,
        'sprite_sheet_key': 2,
        'name_object': 'randomize_button',
        'animation': AnimationComponent(),
        'clickable': ClickableComponent('circle', reset_maze,
                                        **settings.MAZE_STARTING_STATE)
    })
    ai_hoggy = actor_obj.ActorObject(
        **{'x': x - (settings.SPRITE_SIZE / 2),
           'y': y - (settings.SPRITE_SIZE / 2),
           'height': settings.SPRITE_SIZE, 'width': settings.SPRITE_SIZE,
           'sprite_sheet_key': settings.AI_HOGGY_STARTING_STATS[
               'sprite_sheet_key'],
           'name_object': 'ai_hoggy',
           'inventory': InventoryState('tomato'),
           'maze': MazeState('maze_state'),
           'animation': AnimationComponent(),
           'orientation': OrientationComponent('horizontal', 'right'),
           'movable': MovableComponent(
               'ai_hoggy_move', settings.AI_HOGGY_STARTING_STATS['speed']),
           'ai': AIComponent(),
           'rilearning':
           RILearningComponent(
               name_instance="ril_ai_hoggy",
               gamma=settings.AI_HOGGY_STARTING_STATS['gamma'],
               nstates=GAME.current_maze.maze_width * GAME.
               current_maze.maze_height,
               action_space=GAME.action_space, actions=GAME.actions,
               reward_dict=settings.AI_HOGGY_STARTING_STATS['reward_dict'],
               reward_func=GAME.current_maze.maze_graph.set_rewards_table,
               pi_a_s_func=GAME.current_maze.maze_graph.get_pi_a_s)
           })
    ai_hoggy.get_state('MAZE').reset_edge_visits(
        GAME.current_maze.maze_graph.edges)
    ai_hoggy.get_state('MAZE').current_vertex = starting_vertex
    starting_vertex.increment_sprite_visit_count(ai_hoggy)
    ai_hoggy.get_component('RILEARNING').update()
    next_dest = GAME.current_maze.next_dest_from_pi_a_s(
        ai_hoggy.get_component('RILEARNING').pi_a_s,
        starting_vertex, ai_hoggy)
    ai_hoggy.get_component('AI').destination = next_dest
    GAME.main_player = main_player
    GAME.ai_hoggy = ai_hoggy
    # GAME.ai_hoggy.get_component('AI').destination = GAME.main_player

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
        if event.key == K_c:
            GAME.toggle_alg()
            alg_dict = {True: 'Max', False: 'Dist'}
            print("Alg: {}".format(alg_dict[GAME.max_alg]))
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
    # if event.type == AI_HOGGY_MOVE:
        # print("AI HOGGY MOVE EVENT HAPPENING")
        # if not GAME.ai_hoggy.get_state('MAZE').end:
        # pass
        # GAME.current_maze.step_for_sprite(
        # GAME.ai_hoggy)
    # if event.type == RELOADED_EVENT:
        # print("RELOADED EVENT HAPPENING")
        # when the reload timer runs out, reset it
        # print("reloading")
        # pygame.time.set_timer(RELOADED_EVENT, 0)
    return "no-action"


def handle_event_paused(event):
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


def game_loop():
    game_quit = False
    while not game_quit:
        while GAME.is_paused:
            events = pygame.event.get()
            for event in events:
                handle_event_paused(event)
        dt = FPS_CLOCK.get_time()
        events = pygame.event.get()
        mousex, mousey = pygame.mouse.get_pos()
        if len(events) == 0:
            events.append("no-action")
        for event in events:
            if event == "no-action":
                event_type = event
            else:
                event_type = handle_keys(event)
            if event_type == "QUIT":
                game_quit = True
                continue
            update_components(dt, mousex, mousey, event_type)
            handle_collisions()
        draw_game()

        if settings.IS_DEBUG:
            draw_debug(dt)

        pygame.display.update()
        FPS_CLOCK.tick(settings.FPS)


def main():
    game_initialize()
    game_new()
    game_loop()
    pygame.quit()


if __name__ == '__main__':
    main()
