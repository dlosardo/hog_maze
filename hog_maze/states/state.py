class HogMazeState():
    state_id_counter = 0

    def __init__(self, state_type):
        self._state_type = state_type
        self.owner = None
        self._id = HogMazeState.state_id_counter
        HogMazeState.state_id_counter += 1

    def get_state_type(self):
        return self._state_type
