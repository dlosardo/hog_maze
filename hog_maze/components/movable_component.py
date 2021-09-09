from hog_maze.components.component import HogMazeComponent


class MovableComponent(HogMazeComponent):
    def __init__(self, name_instance, speed):
        super(MovableComponent, self).__init__('MOVABLE')
        self.name_instance = name_instance
        self.speed = speed
        self.time_since_last_move = 0
        self.velocity = {'x': 0, 'y': 0}

    def update(self, **kwargs):
        self.owner.x += kwargs['dt'] * self.velocity['x']
        self.owner.y += kwargs['dt'] * self.velocity['y']
        # if self.owner.y < 0:
            # import pdb;
            # pdb.set_trace();

    def is_moving(self):
        return self.velocity['x'] != 0 or self.velocity['y'] != 0

    def reset_velocity(self):
        self.velocity['x'] = 0
        self.velocity['y'] = 0
