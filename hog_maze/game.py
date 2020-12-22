import pygame
import numpy as np
import hog_maze.settings as settings
import hog_maze.actor_obj as actor_obj
from hog_maze.maze.maze_game import MazeGame
from hog_maze.maze.ri_learning import RILearning
from hog_maze.components.pickupable_component import PickupableComponent
from hog_maze.components.animation_component import AnimationComponent


class Game():
    def __init__(self):
        self.current_objects = {}
        self.current_objects.update(
            {'MAIN_PLAYER': actor_obj.ActorObjectGroupSingle(
                'MAIN_PLAYER')})
        self.current_objects.update(
            {'MAZE_WALLS': actor_obj.ActorObjectGroup(
                'MAZE_WALL')})
        self.current_objects.update(
            {'UI_BUTTONS': actor_obj.ActorObjectGroup(
                'UI_BUTTON')})
        self.current_objects.update(
            {'PICKUPS': actor_obj.ActorObjectGroup(
                'PICKUP')})
        self.current_objects.update(
            {'AI_HOGGY': actor_obj.ActorObjectGroupSingle(
                'AI_HOGGY')})
        self.current_objects.update(
            {'HUD': actor_obj.ActorObjectGroup(
                'HUD')})
        self.current_maze = None
        self.reset_maze(**settings.maze_starting_state)
        self.hud = pygame.Surface([settings.WINDOW_WIDTH,
                                   settings.HUD_OFFSETY]
                                  ).convert()
        self.hud_rect = self.hud.get_rect()
        self.set_hud()
        self.is_paused = False
        self.max_alg = False
        self.alpha = settings.learning_state['alpha']
        self.gamma = settings.learning_state['gamma']
        self.epsilon = settings.learning_state['epsilon']

    @property
    def main_player(self):
        return self.current_objects['MAIN_PLAYER'].sprite

    @main_player.setter
    def main_player(self, main_player_sprite):
        self.current_objects['MAIN_PLAYER'].add(
            main_player_sprite)

    @property
    def ai_hoggy(self):
        return self.current_objects['AI_HOGGY'].sprite

    @ai_hoggy.setter
    def ai_hoggy(self, ai_hoggy_sprite):
        self.current_objects['AI_HOGGY'].add(
            ai_hoggy_sprite)

    def toggle_alg(self):
        if self.max_alg:
            self.max_alg = False
        else:
            self.max_alg = True

    def set_ri_object(self):
        self.ri_obj = RILearning(
            self.epsilon, self.alpha, self.gamma,
            self.current_maze.maze_width*self.current_maze.maze_height,
            len(self.actions), self.actions)
        self.ri_obj.set_rewards_table(
            self.current_maze.maze_graph.set_rewards_table,
            settings.maze_starting_state['reward_dict'])
        self.ri_obj.set_state_trans_matrix()
        self.ri_obj.set_rewards_matrix()
        self.ri_obj.initialize_value_function()
        self.ri_obj.value_function()
        self.print_maze_path()

        def format_float(num):
            return np.format_float_positional(round(num, 2))

        r31 = np.vectorize(format_float)
        print(r31(self.ri_obj.V.reshape(self.current_maze.maze_width,
                                        self.current_maze.maze_height)))
        # self.set_path_for_ai_hoggy()
        current_vertex = self.current_maze.vertex_from_x_y(
            *self.ai_hoggy.coords)
        next_dest = self.current_maze.next_dest_from_value_matrix(
            self.ri_obj.V, current_vertex.name, self.ai_hoggy,
            self.max_alg, self.epsilon)
        self.ai_hoggy.get_component('AI').destination = next_dest

    def recalculate_value_function(self):
        self.ri_obj.set_rewards_table(
            self.current_maze.maze_graph.set_rewards_table,
            settings.maze_starting_state['reward_dict'])
        self.ri_obj.set_rewards_matrix()
        self.ri_obj.initialize_value_function()
        self.ri_obj.value_function()

    def set_path_for_ai_hoggy(self):
        self.current_maze.path_from_value_matrix(
            self.ri_obj.V, self.ri_obj.states, self.ai_hoggy)
        next_dest = self.ai_hoggy.get_state('MAZE').path.get()
        self.ai_hoggy.get_component('AI').destination = next_dest

    def set_destination_ai_hoggy(self):
        if self.ai_hoggy.get_component('AI').reached_destination():
            current_vertex = self.current_maze.vertex_from_x_y(
                *self.ai_hoggy.coords)
            next_dest = self.current_maze.next_dest_from_value_matrix(
                self.ri_obj.V, current_vertex.name, self.ai_hoggy,
                self.max_alg, self.epsilon)
            self.ai_hoggy.get_component('AI').destination = next_dest

    def ai_hoggy_reached_exit_vertex(self):
        return self.ai_hoggy.get_state('MAZE').end

    def reset_maze(self, maze_width, maze_height,
                   area_width, area_height,
                   wall_scale, starting_vertex_name=0,
                   reward_dict=None):
        if self.current_maze:
            self.current_maze.reset()
            self.main_player.x = self.main_player.start_x
            self.main_player.y = self.main_player.start_y
        else:
            self.current_maze = MazeGame(maze_width, maze_height,
                                         area_width, area_height,
                                         wall_scale, reward_dict)
        self.current_maze.set_maze(starting_vertex_name)
        self.current_objects['PICKUPS'].empty()
        self.current_objects['MAZE_WALLS'].empty()
        self.current_objects['MAZE_WALLS'].add(
            self.current_maze.maze_walls)
        self.place_tomatoes()
        self.action_space = 4
        self.actions = [MazeGame.NORTH,
                        MazeGame.SOUTH,
                        MazeGame.EAST,
                        MazeGame.WEST]
        if self.current_objects['AI_HOGGY']:
            print("SET AI HOGGY")
            self.ai_hoggy.get_state(
                'MAZE').reset_maze_state(
                    self.current_maze.maze_graph.edges)
            self.ai_hoggy.set_pos(
                self.ai_hoggy.start_x, self.ai_hoggy.start_y)
            self.ai_hoggy.get_state(
                'MAZE').current_vertex = self.current_maze.vertex_from_x_y(
                    self.ai_hoggy.x, self.ai_hoggy.y)
            self.ai_hoggy.get_state('INVENTORY').reset_inventory_state()
            self.set_ri_object()

    def place_tomatoes(self):
        cubby_vertices = self.current_maze.maze_graph.all_cubby_vertices()
        if len(cubby_vertices) > 0:
            for cubby_vertex in cubby_vertices:
                tomato = actor_obj.ActorObject(
                    **{'x': 0, 'y': 0, 'height': 32, 'width': 32,
                       'sprite_sheet_key': 3,
                       'name_object': 'tomato',
                       'animation': AnimationComponent(is_animating=True),
                       'pickupable': PickupableComponent('tomato')
                       })
                x, y = self.current_maze.topleft_sprite_center_in_vertex(
                    cubby_vertex, tomato)
                tomato.set_pos(x, y)
                # print("ADDING TOMATO TO VERTEX {}".format(cubby_vertex))
                cubby_vertex.has_tomato = True
                self.current_objects['PICKUPS'].add(tomato)

    def set_hud(self):
        tomato = actor_obj.ActorObject(
            **{'x': 10, 'y': 10, 'height': 32, 'width': 32,
               'sprite_sheet_key': 3,
               'in_hud': True,
               'name_object': 'hud_tomato'
               })
        self.current_objects['HUD'].add(tomato)

    def print_maze_path(self):
        maze_path = ""
        top_layer = ""
        bottom_layer = ""
        (ai_hoggy_row, ai_hoggy_col) = self.ai_hoggy.get_state('MAZE').coord
        for row in range(0, self.current_maze.maze_height):
            maze_path_below = ""
            maze_path_above = ""
            for col in range(0, self.current_maze.maze_width):
                current_vertex = self.current_maze.maze_graph.maze_layout[
                    row][col]
                data = " "
                if current_vertex.has_tomato:
                    data = "T"
                if current_vertex.sprite_visits[self.ai_hoggy.name_object]:
                    data = "#"
                if ai_hoggy_row == row and ai_hoggy_col == col:
                    data = "H"
                if not current_vertex.is_right_vertex:
                    wall = self.current_maze.maze_graph.\
                            east_structure_from_vertex(current_vertex)
                    if (current_vertex.is_left_vertex) and (
                         not current_vertex.is_top_vertex):
                        if current_vertex.is_exit_vertex:
                            maze_path_below += "  {} {} ".format(data, wall)
                        else:
                            maze_path_below += "| {} {} ".format(data, wall)
                    elif (current_vertex.is_top_vertex and
                          current_vertex.is_left_vertex):
                        maze_path_below += "  {} {} ".format(data, wall)
                    else:
                        maze_path_below += "{} {} ".format(data, wall)
                    if current_vertex.is_top_vertex:
                        if current_vertex.is_exit_vertex:
                            top_layer += "  --"
                        else:
                            top_layer += "----"
                if current_vertex.is_right_vertex:
                    if current_vertex.is_exit_vertex:
                        maze_path_below += "{}".format(data)
                    else:
                        maze_path_below += "{}|".format(data)
                    if row == 0:
                        if current_vertex.is_exit_vertex:
                            top_layer += "    "
                        else:
                            top_layer += "----"
                if not current_vertex.is_top_vertex:
                    wall = self.current_maze.maze_graph.\
                            north_structure_from_vertex(current_vertex)
                    if current_vertex.is_left_vertex:
                        if current_vertex.is_exit_vertex:
                            if wall == self.current_maze.maze_graph.HWALL:
                                maze_path_above += "-  -"
                            elif wall == self.current_maze.maze_graph.EMPTY:
                                maze_path_above += "    "
                        else:
                            if wall == self.current_maze.maze_graph.HWALL:
                                maze_path_above += "|---"
                            elif wall == self.current_maze.maze_graph.EMPTY:
                                maze_path_above += "|   "
                    elif current_vertex.is_right_vertex:
                        if current_vertex.is_exit_vertex:
                            if wall == self.current_maze.maze_graph.HWALL:
                                maze_path_above += "--  "
                            elif wall == self.current_maze.maze_graph.EMPTY:
                                maze_path_above += "    "
                        else:
                            if wall == self.current_maze.maze_graph.HWALL:
                                maze_path_above += "---|"
                            elif wall == self.current_maze.maze_graph.EMPTY:
                                maze_path_above += "   |"
                    else:
                        if wall == self.current_maze.maze_graph.HWALL:
                            maze_path_above += "----"
                        elif wall == self.current_maze.maze_graph.EMPTY:
                            maze_path_above += "    "
                    if current_vertex.is_bottom_vertex:
                        if current_vertex.is_exit_vertex and (
                            current_vertex.is_left_vertex or
                            current_vertex.is_right_vertex
                        ):
                            bottom_layer += "    "
                        elif (current_vertex.is_left_vertex or
                              current_vertex.is_right_vertex):
                            bottom_layer += "----"
                        elif current_vertex.is_exit_vertex:
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
