import pygame
import numpy as np


def collision_one_to_many(single_group, sprite_group,
                          callback, game):
    # collision detection between single_group and sprite_group
    colliding_shapes = pygame.sprite.spritecollide(
        single_group.sprite, sprite_group, False)
    if len(colliding_shapes) > 0:
        callback(single_group.sprite, colliding_shapes, game)


def collision_many_to_many(sprite_group_1, sprite_group_2,
                           callback, game):
    # collision detection between sprite_group and sprite_group
    for sprite in sprite_group_1:
        colliding_shapes = pygame.sprite.spritecollide(
            sprite, sprite_group_2, False)
        if len(colliding_shapes) > 0:
            callback(sprite, colliding_shapes, game)


def hoggy_collision_walls(sprite, colliding_shapes, game):
    tmp = []
    for shape in colliding_shapes:
        # Moving right; Hit the left side of the wall
        if sprite.get_component('MOVABLE').velocity['x'] > 0:
            print("HIT LEFT SIDE OF WALL")
            left_tmp = shape.rect.left
            tmp.append(left_tmp)
        # Moving left; Hit right side of the wall
        elif sprite.get_component('MOVABLE').velocity['x'] < 0:
            right_tmp = shape.rect.right
            tmp.append(right_tmp)
        # Moving up; Hit bottom of the wall
        elif sprite.get_component('MOVABLE').velocity['y'] < 0:
            bottom_tmp = shape.rect.bottom
            tmp.append(bottom_tmp)
        # Moving down; Hit top of the wall
        elif sprite.get_component('MOVABLE').velocity['y'] > 0:
            top_tmp = shape.rect.top
            tmp.append(top_tmp)
    # Moving right; Hit the left side of the wall
    if sprite.get_component('MOVABLE').velocity['x'] > 0:
        sprite.rect.right = np.min(tmp)
    # Moving left; Hit right side of the wall
    elif sprite.get_component('MOVABLE').velocity['x'] < 0:
        sprite.rect.left = np.max(tmp)
    # Moving up; Hit bottom of the wall
    elif sprite.get_component('MOVABLE').velocity['y'] < 0:
        sprite.rect.top = np.max(tmp)
    # Moving down; Hit top of the wall
    elif sprite.get_component('MOVABLE').velocity['y'] > 0:
        sprite.rect.bottom = np.min(tmp)
