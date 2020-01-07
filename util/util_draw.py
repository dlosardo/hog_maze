import pygame


def draw_text(display_surface, text_to_display, font_size,
              x, y, text_color, bg_color=None, font=None,
              center=True):
    font_obj = pygame.font.Font(font, font_size)
    text_surface = font_obj.render(
        text_to_display, True, text_color, bg_color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.centerx = x
        text_rect.centery = y
    else:
        text_rect.topleft = x
        text_rect.topleft = y
    display_surface.blit(text_surface, text_rect)


def draw_text_multiline(display_surface, text_to_display,
                        font_size, x, y, text_color,
                        bg_color=None, font=None, center=True):
    lines = text_to_display.splitlines()
    text_surface_list = []
    font_obj = pygame.font.Font(font, font_size)
    for l in lines:
        text_surface_list.append(font_obj.render(
            l, True, text_color, bg_color))
    for i, text in enumerate(text_surface_list):
        display_surface.blit(
            text, (x, y + (i * 30)))
