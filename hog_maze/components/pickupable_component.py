from hog_maze.components.component import HogMazeComponent


class PickupableComponent(HogMazeComponent):

    def __init__(self, name_instance):
        super(PickupableComponent, self).__init__('PICKUPABLE')
        self.picked_up = False
        self.holder = None
        self.name_instance = name_instance

    def update(self, **kwargs):
        if self.picked_up:
            self.owner.is_dead = True
