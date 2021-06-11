import numpy as np
from hog_maze.components.component import HogMazeComponent


class AIComponent(HogMazeComponent):
    def __init__(self, destination=None):
        super(AIComponent, self).__init__('AI')
        self.destination = destination

    def move_towards(self, other, speed_x, speed_y, dt):
        if dt > 0:
            dx = np.sign(other.x - self.owner.x)
            dy = np.sign(other.y - self.owner.y)
            self.owner.component_dict['MOVABLE'].velocity['x'] = \
                min(abs(int(other.x) - self.owner.x),
                    dt * speed_x)/dt * dx
            self.owner.component_dict['MOVABLE'].velocity['y'] = \
                min(abs(int(other.y) - self.owner.y),
                    dt * speed_y)/dt * dy

    def sprite_within_x_range(self, other, range_value):
        within_x_range = (
            self.owner.x <= (int(other.x) + range_value)
            and
            self.owner.x >= (int(other.x) - range_value)
        )
        return within_x_range

    def sprite_within_y_range(self, other, range_value):
        within_y_range = (
            self.owner.y <= (int(other.y) + range_value)
            and
            self.owner.y >= (int(other.y) - range_value)
        )
        return within_y_range

    def reached_destination(self):
        return (
            self.sprite_within_x_range(self.destination, 0)
            and
            self.sprite_within_y_range(self.destination, 0)
        )

    def sprite_within_range(self, other, range):
        return (
            self.sprite_within_x_range(other, range)
            and
            self.sprite_within_y_range(other, range)
        )

    def update(self, **kwargs):
        speed_x = speed_y = self.owner.component_dict[
            'MOVABLE'].speed
        dt = kwargs['dt']
        self.owner.component_dict['MOVABLE'].reset_velocity()
        # if self.owner.has_component('RILEARNING'):
            # if not self.owner.get_component('RILEARNING').converged:
                # return
        if self.destination:
            try:
                dest_name = self.destination.name_object
            except Exception:
                dest_name = None
            if dest_name is not None and dest_name == 'hoggy':
                if not self.sprite_within_range(self.destination, 64):
                    self.move_towards(self.destination, speed_x, speed_y,
                                      dt)
            else:
                self.move_towards(self.destination, speed_x, speed_y, dt)
        if self.owner.component_dict['MOVABLE'].is_moving():
            self.owner.component_dict['ANIMATION'].is_animating = True
        else:
            self.owner.component_dict['ANIMATION'].is_animating = False
            self.owner.component_dict['MOVABLE'].reset_velocity()
