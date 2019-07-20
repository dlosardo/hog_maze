import pygame
import settings
from my_sprite import MySprite


class SpriteShape(MySprite):
    def __init__(self, x, y, width, height, bg_color):
        MySprite.__init__(self)
        self.width = width
        self.height = height
        self.image = pygame.Surface(
            [self.width, self.height],
            pygame.SRCALPHA).convert_alpha()
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.starting_bg_color = bg_color
        self.bg_color = bg_color
        self.is_colliding = False
        self.draw()

    def draw_shape(self, shape):
        if shape == 'rect':
            self.shape = pygame.draw.rect(
                self.image, settings.ColorFactory.get_color(self.bg_color),
                (0, 0, self.width, self.height))
        elif shape == 'circle':
            self.shape = pygame.draw.circle(
                self.image, settings.ColorFactory.get_color(self.bg_color),
                (10, 10), self.height // 2, 0)

    def draw(self):
        self.draw_shape('rect')

    def reset_color(self):
        self.bg_color = self.starting_bg_color
