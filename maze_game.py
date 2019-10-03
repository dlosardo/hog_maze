import math
import pygame
import settings
from maze import MazeGraph
import actor_obj


class MazeGame(object):
    def __init__(self, maze_width=4, maze_height=3,
                 area_width=640, area_height=480,
                 wall_scale=6):
        self.maze_width = maze_width
        self.maze_height = maze_height
        self.maze_graph = MazeGraph(self.maze_width, self.maze_height)
        self.area_width = area_width
        self.area_height = area_height
        self.cell_width = self.area_width / self.maze_width
        self.cell_height = self.area_height / self.maze_height
        self.wall_scale = wall_scale
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

    def get_x_y_for_vertex(self, vertex):
        row, col = self.maze_graph.get_row_col_for_vertex(vertex)
        left = col * self.cell_width + self.rect.topleft[1] + self.cell_height/2
        top = row * self.cell_height + self.rect.topleft[0] + self.cell_width/4
        return (left, top)

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
                #  print("Left: {}, Top: {}, Bottom: {}, Right {}".format(
                #    left, top, bottom, right))
                (struc_left, struc_right, struc_above,
                 struc_below) = self.maze_graph.get_cell_walls(
                     box_x, box_y)
                if struc_left == MazeGraph.VWALL:
                    self.maze_walls.append(
                        self.vertical_wall(left, top))
                if struc_above == MazeGraph.HWALL:
                    self.maze_walls.append(
                        self.horizontal_wall(left, top))
                if struc_below == MazeGraph.HWALL:
                    self.maze_walls.append(
                        self.horizontal_wall(left, bottom))
                if struc_right == MazeGraph.VWALL:
                    self.maze_walls.append(
                        self.vertical_wall(right, top))
