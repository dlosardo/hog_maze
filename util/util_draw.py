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
