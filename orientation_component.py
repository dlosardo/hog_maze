from component import HogMazeComponent


class OrientationComponent(HogMazeComponent):
    def __init__(self, orientation, is_facing):
        super(OrientationComponent, self).__init__('ORIENTATION')
        self.orientation = orientation
        self.is_facing = is_facing

    def update(self, **kwargs):
        if self.owner.component_dict['MOVABLE'].velocity['y'] < 0:
            self.is_facing = 'up'
            self.orientation = 'vertical'
        if self.owner.component_dict['MOVABLE'].velocity['y'] > 0:
            self.is_facing = 'down'
            self.orientation = 'vertical'
        if self.owner.component_dict['MOVABLE'].velocity['x'] < 0:
            self.is_facing = 'left'
            self.orientation = 'horizontal'
        if self.owner.component_dict['MOVABLE'].velocity['x'] > 0:
            self.is_facing = 'right'
            self.orientation = 'horizontal'
