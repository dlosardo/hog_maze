import pygame

pygame.init()

screen = pygame.display.set_mode((640, 480))

red = (255, 0, 0)

white = (255, 255, 255)
while True:
    screen.fill(white)

    pygame.draw.rect(screen, red, (0, 0, 100, 100), 0)
    pygame.display.update()
