from state import HogMazeState


class MazeState(HogMazeState):

    def __init__(self, name_instance):
        super(MazeState, self).__init__('MAZE')
        self.path = []
        self.edge_visits = {}
        self.name_instance = name_instance
        self.owner = None

    def reset_edge_visits(self, edges):
        for edge in edges:
            self.edge_visits[edge] = False
