import random
from collections import defaultdict
from hog_maze.util.stack import StackArray


class Vertex(object):
    def __init__(self, name):
        self.name = name
        self.is_visited = False
        self.is_top_vertex = False
        self.is_left_vertex = False
        self.is_right_vertex = False
        self.is_bottom_vertex = False
        self.is_entrance_vertex = False
        self.is_exit_vertex = False

        self.north_wall = True
        self.south_wall = True
        self.east_wall = True
        self.west_wall = True

        self.row = None
        self.col = None

        self.has_tomato = False
        self.sprite_with_tomato = None
        self.sprite_visits = defaultdict(int)

    def __str__(self):
        return "{}".format(self.name)

    def text_state(self):
        sprite_with_tomato = "None"
        if self.sprite_with_tomato:
            sprite_with_tomato = self.sprite_with_tomato.name_object
        text = "WALL NORTH: {}, WALL SOUTH: {}, WALL EAST: {} WALL WEST: {}\n"\
               "HAS TOMATO: {}, SPRITE WITH TOMATO: {}\n"\
               "NAME: {}, ROW: {}, COL: {}\n"\
               "SPRITE VISITS: {}\n"\
               "IS EXIT VERTEX: {} IS ENTRANCE VERTEX {}\n"\
               "TOP VERTEX: {}, RIGHT VERTEX: {}".format(
                    self.north_wall, self.south_wall,
                    self.east_wall, self.west_wall,
                    self.has_tomato,
                    sprite_with_tomato,
                    self.name, self.row, self.col,
                    self.sprite_visits,
                    self.is_exit_vertex,
                    self.is_entrance_vertex,
                    self.is_top_vertex,
                    self.is_right_vertex
               )
        return text

    def __lt__(self, other):
        return self.name < other.name

    def __gt__(self, other):
        return self.name > other.name

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.name)

    def increment_sprite_visit_count(self, sprite):
        self.sprite_visits[sprite.name_object] += 1

    @property
    def is_gateway(self):
        return self.is_entrance_vertex or self.is_exit_vertex

    @property
    def is_side_vertex(self):
        return self.is_left_vertex or self.is_right_vertex

    @property
    def is_top_bottom_vertex(self):
        return self.is_top_vertex or self.is_bottom_vertex

    @property
    def is_perimeter_vertex(self):
        return self.is_side_vertex or self.is_top_bottom_vertex

    @property
    def is_corner_vertex(self):
        return (self.is_top_vertex and self.is_right_vertex) or\
                (self.is_top_vertex and self.is_left_vertex) or\
                (self.is_bottom_vertex and self.is_right_vertex) or\
                (self.is_bottom_vertex and self.is_left_vertex)


class MazeGraph(object):
    EMPTY = " "
    HWALL = "-"
    VWALL = "|"

    def __init__(self, maze_width=4, maze_height=3):
        self.maze_width = maze_width
        self.maze_height = maze_height
        self.reset()
        self.path = []
        self.npaths = 0

    def reset(self):
        self.graph = {}
        self.edges = {}
        self.edges_visits = {}
        self.start_vertex = None
        self.end_vertex = None
        self.entrance_direction = None
        self.exit_direction = None
        self.stack = StackArray(200)
        self.maze_layout = [[None] * self.maze_width
                            for i in range(0, self.maze_height)
                            ]

    def set_rewards_table(self, actions):
        rewards_table = defaultdict(int)
        for row in range(0, self.maze_height):
            for col in range(0, self.maze_width):
                vertex = self.maze_layout[row][col]
                rewards_table[vertex.name] = {
                    a: [self.next_state_for_action(a, vertex)]
                    for a in actions
                }
        return rewards_table

    def found_exit(self, a, vertex):
        if (a == 0 and vertex.is_exit_vertex and
            self.exit_direction == 'TOP') or (
                a == 1 and vertex.is_exit_vertex and self.exit_direction ==
                'BOTTOM') or (
                    a == 2 and vertex.is_exit_vertex and self.exit_direction ==
                    'RIGHT') or (
                        a == 3 and vertex.is_exit_vertex and
                        self.exit_direction == 'LEFT'):
            return True
        else:
            return False

    def valid_move(self, a, vertex):
        if ((a == 0)
            and (not vertex.north_wall)
            and (not (
                vertex.is_entrance_vertex and self.exit_direction == 'TOP')
            )) or (
                (a == 1)
                and (not vertex.south_wall)
                and (not (
                    vertex.is_entrance_vertex
                    and self.entrance_direction == 'BOTTOM'))
            ) or (
                (a == 2)
                and (not vertex.east_wall)
                and (not (
                    vertex.is_entrance_vertex
                    and self.entrance_direction == 'RIGHT'))
            ) or (
                (a == 3)
                and (not vertex.west_wall)
                and (not (
                    vertex.is_entrance_vertex
                    and self.entrance_direction == 'LEFT'))):
            return True
        else:
            return False

    def next_state_for_action(self, action, vertex):
        print("Vertex: {} Action: {}".format(
            vertex, action))
        if self.found_exit(action, vertex):
            return (1.0,
                    vertex.name,
                    1000.,
                    True)
        elif self.valid_move(action, vertex):
            return (1.0,
                    self.adjacent_vertex(vertex, action).name,
                    -1,
                    False)
        else:
            return (10.0,
                    vertex.name,
                    -1,
                    False)

    def reward_for_action(self, a, vertex):
        if self.found_exit(a, vertex):
            return 100
        elif self.valid_move(a, vertex):
            return -1
        else:
            return -5

    def set_maze_layout(self):
        c = 0
        for row in range(0, self.maze_height):
            for col in range(0, self.maze_width):
                # v = Vertex(chr(ord('A') + c))
                v = Vertex(0 + c)
                if row == 0:
                    v.is_top_vertex = True
                if row == (self.maze_height - 1):
                    v.is_bottom_vertex = True
                if col == 0:
                    v.is_left_vertex = True
                if col == (self.maze_width - 1):
                    v.is_right_vertex = True
                self.maze_layout[row][col] = v
                c += 1

    def get_row_col_for_vertex(self, vertex):
        for row in range(0, self.maze_height):
            for col in range(0, self.maze_width):
                if self.maze_layout[row][col] == vertex:
                    return (row, col)

    def reset_vertex_visits(self):
        for v in self.graph.keys():
            v.is_visited = False

    def reset_edge_visits(self):
        for e in self.edges_visits.keys():
            self.edges_visits[e] = False

    def set_graph(self):
        self.set_maze_layout()
        for row in range(0, self.maze_height):
            for col in range(0, self.maze_width):
                v1 = self.maze_layout[row][col]
                if col < (self.maze_width - 1):
                    v2 = self.maze_layout[row][col + 1]
                    edge = frozenset([v1, v2])
                    self.edges.update({edge: MazeGraph.VWALL})
                    self.edges_visits.update({edge: False})
                    if v1 not in self.graph:
                        self.graph.update({v1: [v2]})
                    else:
                        self.graph[v1].append(v2)
                    if v2 not in self.graph:
                        self.graph.update({v2: [v1]})
                    else:
                        self.graph[v2].append(v1)
                if row > 0:
                    v2 = self.maze_layout[row - 1][col]
                    edge = frozenset([v1, v2])
                    self.edges.update({edge: MazeGraph.HWALL})
                    self.edges_visits.update({edge: False})
                    if v1 not in self.graph:
                        self.graph.update({v1: [v2]})
                    else:
                        self.graph[v1].append(v2)
                    if v2 not in self.graph:
                        self.graph.update({v2: [v1]})
                    else:
                        self.graph[v2].append(v1)

    def get_vertex_by_name(self, vertex_name):
        vertex = [v
                  for v in self.graph.keys()
                  if v.name == vertex_name
                  ][0]
        return vertex

    def has_unvisited_neighbors(self, vertex):
        if len(self.graph[vertex]) == 0:
            return False
        for neighbor in self.graph[vertex]:
            if not neighbor.is_visited:
                return True
        return False

    def any_unvisited_vertices(self):
        for vertex in self.graph.keys():
            if not vertex.is_visited:
                return True
        return False

    def get_unvisited_neighbors(self, vertex):
        unvisited_neighbors = [
            v
            for v in self.graph[vertex]
            if not v.is_visited
        ]
        return unvisited_neighbors

    def get_neighbors_unexplored_edges(self, vertex):
        neighbors = self.graph[vertex]
        neighbors_unexplored_edges = [
            v
            for v in neighbors
            if not self.edges_visits[frozenset([v, vertex])]
        ]
        return neighbors_unexplored_edges

    def any_right_unvisited_vertices(self):
        for i in range(0, self.maze_height):
            if not self.maze_layout[i][self.maze_width - 1].is_visited:
                return True
        return False

    def is_cubby_vertex(self, vertex):
        neighbors_with_wall = 0
        for neighbor in self.graph[vertex]:
            if self.edges[frozenset([vertex, neighbor])] != MazeGraph.EMPTY\
               and not vertex.is_corner_vertex:
                neighbors_with_wall += 1
        if vertex.is_perimeter_vertex and not vertex.is_gateway:
            neighbors_with_wall += 1
        return neighbors_with_wall == 3

    def all_cubby_vertices(self):
        cubby_vertices = []
        for vertex in self.graph.keys():
            if self.is_cubby_vertex(vertex):
                cubby_vertices.append(vertex)
        return cubby_vertices

    def create_maze_path(self, start_vertex_name,
                         entrance_direction='LEFT'):
        self.entrance_direction = entrance_direction
        current_vertex = self.get_vertex_by_name(start_vertex_name)
        self.start_vertex = current_vertex
        current_vertex.is_visited = True
        current_vertex.is_entrance_vertex = True
        while self.any_unvisited_vertices():
            while self.has_unvisited_neighbors(current_vertex):
                unvisited_neighbors = self.get_unvisited_neighbors(
                    current_vertex)
                rc = random.choice(range(0, len(unvisited_neighbors)))
                previous_vertex = current_vertex
                current_vertex = unvisited_neighbors[rc]
                self.stack.push(previous_vertex)
                current_vertex.is_visited = True
                self.edges[frozenset(
                    [previous_vertex, current_vertex])] = MazeGraph.EMPTY
                if not self.any_right_unvisited_vertices():
                    if self.end_vertex is None:
                        self.end_vertex = current_vertex
                        current_vertex.is_exit_vertex = True
                        rc = random.choice(range(0, 2))
                        if current_vertex.is_right_vertex:
                            if current_vertex.is_top_vertex:
                                self.exit_direction = ['RIGHT', 'TOP'][rc]
                            elif current_vertex.is_bottom_vertex:
                                self.exit_direction = ['RIGHT', 'BOTTOM'][rc]
                            else:
                                self.exit_direction = 'RIGHT'
                        if current_vertex.is_left_vertex:
                            if current_vertex.is_top_vertex:
                                self.exit_direction = ['LEFT', 'TOP'][rc]
                            elif current_vertex.is_bottom_vertex:
                                self.exit_direction = ['LEFT', 'BOTTOM'][rc]
                            else:
                                self.exit_direction = 'LEFT'
                        if not self.exit_direction:
                            if current_vertex.is_bottom_vertex:
                                self.exit_direction = 'BOTTOM'
                            elif current_vertex.is_top_vertex:
                                self.exit_direction = 'TOP'
                if not self.any_unvisited_vertices():
                    if self.end_vertex is None:
                        self.end_vertex = current_vertex
                        current_vertex.is_exit_vertex = True
            if not self.stack.is_empty():
                current_vertex = self.stack.pop()
        self.set_vertex_cell_walls()

    def set_vertex_cell_walls(self):
        for row in range(0, self.maze_height):
            for col in range(0, self.maze_width):
                (structure_left_of_vertex,
                 structure_right_of_vertex, structure_above_vertex,
                 structure_below_vertex) = self.get_cell_walls(row, col)
                vertex = self.maze_layout[row][col]
                vertex.row = row
                vertex.col = col
                vertex.west_wall = MazeGraph.EMPTY != structure_left_of_vertex
                vertex.east_wall = MazeGraph.EMPTY != structure_right_of_vertex
                vertex.north_wall = MazeGraph.EMPTY != structure_above_vertex
                vertex.south_wall = MazeGraph.EMPTY != structure_below_vertex

    def traverse_graph(self, start_vertex_name):
        current_vertex = self.get_vertex_by_name(start_vertex_name)
        self.reset_edge_visits()
        self.traverse(current_vertex)
        self.npaths += 1

    def traverse(self, vertex):
        if vertex.is_exit_vertex:
            print("Found exit vertex {}".format(vertex))
            self.path.append(vertex)
            return vertex
        else:
            neighbors_unexplored_edges = self.get_neighbors_unexplored_edges(
                vertex)
            if len(neighbors_unexplored_edges) == 0:
                all_neighbors = self.graph[vertex]
                neighbor_no_wall = False
                while not neighbor_no_wall:
                    rc = random.choice(range(0, len(all_neighbors)))
                    next_vertex = all_neighbors[rc]
                    edge = frozenset([vertex, next_vertex])
                    if self.edges[edge] == MazeGraph.EMPTY:
                        neighbor_no_wall = True
                    else:
                        all_neighbors.remove(next_vertex)
                        print("Hit dead end at {}, then hill wall at {}"
                              .format(vertex, next_vertex))
                print("Hit dead end at {}, traveling back to {}".format(
                    vertex, next_vertex))
                self.path.append(next_vertex)
                self.traverse(next_vertex)
            else:
                rc = random.choice(range(0, len(neighbors_unexplored_edges)))
                next_vertex = neighbors_unexplored_edges[rc]
                edge = frozenset([vertex, next_vertex])
                self.edges_visits[edge] = True
                if self.edges[edge] == MazeGraph.EMPTY:
                    print("Traveling from {} to {}".format(
                        vertex, next_vertex))
                    self.path.append(next_vertex)
                    self.traverse(next_vertex)
                else:
                    print("Hit wall from {} to {}".format(
                        vertex, next_vertex))
                    self.path.append(vertex)
                    self.traverse(vertex)

    def print_maze_layout(self):
        maze_layout_display = ""
        for row in range(0, self.maze_height):
            for col in range(0, self.maze_width):
                maze_layout_display += "{}".format(self.maze_layout[row][col])
                maze_layout_display += " "
            maze_layout_display += "\n"
        print(maze_layout_display)

    def print_maze_path(self):
        maze_path = ""
        top_layer = ""
        bottom_layer = ""
        for row in range(0, self.maze_height):
            maze_path_below = ""
            maze_path_above = ""
            for col in range(0, self.maze_width):
                data = " "
                if self.maze_layout[row][col].has_tomato:
                    data = "T"
                if col < (self.maze_width - 1):
                    edge = frozenset(
                        [self.maze_layout[row][col],
                         self.maze_layout[row][col + 1]]
                    )
                    wall = self.edges[edge]
                    if col == 0 and row != 0:
                        if self.maze_layout[row][col].is_exit_vertex:
                            maze_path_below += "  {} {} ".format(data, wall)
                        else:
                            maze_path_below += "| {} {} ".format(data, wall)
                    elif col == 0 and row == 0:
                        maze_path_below += "  {} {} ".format(data, wall)
                    else:
                        maze_path_below += "{} {} ".format(data, wall)
                    if row == 0:
                        if self.maze_layout[row][col].is_exit_vertex:
                            top_layer += "  --"
                        else:
                            top_layer += "----"
                if col == (self.maze_width - 1):
                    if self.maze_layout[row][col].is_exit_vertex:
                        maze_path_below += "{}".format(data)
                    else:
                        maze_path_below += "{}|".format(data)
                    if row == 0:
                        if self.maze_layout[row][col].is_exit_vertex:
                            top_layer += "    "
                        else:
                            top_layer += "----"
                if row > 0:
                    edge = frozenset(
                        [self.maze_layout[row][col],
                         self.maze_layout[row - 1][col]]
                    )
                    wall = self.edges[edge]
                    if col == 0:
                        if self.maze_layout[row][col].is_exit_vertex:
                            if wall == MazeGraph.HWALL:
                                maze_path_above += "-  -"
                            elif wall == MazeGraph.EMPTY:
                                maze_path_above += "    "
                        else:
                            if wall == MazeGraph.HWALL:
                                maze_path_above += "|---"
                            elif wall == MazeGraph.EMPTY:
                                maze_path_above += "|   "
                    elif col == (self.maze_width - 1):
                        if self.maze_layout[row][col].is_exit_vertex:
                            if wall == MazeGraph.HWALL:
                                maze_path_above += "--  "
                            elif wall == MazeGraph.EMPTY:
                                maze_path_above += "    "
                        else:
                            if wall == MazeGraph.HWALL:
                                maze_path_above += "---|"
                            elif wall == MazeGraph.EMPTY:
                                maze_path_above += "   |"
                    else:
                        if wall == MazeGraph.HWALL:
                            maze_path_above += "----"
                        elif wall == MazeGraph.EMPTY:
                            maze_path_above += "    "
                    if row == (self.maze_height - 1):
                        if self.maze_layout[row][col].is_exit_vertex and (
                              self.maze_layout[row][col].is_left_vertex or
                              self.maze_layout[row][col].is_right_vertex):
                            bottom_layer += "    "
                        elif (self.maze_layout[row][col].is_left_vertex or
                                self.maze_layout[row][col].is_right_vertex):
                            bottom_layer += "----"
                        elif self.maze_layout[row][col].is_exit_vertex:
                            bottom_layer += "-  -"
                        else:
                            bottom_layer += "----"
            maze_path_above += "\n"
            maze_path_above += maze_path_below
            maze_path += maze_path_above
            maze_path += "\n"
        maze_path += bottom_layer
        top_layer += maze_path
        print(top_layer)

    def adjacent_vertex(self, vertex, action):
        if action == 0:
            return self.maze_layout[vertex.row - 1][vertex.col]
        elif action == 1:
            return self.maze_layout[vertex.row + 1][vertex.col]
        elif action == 2:
            return self.maze_layout[vertex.row][vertex.col + 1]
        elif action == 3:
            return self.maze_layout[vertex.row][vertex.col - 1]

    def east_structure_from_vertex(self, vertex):
        if vertex.col < (self.maze_width - 1):
            vertex_right = self.maze_layout[vertex.row][vertex.col + 1]
            edge = frozenset([vertex, vertex_right])
            return self.edges[edge]
        elif vertex.col == (self.maze_width - 1):
            if vertex.is_gateway:
                return MazeGraph.EMPTY
            else:
                return MazeGraph.VWALL

    def west_structure_from_vertex(self, vertex):
        if vertex.col < (self.maze_width - 1):
            if vertex.col == 0:
                if not vertex.is_gateway:
                    return MazeGraph.VWALL
                else:
                    return MazeGraph.EMPTY
            else:
                vertex_left = self.maze_layout[vertex.row][vertex.col - 1]
                edge = frozenset([vertex, vertex_left])
                return self.edges[edge]

    def north_structure_from_vertex(self, vertex):
        if vertex.row == 0:
            if vertex.is_gateway and not vertex.is_side_vertex:
                return MazeGraph.EMPTY
            else:
                return MazeGraph.HWALL
        if vertex.row > 0:
            vertex_above = self.maze_layout[vertex.row - 1][vertex.col]
            edge = frozenset([vertex, vertex_above])
            return self.edges[edge]

    def south_structure_from_vertex(self, vertex):
        if vertex.row > 0:
            if vertex.row == (self.maze_height - 1):
                if vertex.is_gateway and not vertex.is_side_vertex:
                    return MazeGraph.EMPTY
                else:
                    return MazeGraph.HWALL
        if vertex.row != (self.maze_height - 1):
            vertex_below = self.maze_layout[vertex.row + 1][vertex.col]
            edge = frozenset([vertex, vertex_below])
            return self.edges[edge]

    def get_cell_walls(self, row, col):
        vertex = self.maze_layout[row][col]
        if col < (self.maze_width - 1):
            vertex_right = self.maze_layout[row][col + 1]
            edge = frozenset([vertex, vertex_right])
            structure_right_of_vertex = self.edges[edge]
            if col == 0:
                if vertex.is_gateway and (self.exit_direction == 'LEFT'
                                          or
                                          self.entrance_direction == 'LEFT'
                                          ):
                    structure_left_of_vertex = MazeGraph.EMPTY
                else:
                    structure_left_of_vertex = MazeGraph.VWALL
            else:
                vertex_left = self.maze_layout[row][col - 1]
                edge = frozenset([vertex, vertex_left])
                structure_left_of_vertex = self.edges[edge]
        if col == (self.maze_width - 1):
            if vertex.is_gateway and (self.exit_direction == 'RIGHT'
                                      or
                                      self.entrance_direction == 'RIGHT'
                                      ):
                structure_right_of_vertex = MazeGraph.EMPTY
            else:
                structure_right_of_vertex = MazeGraph.VWALL
            vertex_left = self.maze_layout[row][col - 1]
            edge = frozenset([vertex, vertex_left])
            structure_left_of_vertex = self.edges[edge]
        if row == 0:
            if vertex.is_gateway and (self.exit_direction == 'TOP'
                                      or
                                      self.entrance_direction == 'TOP'
                                      ):
                structure_above_vertex = MazeGraph.EMPTY
            else:
                structure_above_vertex = MazeGraph.HWALL
        if row > 0:
            vertex_above = self.maze_layout[row - 1][col]
            edge = frozenset([vertex, vertex_above])
            structure_above_vertex = self.edges[edge]
            if row == (self.maze_height - 1):
                if vertex.is_gateway and (self.exit_direction == 'BOTTOM'
                                          or
                                          self.entrance_direction == 'BOTTOM'
                                          ):
                    structure_below_vertex = MazeGraph.EMPTY
                else:
                    structure_below_vertex = MazeGraph.HWALL
        if row != (self.maze_height - 1):
            vertex_below = self.maze_layout[row + 1][col]
            edge = frozenset([vertex, vertex_below])
            structure_below_vertex = self.edges[edge]
        return (structure_left_of_vertex,
                structure_right_of_vertex,
                structure_above_vertex,
                structure_below_vertex)
