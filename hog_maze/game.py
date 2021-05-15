import hog_maze.settings as settings
import hog_maze.actor_obj as actor_obj
from hog_maze.maze.maze_game import MazeGame
from hog_maze.maze.maze import MazeDirections
from hog_maze.components.pickupable_component import PickupableComponent
from hog_maze.components.animation_component import AnimationComponent


class Game():
    def __init__(self):
        self.maze_number = 0
        self.level = 1
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
            {'AI_HOGS': actor_obj.ActorObjectGroup(
                'AI_HOGS')})
        self.current_objects.update(
            {'HUD': actor_obj.ActorObjectGroup(
                'HUD')})
        self.previous_mazes = {}
        self.current_maze = None
        self.is_paused = False
        self.action_space = 4
        self.actions = [MazeDirections.NORTH,
                        MazeDirections.SOUTH,
                        MazeDirections.EAST,
                        MazeDirections.WEST]

    @property
    def main_player(self):
        return self.current_objects['MAIN_PLAYER'].sprite

    @main_player.setter
    def main_player(self, main_player_sprite):
        self.current_objects['MAIN_PLAYER'].add(
            main_player_sprite)

    def get_ai_hoggy(self, ai_hoggy_sprite):
        for ai_hog in self.current_objects['AI_HOGS']:
            if ai_hog.name_instance == ai_hoggy_sprite.name_instance:
                return ai_hog

    def add_ai_hoggy(self, ai_hoggy_sprite):
        self.current_objects['AI_HOGS'].add(
            ai_hoggy_sprite)

    def reset_maze(self, maze_width, maze_height,
                   area_width, area_height,
                   wall_scale, starting_vertex_name=None,
                   entrance_direction=MazeDirections.WEST,
                   exit_direction=MazeDirections.EAST, seed=None
                   ):
        if self.current_maze:
            # try:
                # self.previous_mazes.update(
                    # {'MAZE_{}'.format(self.maze_number):
                    # pickle.dumps(self.current_maze)}
                # )
            # except Exception:
                # import pdb; pdb.set_trace()
            self.maze_number += 1
            self.current_maze.reset()
        else:
            self.current_maze = MazeGame(
                maze_width=maze_width, maze_height=maze_height,
                area_width=area_width, area_height=area_height,
                wall_scale=wall_scale, entrance_direction=entrance_direction,
                exit_direction=exit_direction, seed=seed)
        if starting_vertex_name is None:
            starting_vertex_name = self.current_maze.generate_starting_vertex()
        self.current_maze.set_maze(starting_vertex_name)
        self.current_objects['PICKUPS'].empty()
        self.current_objects['MAZE_WALLS'].empty()
        self.current_objects['MAZE_WALLS'].add(
            self.current_maze.maze_walls)
        self.place_tomatoes()
        if self.main_player:
            starting_vertex = self.current_maze.maze_graph.start_vertex
            (x, y) = self.current_maze.topleft_sprite_center_in_vertex(
                starting_vertex, self.main_player)
            self.main_player.set_pos(x, y)
        if self.current_objects['AI_HOGS']:
            starting_vertex = self.current_maze.maze_graph.start_vertex
            for ai_hoggy in self.current_objects['AI_HOGS']:
                (x, y) = self.current_maze.topleft_sprite_center_in_vertex(
                    starting_vertex, ai_hoggy)
                ai_hoggy.get_state('MAZE').reset_maze_state(
                        self.current_maze.maze_graph.edges)
                ai_hoggy.set_pos(x, y)
                ai_hoggy.get_state(
                    'MAZE').current_vertex = self.current_maze.vertex_from_x_y(
                        x, y)
                ai_hoggy.get_state('INVENTORY').reset_inventory_state()
                ai_hoggy.reward_func = (self.current_maze.maze_graph.
                                        set_rewards_table)
                ai_hoggy.pi_a_s_func = self.current_maze.maze_graph.get_pi_a_s
                ai_hoggy.get_component(
                    'RILEARNING').initialize_value_function()
                ai_hoggy.get_component('RILEARNING').recalc = True
                ai_hoggy.get_component('RILEARNING').update()
                next_dest = self.current_maze.next_dest_from_pi_a_s(
                    ai_hoggy.get_component('RILEARNING').pi_a_s,
                    ai_hoggy)
                ai_hoggy.get_component('AI').destination = next_dest
                # self.print_maze_path()

    def place_tomatoes(self):
        cubby_vertices = self.current_maze.maze_graph.all_cubby_vertices()
        if len(cubby_vertices) > 0:
            for cubby_vertex in cubby_vertices:
                tomato = actor_obj.ActorObject(
                    **{'x': 0, 'y': 0,
                       'height': settings.TOMATO_STATE['height'],
                       'width': settings.TOMATO_STATE['width'],
                       'sprite_sheet_key':
                       settings.TOMATO_STATE['sprite_sheet_key'],
                       'name_object': 'tomato',
                       'animation': AnimationComponent(is_animating=True),
                       'pickupable': PickupableComponent('tomato')
                       })
                x, y = self.current_maze.topleft_sprite_center_in_vertex(
                    cubby_vertex, tomato)
                tomato.set_pos(x, y)
                cubby_vertex.has_tomato = True
                self.current_objects['PICKUPS'].add(tomato)

    def print_maze_path(self):
        maze_path = ""
        top_layer = ""
        bottom_layer = ""
        print(self.current_objects['AI_HOGS'])
        ai_hoggy = self.current_objects['AI_HOGS'].sprite
        vertex = self.current_maze.vertex_from_x_y(*ai_hoggy.coords)
        (ai_hoggy_row, ai_hoggy_col) = vertex.row, vertex.col
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
