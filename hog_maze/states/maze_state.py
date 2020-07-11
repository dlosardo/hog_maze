from hog_maze.states.state import HogMazeState


class MazeState(HogMazeState):

    def __init__(self, name_instance):
        super(MazeState, self).__init__('MAZE')
        self.path = []
        self.edge_visits = {}
        self.name_instance = name_instance
        self.owner = None
        self.current_vertex = None
        self.rewards = 0
        self.end = False

    def reset_edge_visits(self, edges):
        for edge in edges:
            self.edge_visits[edge] = False

    def reset_rewards(self):
        self.rewards = 0

    def reset_maze_state(self, edges):
        self.reset_edge_visits(edges)
        self.reset_rewards()
        self.path = []
        self.end = False

    def print_state(self):
        text = "Position: {}, Rewards: {}".format(
            self.coord, self.rewards)
        return text

    @property
    def north_wall(self):
        if self.current_vertex:
            return self.current_vertex.north_wall
        else:
            return None

    @property
    def south_wall(self):
        if self.current_vertex:
            return self.current_vertex.south_wall
        else:
            return None

    @property
    def east_wall(self):
        if self.current_vertex:
            return self.current_vertex.east_wall
        else:
            return None

    @property
    def west_wall(self):
        if self.current_vertex:
            return self.current_vertex.west_wall
        else:
            return None

    @property
    def has_tomato(self):
        if self.current_vertex:
            return self.current_vertex.has_tomato
        else:
            return None

    @property
    def coord(self):
        if self.current_vertex:
            return (self.current_vertex.row,
                    self.current_vertex.col)
        else:
            return None
