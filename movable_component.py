from component import HogMazeComponent


class MovableComponent(HogMazeComponent):
    def __init__(self, name_instance, speed):
        super(MovableComponent, self).__init__('MOVABLE')
        self.name_instance = name_instance
        self.speed = speed
        self.velocity = {'x': 0, 'y': 0}

    def update(self, **kwargs):
        self.owner.x += self.velocity['x']
        self.owner.y += self.velocity['y']

    def is_moving(self):
        return self.velocity['x'] != 0 or self.velocity['y'] != 0

    def reset_velocity(self):
        self.velocity['x'] = 0
        self.velocity['y'] = 0
