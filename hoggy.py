import pygame
from pygame.locals import (
    QUIT, KEYDOWN, KEYUP, K_UP, K_DOWN,
    K_LEFT, K_RIGHT, MOUSEMOTION,
    MOUSEBUTTONUP
)
import settings
from player import Player
from maze_game import MazeGame
from ui import UIButton
import debuginfo
import debugmouse
import debugevent


class MySpriteGroup(pygame.sprite.Group):
    def __init__(self, type):
        pygame.sprite.Group.__init__(self)
        self.type = type


def maze_create():
    maze_game = MazeGame(**settings.maze_starting_state)
    maze_game.set_maze(0)
    return maze_game


class Game():
    def __init__(self):
        self.current_objects = {}
        self.current_maze = maze_create()
        maze_walls = MySpriteGroup('MAZE_WALLS')
        maze_walls.add(self.current_maze.maze_walls)
        self.current_objects.update({'MAZE_WALLS': maze_walls})

    def reset_maze(self, starting_vertex_name=0):
        self.current_maze.reset()
        self.current_maze.set_maze(
            starting_vertex_name)
        self.current_objects['MAZE_WALLS'].empty()
        self.current_objects['MAZE_WALLS'].add(
            self.current_maze.maze_walls)
        self.current_objects['MAIN_PLAYER'].sprite.set_to_start_position()


def reset_maze():
    GAME.reset_maze()


def collision_one_to_many(single_group, sprite_group,
                          callback):
    # collision detection between single_group and sprite_group
    colliding_shapes = pygame.sprite.spritecollide(
        single_group.sprite, sprite_group, False)
    callback(single_group.sprite, colliding_shapes)


def hoggy_collision_walls(sprite, colliding_shapes):
    for shape in colliding_shapes:
        # Moving right; Hit the left side of the wall
        if sprite.velocity['x'] > 0:
            sprite.rect.right = shape.rect.left
            shape.bg_color = 'red'
            shape.is_colliding = True
        # Moving left; Hit right side of the wall
        elif sprite.velocity['x'] < 0:
            sprite.rect.left = shape.rect.right
            shape.bg_color = 'blue'
            shape.is_colliding = True
        # Moving up; Hit bottom of the wall
        elif sprite.velocity['y'] < 0:
            sprite.rect.top = shape.rect.bottom
            shape.bg_color = 'green'
            shape.is_colliding = True
        # Moving down; Hit top of the wall
        elif sprite.velocity['y'] > 0:
            sprite.rect.bottom = shape.rect.top
            shape.bg_color = 'orange'
            shape.is_colliding = True


def draw_game():
    WORLD.fill(settings.WHITE)
    for name, obj in GAME.current_objects.items():
        obj.draw(WORLD)


def handle_keys(event):
    DEBUGEVENT.update(event)
    if event.type == QUIT:
        return "QUIT"
    if event.type == KEYDOWN:
        if event.key == K_UP:
            GAME.current_objects['MAIN_PLAYER'].sprite.set_key_down('up')
        if event.key == K_DOWN:
            GAME.current_objects['MAIN_PLAYER'].sprite.set_key_down('down')
        if event.key == K_LEFT:
            GAME.current_objects['MAIN_PLAYER'].sprite.set_key_down('left')
        if event.key == K_RIGHT:
            GAME.current_objects['MAIN_PLAYER'].sprite.set_key_down('right')
    if event.type == KEYUP:
        if event.key == K_UP:
            GAME.current_objects['MAIN_PLAYER'].sprite.set_key_up('up')
        if event.key == K_DOWN:
            GAME.current_objects['MAIN_PLAYER'].sprite.set_key_up('down')
        if event.key == K_LEFT:
            GAME.current_objects['MAIN_PLAYER'].sprite.set_key_up('left')
        if event.key == K_RIGHT:
            GAME.current_objects['MAIN_PLAYER'].sprite.set_key_up('right')
    if event.type in [KEYDOWN, KEYUP]:
        return "player-movement"
    if event.type == MOUSEMOTION:
        mousex, mousey = event.pos
        DEBUGM.update(mousex, mousey)
        return "MOUSEMOTION"
    if event.type == MOUSEBUTTONUP:
        mousex, mousey = event.pos
        return "MOUSEBUTTONUP"


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

    WORLD = pygame.display.set_mode((settings.WINDOW_WIDTH,
                                     settings.WINDOW_HEIGHT))
    FPS_CLOCK = pygame.time.Clock()


def game_new():
    global GAME
    GAME = Game()
    hoggy = Player(**settings.hoggy_starting_state)
    hoggy_sprite = pygame.sprite.GroupSingle(hoggy)

    ui_button_group = MySpriteGroup('UI_BUTTON')
    randomize_button = UIButton(
        'randomize', reset_maze,
        settings.WINDOW_WIDTH - 200,
        20, 100, 100, "Randomize", 24)
    ui_button_group.add([randomize_button])

    GAME.current_objects.update(
        {'UI_BUTTONS': ui_button_group})
    GAME.current_objects.update(
        {'MAIN_PLAYER': hoggy_sprite})


def game_loop():
    game_quit = False
    while not game_quit:
        FPS_CLOCK.tick(settings.FPS)
        ticks = pygame.time.get_ticks()
        for event in pygame.event.get():
            input = handle_keys(event)
            if input == "QUIT":
                game_quit = True
                continue
            mousex, mousey = pygame.mouse.get_pos()
            for button in GAME.current_objects['UI_BUTTONS']:
                button.update(mousex, mousey, input)
        GAME.current_objects['MAIN_PLAYER'].update(ticks)
        collision_one_to_many(GAME.current_objects[
            'MAIN_PLAYER'], GAME.current_objects[
                'MAZE_WALLS'], hoggy_collision_walls)
        for wall in GAME.current_objects['MAZE_WALLS'].sprites():
            if not wall.is_colliding:
                wall.reset_color()
            wall.is_colliding = False
            wall.draw()
        draw_game()
        if settings.IS_DEBUG:
            DEBUGSCREEN.update(
                GAME.current_objects['MAIN_PLAYER'].sprite, ticks)
            WORLD.blit(DEBUGSCREEN.text, (0, 465))
            WORLD.blit(DEBUGM.text, (0, 400))
            WORLD.blit(DEBUGEVENT.text, (0, 440))
        pygame.display.update()


def main():
    game_initialize()
    game_new()
    game_loop()
    pygame.quit()


if __name__ == '__main__':
    main()
