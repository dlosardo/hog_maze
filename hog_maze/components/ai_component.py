from hog_maze.components.component import HogMazeComponent


class AIComponent(HogMazeComponent):
    def __init__(self, destination=None, direction=None):
        super(AIComponent, self).__init__('AI')
        self.destination = destination
        self.direction = direction

    def move_towards(self, other, speed_x, speed_y):
        dx = other.x - self.owner.x
        dy = other.y - self.owner.y
        if dx > 0:
            dx = 1
        elif dx < 0:
            dx = -1
        if dy > 0:
            dy = 1
        elif dy < 0:
            dy = -1
        if self.sprite_within_x_range(speed_x):
            self.owner.component_dict['MOVABLE'].velocity['x'] =  \
                int(self.destination.x) - self.owner.x
        else:
            self.owner.component_dict['MOVABLE'].velocity['x'] = dx * \
                speed_x
        if self.sprite_within_y_range(speed_y):
            self.owner.component_dict['MOVABLE'].velocity['y'] =  \
                 int(self.destination.y) - self.owner.y
        else:
            self.owner.component_dict['MOVABLE'].velocity['y'] = dy * \
                speed_y

    def sprite_within_x_range(self, range_value):
        within_x_range = (
            self.owner.x <= (int(self.destination.x) + range_value)
            and
            self.owner.x >= (int(self.destination.x) - range_value)
        )
        return within_x_range

    def sprite_within_y_range(self, range_value):
        within_y_range = (
            self.owner.y <= (int(self.destination.y) + range_value)
            and
            self.owner.y >= (int(self.destination.y) - range_value)
        )
        return within_y_range

    def reached_destination(self):
        return (
            self.sprite_within_x_range(0)
            and
            self.sprite_within_y_range(0)
        )

    def update(self, **kwargs):
        speed_x = speed_y = self.owner.component_dict[
            'MOVABLE'].speed
        self.owner.component_dict['MOVABLE'].reset_velocity()
        if self.destination:
            if self.reached_destination():
                if self.owner.get_state("MAZE").path.empty():
                    self.destination = None
                else:
                    next_vertex = self.owner.get_state("MAZE").path.get()
                    self.destination = next_vertex
            if self.destination:
                self.move_towards(self.destination, speed_x, speed_y)
        if self.owner.component_dict['MOVABLE'].is_moving():
            self.owner.component_dict['ANIMATION'].is_animating = True
        else:
            self.owner.component_dict['ANIMATION'].is_animating = False
            self.owner.component_dict['MOVABLE'].reset_velocity()
