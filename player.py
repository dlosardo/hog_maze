import pygame
import settings
from my_sprite import MySprite
from util.util import Point


class Player(MySprite):
    def __init__(self, point, speed_x, speed_y,
                 image_filename, frame_width,
                 frame_height, ncols,
                 animation_delay):
        MySprite.__init__(self)
        self.sprite_sheet = pygame.image.load(
            image_filename).convert_alpha()
        # animation
        self.time_since_last_move = 0
        self.frame = 0
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.ncols = ncols
        self.animation_delay = animation_delay
        self.old_frame = -1
        self.first_frame = 0
        self.last_frame = self.ncols - 1
        self.last_time = 0
        self.is_facing = 'left'
        self.orientation = 'horizontal'
        # image and attributes
        rect = (0, 0, frame_width, frame_height)
        self.image = self.sprite_sheet.subsurface(
            rect)
        self.rect = self.image.get_rect()
        self.x = point.x
        self.y = point.y
        self.start_position = (self.x, self.y)
        self.velocity = {'x': 0, 'y': 0}
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.previous_coords = Point(None, None)
        self.key_dict = {'up': False,
                         'down': False,
                         'left': False,
                         'right': False,
                         'space': False}

    def set_to_start_position(self):
        self.x = self.start_position[0]
        self.y = self.start_position[1]

    def set_key_down(self, event):
        self.key_dict[event] = True

    def set_key_up(self, event):
        self.key_dict[event] = False

    def reset_velocity(self):
        self.velocity = {'x': 0, 'y': 0}

    def move(self):
        if self.key_dict['up']:
            if self.y <= 0:
                self.y = 0
            else:
                self.velocity['y'] = -self.speed_y
            self.is_facing = 'up'
            self.orientation = 'vertical'
        elif self.key_dict['down']:
            if self.y >= (settings.WINDOW_HEIGHT - self.rect.height):
                self.velocity['y'] = 0
            else:
                self.velocity['y'] = self.speed_y
            self.is_facing = 'down'
            self.orientation = 'vertical'
        elif self.key_dict['left']:
            if self.x <= 0:
                self.velocity['x'] = 0
            else:
                self.velocity['x'] = -self.speed_x
            self.is_facing = 'left'
            self.orientation = 'horizontal'
        elif self.key_dict['right']:
            if self.x >= (settings.WINDOW_WIDTH - self.rect.width):
                self.velocity['x'] = 0
            else:
                self.velocity['x'] = self.speed_x
            self.is_facing = 'right'
            self.orientation = 'horizontal'

        self.previous_coords.x = self.x
        self.previous_coords.y = self.y
        self.x += self.velocity['x']
        self.y += self.velocity['y']

    def animate(self, dt):
        self.time_since_last_move = dt + self.time_since_last_move
        if self.time_since_last_move > self.animation_delay:
            self.time_since_last_move = 0
            self.frame += 1
            if self.frame > self.last_frame:
                self.frame = self.first_frame
            if self.frame != self.old_frame:
                frame_x = (self.frame % self.ncols) * self.frame_width
                frame_y = (self.frame // self.ncols) * self.frame_height
                if self.orientation == 'vertical':
                    frame_y = frame_y + self.frame_height
                rect = (frame_x, frame_y, self.frame_width, self.frame_height)
                self.image = self.sprite_sheet.subsurface(rect)
                if (self.orientation == 'horizontal' and
                        self.is_facing == 'right'):
                    self.image = pygame.transform.flip(self.image, True, False)
                if (
                    self.orientation == 'vertical'
                    and self.is_facing == 'up'
                ):
                    self.image = pygame.transform.flip(self.image, False, True)
                self.old_frame = self.frame

    def update(self, dt):
        self.reset_velocity()
        self.move()
        if self.velocity['x'] != 0 or self.velocity['y'] != 0:
            self.animate(dt)
