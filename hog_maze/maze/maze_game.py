import math
import random
import pygame
import numpy as np
import hog_maze.settings as settings
from hog_maze.settings import r31
from hog_maze.util.util import (
    Point, index_from_prob_dist, draw_from_dist_1)
from hog_maze.maze.maze import MazeGraph
import hog_maze.actor_obj as actor_obj


class MazeGame(object):
    NORTH = 0
    SOUTH = 1
    EAST = 2
    WEST = 3

    def __init__(self, maze_width=4, maze_height=3,
                 area_width=640, area_height=480,
                 wall_scale=6, reward_dict=None):
        self.maze_width = maze_width
        self.maze_height = maze_height
        self.maze_graph = MazeGraph(self.maze_width, self.maze_height)
        self.area_width = area_width
        self.area_height = area_height
        self.cell_width = self.area_width / self.maze_width
        self.cell_height = self.area_height / self.maze_height
        self.wall_scale = wall_scale
        if reward_dict is None:
            self.reward_dict = {'exit_reward': 10000,
                                'valid_move_reward': -1,
                                'invalid_move_reward': -1
                                }
        else:
            self.reward_dict = reward_dict
        self.reset()

    def reset(self):
        self.game_over = False
        self.image = pygame.Surface(
            [self.area_width, self.area_height]
        ).convert()
        self.rect = self.image.get_rect()
        self.image.fill(settings.WHITE)
        self.maze_walls = []
        self.maze_graph.reset()

    def set_maze(self, start_vertex_name):
        self.maze_graph.set_graph()
        self.maze_graph.create_maze_path(start_vertex_name)
        self.set_maze_walls()

    def set_rewards_table(self, actions):
        return self.maze_graph.set_rewards_table(
            actions, self.reward_dict)

    def horizontal_wall(self, x, y):
        horizontal_wall = actor_obj.ActorObject(
            **{'x': x, 'y': y,
               'width': 32,
               'height': 96,
               'sprite_sheet_key': 1,
               'name_object': 'maze_wall'
               })
        topleft = horizontal_wall.rect.topleft
        horizontal_wall.image = pygame.transform.rotate(
            horizontal_wall.image, 90)
        horizontal_wall.image = pygame.transform.scale(
            horizontal_wall.image, (
                int(self.cell_width),
                int(math.ceil(self.cell_height / self.wall_scale))
            ))
        horizontal_wall.rect = horizontal_wall.image.get_rect()
        horizontal_wall.rect.topleft = topleft
        return horizontal_wall

    def vertical_wall(self, x, y):
        vertical_wall = actor_obj.ActorObject(
            **{'x': x, 'y': y,
               'width': 32,
               'height': 96,
               'sprite_sheet_key': 1,
               'name_object': 'maze_wall'
               })
        topleft = vertical_wall.rect.topleft
        vertical_wall.image = pygame.transform.scale(
            vertical_wall.image, (
                int(math.ceil(self.cell_width / self.wall_scale)),
                int(self.cell_height)
            ))
        vertical_wall.rect = vertical_wall.image.get_rect()
        vertical_wall.rect.topleft = topleft
        return vertical_wall

    def topleft_for_vertex(self, vertex):
        left = vertex.col * self.cell_width
        top = vertex.row * self.cell_height
        return (left, top)

    def center_for_vertex(self, vertex):
        centerx = vertex.col * self.cell_width + self.cell_width/2
        centery = vertex.row * self.cell_height + self.cell_height/2
        return (centerx, centery)

    def topleft_sprite_center_in_vertex(self, vertex, sprite):
        centerx, centery = self.center_for_vertex(vertex)
        return (centerx - sprite.width/2,
                centery - sprite.height/2)

    def exit_coords_for_vertex(self, vertex, sprite):
        if self.maze_graph.exit_direction == 'RIGHT':
            x = vertex.col * self.cell_width + self.cell_width
            y = vertex.row * self.cell_height + self.cell_height/2
        elif self.maze_graph.exit_direction == 'TOP':
            x = vertex.col * self.cell_width + self.cell_width/2
            y = vertex.row * self.cell_height
        elif self.maze_graph.exit_direction == 'BOTTOM':
            x = vertex.col * self.cell_width + self.cell_width/2
            y = vertex.row * self.cell_height + self.cell_height
        elif self.maze_graph.exit_direction == 'LEFT':
            x = vertex.col * self.cell_width
            y = vertex.row * self.cell_height + self.cell_height/2
        return Point(x - sprite.width/2, y - sprite.height/2)

    def vertex_from_x_y(self, x, y):
        for row in range(0, self.maze_height):
            for col in range(0, self.maze_width):
                left = col * self.cell_width +\
                        self.rect.topleft[1]
                top = row * self.cell_height + self.rect.topleft[0]
                rect = pygame.Rect((left, top),
                                   (self.cell_width, self.cell_height))
                if rect.collidepoint(x, y):
                    return self.maze_graph.maze_layout[row][col]

    def all_neighbors_for_sprite(self, sprite):
        vertex = self.vertex_from_x_y(sprite.x, sprite.y)
        all_neighbors = self.maze_graph.graph[vertex]
        return all_neighbors

    def all_neighbors_for_vertex(self, vertex):
        all_neighbors = self.maze_graph.graph[vertex]
        return all_neighbors

    def neighbors_unexplored_edges_for_sprite(self, sprite):
        vertex = self.vertex_from_x_y(sprite.x, sprite.y)
        all_neighbors = self.maze_graph.graph[vertex]
        neighbors_unexplored_edges = [
            v
            for v in all_neighbors
            if not sprite.get_state('MAZE').edge_visits[
                frozenset([v, vertex])]
        ]
        return neighbors_unexplored_edges

    def neighbors_unexplored_edges_from_vertex(self, vertex,
                                               edge_visits):
        all_neighbors = self.all_neighbors_for_vertex(vertex)
        neighbors_unexplored_edges = [
            v
            for v in all_neighbors
            if not edge_visits[frozenset([v, vertex])]
        ]
        return neighbors_unexplored_edges

    def set_state(self, state, sprite):
        state_vertex = self.maze_graph.get_vertex_by_name(
            state)
        sprite.get_state(
            'MAZE').current_vertex = state_vertex

    def next_dest_from_pi_a_s(self, pi_a_s, vertex, sprite):
        action_probs = pi_a_s[vertex.name]
        action = index_from_prob_dist(action_probs)
        if vertex.is_exit_vertex:
            dir_dict = {0: 'TOP', 1: 'BOTTOM', 2: 'RIGHT', 3: 'LEFT'}
            if dir_dict[action] == self.maze_graph.exit_direction:
                point = self.exit_coords_for_vertex(vertex, sprite)
                sprite.get_state('MAZE').end = True
                return point
        print("State: {}; Action: {}".format(vertex.name,
                                             action))
        next_vertex = self.maze_graph.adjacent_vertex(vertex, action)
        (x_dest,
         y_dest) = self.topleft_sprite_center_in_vertex(
             next_vertex, sprite)
        return Point(x_dest, y_dest)

    def next_dest_from_value_matrix(self, V, vertex, sprite,
                                    max_alg, epsilon):
        valid_actions = self.valid_actions_for_vertex(vertex)
        if vertex.is_exit_vertex:
            if random.uniform(0, 1) < .5:
                point = self.exit_coords_for_vertex(vertex, sprite)
                sprite.get_state('MAZE').end = True
                return point
        if random.uniform(0, 1) < epsilon:
            print("Exploring space...")
            rc = random.choice(range(0, len(valid_actions)))
            state = self.maze_graph.adjacent_vertex(
                vertex, valid_actions[rc]).name
        else:
            vals = [(self.maze_graph.adjacent_vertex(vertex, a).name,
                     V[self.maze_graph.adjacent_vertex(vertex, a).name][0])
                    for a in valid_actions]
            if max_alg:
                max_value = np.max([v[1] for v in vals])
                state = [v[0] for v in vals
                         if v[1] == max_value][0]
            else:
                state = draw_from_dist_1(vals)
        next_vertex = self.maze_graph.get_vertex_by_name(state)
        (x_dest,
         y_dest) = self.topleft_sprite_center_in_vertex(
             next_vertex, sprite)
        return Point(x_dest, y_dest)

    def path_from_value_matrix(self, V, states, sprite):
        state = 0
        end = False

        print(r31(V.reshape(self.maze_width, self.maze_height)))

        while not end:
            vertex = self.maze_graph.get_vertex_by_name(state)
            valid_actions = self.valid_actions_for_vertex(vertex)
            vals = [(self.maze_graph.adjacent_vertex(vertex, a).name,
                     V[self.maze_graph.adjacent_vertex(vertex, a).name][0])
                    for a in valid_actions]
            max_value = np.max([v[1] for v in vals])
            state = [v[0] for v in vals
                     if v[1] == max_value][0]
            next_vertex = self.maze_graph.get_vertex_by_name(state)
            (x_dest,
             y_dest) = self.topleft_sprite_center_in_vertex(
                 next_vertex, sprite)
            sprite.get_state('MAZE').path.put(Point(x_dest, y_dest))
            if next_vertex.is_exit_vertex:
                point = self.exit_coords_for_vertex(next_vertex, sprite)
                sprite.get_state('MAZE').path.put(point)
                end = True

    def valid_actions_for_vertex(self, vertex):
        actions = []
        if (not vertex.north_wall) and not (
             vertex.is_entrance_vertex and
             self.maze_graph.entrance_direction == 'TOP'
        ) and not (
            vertex.is_exit_vertex and
            self.maze_graph.exit_direction == 'TOP'
        ):
            actions.append(MazeGame.NORTH)
        if (not vertex.south_wall) and not (
             vertex.is_entrance_vertex and
             self.maze_graph.entrance_direction == 'BOTTOM'
        ) and not (
            vertex.is_exit_vertex and
            self.maze_graph.exit_direction == 'BOTTOM'
        ):
            actions.append(MazeGame.SOUTH)
        if (not vertex.east_wall) and not (
             vertex.is_entrance_vertex and
             self.maze_graph.entrance_direction == 'RIGHT'
        ) and not (
            vertex.is_exit_vertex and
            self.maze_graph.exit_direction == 'RIGHT'
        ):
            actions.append(MazeGame.EAST)
        if (not vertex.west_wall) and not (
             vertex.is_entrance_vertex and
             self.maze_graph.entrance_direction == 'LEFT'
        ) and not (
            vertex.is_exit_vertex and
            self.maze_graph.exit_direction == 'LEFT'
        ):
            actions.append(MazeGame.WEST)
        return actions

    def step_for_sprite_action(self, sprite, action):
        vertex = sprite.get_state('MAZE').current_vertex
        edge_visits = sprite.get_state('MAZE').edge_visits
        valid_actions = self.valid_actions_for_vertex(vertex)
        if action in valid_actions:
            if action == MazeGame.NORTH:
                if (vertex.is_exit_vertex) and (
                     self.maze_graph.exit_direction == 'TOP'):
                    sprite.get_state('MAZE').rewards += 100
                    sprite.get_state('MAZE').end = True
                    # print("HOGGY FOUND EXIT!")
                    return
                else:
                    next_vertex = self.maze_graph.maze_layout[
                        vertex.row - 1][vertex.col]
            elif action == MazeGame.SOUTH:
                if (vertex.is_exit_vertex) and (
                     self.maze_graph.exit_direction == 'BOTTOM'):
                    sprite.get_state('MAZE').rewards += 100
                    sprite.get_state('MAZE').end = True
                    # print("HOGGY FOUND EXIT!")
                    return
                else:
                    next_vertex = self.maze_graph.maze_layout[
                        vertex.row + 1][vertex.col]
            elif action == MazeGame.EAST:
                if (vertex.is_exit_vertex) and (
                     self.maze_graph.exit_direction == 'RIGHT'):
                    sprite.get_state('MAZE').rewards += 100
                    sprite.get_state('MAZE').end = True
                    # print("HOGGY FOUND EXIT!")
                    return
                else:
                    next_vertex = self.maze_graph.maze_layout[
                        vertex.row][vertex.col + 1]
            elif action == MazeGame.WEST:
                if (vertex.is_exit_vertex) and (
                     self.maze_graph.exit_direction == 'LEFT'):
                    sprite.get_state('MAZE').rewards += 100
                    sprite.get_state('MAZE').end = True
                    # print("HOGGY FOUND EXIT!")
                    return
                else:
                    next_vertex = self.maze_graph.maze_layout[
                        vertex.row][vertex.col - 1]
            edge = frozenset([vertex, next_vertex])
            if edge_visits[edge]:
                # print("Already traversed edge, higher penalty")
                sprite.get_state('MAZE').rewards -= 5
            else:
                edge_visits[edge] = True
            sprite.set_pos(*self.topleft_sprite_center_in_vertex(
                next_vertex, sprite))
            sprite.get_state('MAZE').rewards -= 1
            sprite.get_state('MAZE').current_vertex = next_vertex
            next_vertex.increment_sprite_visit_count(sprite)
        else:
            # print("hit wall, invalid move")
            sprite.get_state('MAZE').rewards -= 5

    def random_action(self, actions):
        rc = random.choice(range(0, len(actions)))
        return actions[rc]

    def step_for_sprite(self, sprite):
        vertex = sprite.get_state('MAZE').current_vertex
        path = sprite.get_state('MAZE').path
        edge_visits = sprite.get_state('MAZE').edge_visits
        neighbors_unexplored_edges =\
            self.neighbors_unexplored_edges_from_vertex(vertex,
                                                        edge_visits)
        if vertex.is_exit_vertex:
            neighbors_unexplored_edges.append('EXIT')
        if len(neighbors_unexplored_edges) == 0:
            all_neighbors = self.all_neighbors_for_vertex(vertex)
            neighbor_no_wall = False
            while not neighbor_no_wall:
                rc = random.choice(range(0, len(all_neighbors)))
                next_vertex = all_neighbors[rc]
                edge = frozenset([vertex, next_vertex])
                if self.maze_graph.edges[edge] == MazeGraph.EMPTY:
                    neighbor_no_wall = True
                else:
                    all_neighbors.remove(next_vertex)
                    sprite.get_state('MAZE').rewards -= 5
                    # print("Hit dead end at {}, then hill wall at {}"
                    #      .format(vertex, next_vertex))
                    next_vertex.increment_sprite_visit_count(sprite)
            # print("Hit dead end at {}, traveling back to {}".format(
            #    vertex, next_vertex))
            sprite.get_state('MAZE').rewards -= 5
            x, y = self.topleft_sprite_center_in_vertex(
                next_vertex, sprite)
            sprite.set_pos(x, y)
            sprite.get_state('MAZE').current_vertex = next_vertex
            path.put(next_vertex)
            next_vertex.increment_sprite_visit_count(sprite)
        else:
            rc = random.choice(range(0, len(neighbors_unexplored_edges)))
            next_vertex = neighbors_unexplored_edges[rc]
            if next_vertex == 'EXIT':
                sprite.get_state('MAZE').rewards += 100
                sprite.get_state('MAZE').end = True
                # print("HOGGY FOUND EXIT!")
            else:
                edge = frozenset([vertex, next_vertex])
                edge_visits[edge] = True
                if self.maze_graph.edges[edge] == MazeGraph.EMPTY:
                    # print("Traveling from {} to {}".format(
                    #    vertex, next_vertex))
                    x, y = self.topleft_sprite_center_in_vertex(
                        next_vertex, sprite)
                    sprite.set_pos(x, y)
                    sprite.get_state('MAZE').rewards -= 1
                    sprite.get_state('MAZE').current_vertex = next_vertex
                    path.put(next_vertex)
                    next_vertex.increment_sprite_visit_count(sprite)
                else:
                    # print("Hit wall from {} to {}".format(
                    #    vertex, next_vertex))
                    sprite.get_state('MAZE').rewards -= 5
                    path.put(vertex)
                    vertex.increment_sprite_visit_count(sprite)

    def set_maze_walls(self):
        for box_x in range(0, self.maze_height):
            for box_y in range(0, self.maze_width):
                left = (box_y * self.cell_width +
                        self.rect.topleft[1])
                top = (box_x * self.cell_height +
                       self.rect.topleft[0])
                bottom = (top +
                          self.cell_height -
                          math.ceil(self.cell_height / self.wall_scale))
                right = (left +
                         self.cell_width - math.ceil(
                             self.cell_width / self.wall_scale)
                         )
                vertex = self.maze_graph.maze_layout[box_x][box_y]
                if vertex.north_wall:
                    self.maze_walls.append(
                        self.horizontal_wall(left, top))
                if vertex.south_wall:
                    self.maze_walls.append(
                        self.horizontal_wall(left, bottom))
                if vertex.west_wall:
                    self.maze_walls.append(
                        self.vertical_wall(left, top))
                if vertex.east_wall:
                    self.maze_walls.append(
                        self.vertical_wall(right, top))
