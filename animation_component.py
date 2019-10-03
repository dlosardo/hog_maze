import pygame
from component import HogMazeComponent


class AnimationComponent(HogMazeComponent):
    def __init__(self, is_animating=False):
        super(AnimationComponent, self).__init__('ANIMATION')
        # animation
        self.frame = 0
        self.old_frame = -1
        self.first_frame = 0
        self.last_frame = 0
        self.last_time = 0
        self.time_since_last_move = 0
        self.is_animating = is_animating

    def update(self, **kwargs):
        dt = kwargs['dt']
        if self.is_animating:
            self.time_since_last_move = dt + self.time_since_last_move
            if self.time_since_last_move > self.owner.animation_delay:
                self.time_since_last_move = 0
                self.frame += 1
                if self.frame > self.last_frame:
                    self.frame = self.first_frame
                if self.frame != self.old_frame:
                    frame_x = (
                        self.frame % self.owner.ncols) * self.owner.width
                    frame_y = (
                        self.frame // self.owner.ncols) * self.owner.height
                    if self.owner.has_component('ORIENTATION'):
                        if self.owner.get_component('ORIENTATION')\
                           .orientation == 'vertical':
                            frame_y = frame_y + self.owner.height
                    rect = (
                        frame_x, frame_y, self.owner.width, self.owner.height)
                    self.owner.image = self.owner.sprite_sheet.subsurface(
                        rect)
                    self.old_frame = self.frame
                    if self.owner.has_component('ORIENTATION'):
                        if (
                            self.owner.get_component('ORIENTATION')
                            .orientation == 'horizontal' and self.owner
                            .get_component('ORIENTATION')
                            .is_facing == 'right'
                        ):
                            self.owner.image = pygame.transform.flip(
                                self.owner.image, True, False)
                    if self.owner.has_component('ORIENTATION'):
                        if self.owner.get_component('ORIENTATION').\
                           orientation == 'vertical' and self.owner.\
                           get_component('ORIENTATION').is_facing == 'up':
                            self.owner.image = pygame.transform.flip(
                                self.owner.image, False, True)
