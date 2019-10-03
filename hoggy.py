import pygame
from pygame.locals import (
    QUIT, KEYDOWN, KEYUP, K_UP, K_DOWN,
    K_LEFT, K_RIGHT, MOUSEMOTION,
    MOUSEBUTTONUP, K_SPACE
)
import settings
import actor_obj
from util.util_draw import draw_text
from animation_component import AnimationComponent
from player_input_component import PlayerInputComponent
from movable_component import MovableComponent
from clickable_component import ClickableComponent
from orientation_component import OrientationComponent
from pickupable_component import PickupableComponent
from inventory_state import InventoryState
from maze_game import MazeGame
import debuginfo
import debugmouse
import debugevent

COMPONENTS = ['PLAYER_INPUT', 'MOVABLE', 'ORIENTATION',
              'ANIMATION', 'CLICKABLE', 'PICKUPABLE']

settings.IS_DEBUG = False


def update_components(dt, mousex, mousey, event_type):
    for component in COMPONENTS:
        for name, obj in GAME.current_objects.items():
            for sprite in obj:
                if sprite.is_dead:
                    sprite.kill()
                elif sprite.has_component(component):
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
                              (sprite.x, sprite.y)
                              )
                ntomatoes = GAME.current_objects[
                  'MAIN_PLAYER'].sprite.get_state(
                      'INVENTORY').inventory.get('tomato')
                if not ntomatoes:
                    ntomatoes = 0
                draw_text(GAME.hud, "Tomatoes: {}".format(ntomatoes),
                          24, 60, 10, settings.ORANGE)
    WORLD.blit(GAME.current_maze.image,
               (0, settings.HUD_OFFSETY))
    WORLD.blit(GAME.hud,
               (0, 0))


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
        self.current_maze = None
        self.reset_maze(**settings.maze_starting_state)
        self.hud = pygame.Surface([settings.WINDOW_WIDTH,
                                   settings.HUD_OFFSETY]
                                  ).convert()
        self.hud_rect = self.hud.get_rect()

    def reset_maze(self, maze_width, maze_height,
                   area_width, area_height,
                   wall_scale, starting_vertex_name=0):
        if self.current_maze:
            self.current_maze.reset()
            self.current_objects[
                'MAIN_PLAYER'].sprite.x = self.current_objects[
                'MAIN_PLAYER'].sprite.start_x
            self.current_objects[
                'MAIN_PLAYER'].sprite.y = self.current_objects[
                'MAIN_PLAYER'].sprite.start_y
        else:
            self.current_maze = MazeGame(maze_width, maze_height,
                                         area_width, area_height,
                                         wall_scale)
        self.current_maze.set_maze(starting_vertex_name)
        self.current_objects['PICKUPS'].empty()
        self.current_objects['MAZE_WALLS'].empty()
        self.current_objects['MAZE_WALLS'].add(
            self.current_maze.maze_walls)
        cubby_vertices = self.current_maze.maze_graph.all_cubby_vertices()
        if len(cubby_vertices) > 0:
            for cubby_vertex in cubby_vertices:
                x, y = self.current_maze.get_x_y_for_vertex(cubby_vertex)
                centerx = x + self.current_maze.cell_width / 2
                centery = y + self.current_maze.cell_height / 2
                x = centerx - 32/2
                y = centery - 32/2
                tomato = actor_obj.ActorObject(
                    **{'x': x, 'y': y, 'height': 32, 'width': 32,
                       'sprite_sheet_key': 3,
                       'name_object': 'tomato',
                       'animation': AnimationComponent(is_animating=True),
                       'pickupable': PickupableComponent('tomato')
                       })
                self.current_objects['PICKUPS'].add(tomato)


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
            print("GETTING TOMATO")
            sprite.get_state('INVENTORY').add_item(
                pickup.get_component('PICKUPABLE').name_instance)


def handle_collisions():
    collision_one_to_many(GAME.current_objects[
        'MAIN_PLAYER'], GAME.current_objects[
            'MAZE_WALLS'], hoggy_collision_walls)
    collision_one_to_many(GAME.current_objects[
        'MAIN_PLAYER'], GAME.current_objects[
            'PICKUPS'], hoggy_collision_tomatoes)


def game_initialize():
    global WORLD
    global FPS_CLOCK
    global DEBUGSCREEN
    global DEBUGEVENT
    global DEBUGM

    pygame.init()

    DEBUGSCREEN = debuginfo.DebugInfo()
    DEBUGEVENT = debugevent.DebugEvent()
    DEBUGM = debugmouse.DebugMouse()
    DEBUGM.update("", "")
    WORLD = pygame.display.set_mode((settings.WINDOW_WIDTH +
                                     settings.HUD_OFFSETX,
                                     settings.WINDOW_HEIGHT +
                                     settings.HUD_OFFSETY))
    FPS_CLOCK = pygame.time.Clock()


def game_new():
    global GAME
    GAME = Game()
    main_player = actor_obj.ActorObject(
        **{'x': 0, 'y': 12, 'height': 32, 'width': 32,
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

    GAME.current_objects['MAIN_PLAYER'].add(main_player)
    GAME.current_objects['UI_BUTTONS'].add(randomize_button)


def handle_keys(event):
    DEBUGEVENT.update(event)
    if event.type == QUIT:
        return "QUIT"
    if event.type == KEYDOWN:
        if event.key == K_UP:
            GAME.current_objects['MAIN_PLAYER'].\
                    sprite.get_component('PLAYER_INPUT').set_key_down('up')
        if event.key == K_DOWN:
            GAME.current_objects['MAIN_PLAYER'].\
                    sprite.get_component('PLAYER_INPUT').set_key_down('down')
        if event.key == K_LEFT:
            GAME.current_objects['MAIN_PLAYER'].\
                    sprite.get_component('PLAYER_INPUT').set_key_down('left')
        if event.key == K_RIGHT:
            GAME.current_objects['MAIN_PLAYER'].\
                    sprite.get_component('PLAYER_INPUT').set_key_down('right')
        if event.key == K_SPACE:
            GAME.current_objects['MAIN_PLAYER'].\
                    sprite.get_component('PLAYER_INPUT').set_key_down('eat')
    if event.type == KEYUP:
        if event.key == K_UP:
            GAME.current_objects['MAIN_PLAYER'].\
                    sprite.get_component('PLAYER_INPUT').set_key_up('up')
        if event.key == K_DOWN:
            GAME.current_objects['MAIN_PLAYER'].\
                    sprite.get_component('PLAYER_INPUT').set_key_up('down')
        if event.key == K_LEFT:
            GAME.current_objects['MAIN_PLAYER'].\
                    sprite.get_component('PLAYER_INPUT').set_key_up('left')
        if event.key == K_RIGHT:
            GAME.current_objects['MAIN_PLAYER'].\
                    sprite.get_component('PLAYER_INPUT').set_key_up('right')
        if event.key == K_SPACE:
            GAME.current_objects['MAIN_PLAYER'].\
                    sprite.get_component('PLAYER_INPUT').set_key_up('eat')
    if event.type == MOUSEMOTION:
        mousex, mousey = event.pos
        DEBUGM.update(mousex, mousey)
        return "MOUSEMOTION"
    if event.type == MOUSEBUTTONUP:
        mousex, mousey = event.pos
        return "MOUSEBUTTONUP"
    if event.type in [KEYDOWN, KEYUP]:
        return "player-movement"
    return "no-action"


def game_loop():
    game_quit = False
    while not game_quit:
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
                print(pygame.event.event_name(event.type))
                event_type = handle_keys(event)
            if event_type == "QUIT":
                game_quit = True
                continue
            update_components(dt, mousex, mousey, event_type)
            handle_collisions()
        draw_game()

        if settings.IS_DEBUG:
            DEBUGSCREEN.update(
                GAME.current_objects['MAIN_PLAYER'].sprite, dt)
            WORLD.blit(DEBUGSCREEN.text, (0, 465))
            WORLD.blit(DEBUGM.text, (0, 400))
            WORLD.blit(DEBUGEVENT.text, (0, 440))

        pygame.display.update()
        FPS_CLOCK.tick(settings.FPS)


def main():
    game_initialize()
    game_new()
    game_loop()
    pygame.quit()


if __name__ == '__main__':
    main()
