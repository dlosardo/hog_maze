class HogMazeComponent():
    component_id_counter = 0

    def __init__(self, component_type):
        self._component_type = component_type
        self.is_dead = False
        self.owner = None
        self._id = HogMazeComponent.component_id_counter
        HogMazeComponent.component_id_counter += 1

    def update(self, *args):
        raise NotImplementedError

    def get_component_type(self):
        return self._component_type
