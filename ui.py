from my_sprite import MySprite
import settings
import pygame
from util.util_draw import draw_text


class UIButton(MySprite):

    def __init__(self, name, callback, x, y, width, height, text,
                 font_size, font=None,
                 text_color=settings.RED, bg_color=settings.GREEN,
                 text_color_mouseover=settings.GRAY,
                 bg_color_mouseover=settings.BLUE):
        MySprite.__init__(self)
        self.name = name
        self.callback = callback
        self.width = width
        self.height = height
        self.image = pygame.Surface(
            [self.width, self.height],
            pygame.SRCALPHA).convert_alpha()
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y

        self.text = text
        self.font_size = font_size
        self.font = font
        self.text_color = text_color
        self.bg_color = bg_color
        self.text_color_mouseover = text_color_mouseover
        self.bg_color_mouseover = bg_color_mouseover

        self.current_text_color = self.text_color
        self.current_bg_color = self.bg_color

        self.mouseover = False
        self.pressed = False
        self.draw()

    def update(self, mousex, mousey, input):
        if self.rect.collidepoint(mousex, mousey):
            self.current_text_color = self.text_color_mouseover
            self.current_bg_color = self.bg_color_mouseover
            self.mouseover = True
        else:
            self.current_text_color = self.text_color
            self.current_bg_color = self.bg_color
            self.mouseover = False
        if input == "MOUSEBUTTONUP":
            self.pressed = True
        else:
            self.pressed = False
        self.draw()
        if self.mouseover and self.pressed:
            self.callback()

    def draw(self):
        pygame.draw.rect(self.image, self.current_bg_color,
                         (0, 0, self.width, self.height))
        draw_text(self.image, self.text,
                  self.font_size, self.height // 2, self.width // 2,
                  self.current_text_color)
