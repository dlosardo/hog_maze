import pygame


def collision_one_to_many(single_group, sprite_group,
                          callback, game):
    # collision detection between single_group and sprite_group
    colliding_shapes = pygame.sprite.spritecollide(
        single_group.sprite, sprite_group, False)
    callback(single_group.sprite, colliding_shapes, game)


def collision_many_to_many(sprite_group_1, sprite_group_2,
                           callback, game):
    # collision detection between sprite_group and sprite_group
    for sprite in sprite_group_1:
        colliding_shapes = pygame.sprite.spritecollide(
            sprite, sprite_group_2, False)
        callback(sprite, colliding_shapes, game)


def hoggy_collision_walls(sprite, colliding_shapes, game):
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
