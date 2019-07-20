import pygame


class MySprite(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = None
        self.rect = None

    def load(self):
        pass

    def set_image(self):
        pass

    @property
    def x(self):
        return self.rect.x

    @x.setter
    def x(self, x):
        self.rect.x = x

    @property
    def y(self):
        return self.rect.y

    @y.setter
    def y(self, y):
        self.rect.y = y
