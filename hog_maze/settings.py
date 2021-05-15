import numpy as np
from hog_maze.maze.maze import MazeDirections
from pathlib import Path
path = Path(__file__).parent / "assets"

SPRITE_SIZE = 32
WINDOW_WIDTH = SPRITE_SIZE * 30  # 640
# WINDOW_HEIGHT = 32 * 23  # 480
WINDOW_HEIGHT = SPRITE_SIZE * 22
HUD_OFFSETX = 0
HUD_OFFSETY = SPRITE_SIZE * 2
FPS = 30  # frames per second setting
IS_DEBUG = False

HOGGY_ANIMATION_DELAY = 45
MAZE_SEED = None

SPRITE_SHEET_DICT = {0: {'image_filename':
                         "{}/hoggy_spritesheet_2.png".format(path),
                         'ncols': 4,
                         'animation_delay': HOGGY_ANIMATION_DELAY},
                     1: {'image_filename': "{}/wall.png".format(path),
                         "ncols": 1},
                     2: {'image_filename': "{}/refresh_64.png".format(path),
                         "ncols": 2,
                         'animation_delay': 10},
                     3: {'image_filename': "{}/tomatoes.png".format(path),
                         "ncols": 2,
                         'animation_delay': 400},
                     4: {'image_filename': "{}/next_level_swap.png".format(path),
                         "ncols": 2,
                         "animation_delay": 10}
                     }

HOGGY_STARTING_STATS = {"speed": 13,
                        "sprite_sheet_key": 0}

AI_HOGGY_STARTING_STATS = {'default': {"speed": 8,
                                       "sprite_sheet_key": 0,
                                       'gamma': 0.9,
                                       'reward_dict': {'exit_reward': 10,
                                                       'tomato_reward': 1000,
                                                       'valid_move_reward': -1,
                                                       'invalid_move_reward': -10000
                                                       }
                                       },
                           'fast': {"speed": 9,
                                    "sprite_sheet_key": 0,
                                    'gamma': 0.9,
                                    'reward_dict': {'exit_reward': 10,
                                                    'tomato_reward': 1000,
                                                    'valid_move_reward': -1,
                                                    'invalid_move_reward': -10000
                                                    }
                                    },
                           'slow': {"speed": 3,
                                    "sprite_sheet_key": 0,
                                    'gamma': 0.95,
                                    'reward_dict': {'exit_reward': 100,
                                                    'tomato_reward': 0,
                                                    'valid_move_reward': -1,
                                                    'invalid_move_reward': -10000
                                                    }
                                    },
                           'exit': {"speed": 8,
                                    "sprite_sheet_key": 0,
                                    'gamma': 0.99,
                                    'reward_dict': {'exit_reward': 100,
                                                    'tomato_reward': 0,
                                                    'valid_move_reward': -1,
                                                    'invalid_move_reward': -10000
                                                    }
                                    }
                           }

MAZE_STARTING_STATE = {
    'maze_width': 6,
    'maze_height': 6,
    'wall_scale': 8,
    'area_width': WINDOW_WIDTH,
    'area_height': WINDOW_HEIGHT,
    'entrance_direction': MazeDirections.SOUTH,
    'starting_vertex_name': None,
    'exit_direction': MazeDirections.SOUTH,
    'seed': MAZE_SEED
}

TOMATO_STATE = {
    'height': SPRITE_SIZE,
    'width': SPRITE_SIZE,
    'sprite_sheet_key': 3
}

MAZE_WALL_STATE = {
    "width": SPRITE_SIZE,
    "height": SPRITE_SIZE * 3,
    "sprite_sheet_key": 1}

LEARNING_STATE = {
    'alpha': 0.3,
    'gamma': 0.9,
    'epsilon': 0.0
}

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GRAY = (100, 100, 100)
BLACK = (0, 0, 0)
ORANGE = (225, 165, 0)


class ColorFactory():

    @staticmethod
    def get_color(color):
        if color == 'white':
            return WHITE
        elif color == 'green':
            return GREEN
        if color == 'blue':
            return BLUE
        elif color == 'red':
            return RED
        if color == 'gray':
            return GRAY
        elif color == 'black':
            return BLACK
        elif color == 'orange':
            return ORANGE


def format_float(num):
    return np.format_float_positional(round(num, 2))


r31 = np.vectorize(format_float)

LEVEL_1_SETTINGS = {
    'reset_maze':
        {
            'maze_width': 5,
            'maze_height': 4,
            'wall_scale': 6,
            'area_width': WINDOW_WIDTH,
            'area_height': WINDOW_HEIGHT,
            'entrance_direction': MazeDirections.SOUTH,
            'starting_vertex_name': None,
            'exit_direction': MazeDirections.SOUTH,
            'seed': MAZE_SEED
        },
    'new_hoggy': True,
    'add_tomatoes': True,
    'ai_hogs': {'ai_hoggy': 'default',
                'ai_hoggy_1': 'exit'
                # ,
                # 'ai_hoggy_2': 'slow'
                }
}

LEVEL_2_SETTINGS = {
    'reset_maze':
    {
        'maze_width': 8,
        'maze_height': 8,
        'wall_scale': 4,
        'area_width': WINDOW_WIDTH,
        'area_height': WINDOW_HEIGHT,
        'entrance_direction': MazeDirections.EAST,
        'starting_vertex_name': None,
        'exit_direction': MazeDirections.WEST,
        'seed': MAZE_SEED
     },
    'new_hoggy': False,
    'add_tomatoes': True,
    'ai_hogs': {'ai_hoggy': 'default',
                'ai_hoggy_1': 'fast'
                }
}

LEVEL_3_SETTINGS = {
    'reset_maze':
    {
        'maze_width': 10,
        'maze_height': 12,
        'wall_scale': 10,
        'area_width': WINDOW_WIDTH,
        'area_height': WINDOW_HEIGHT,
        'entrance_direction': MazeDirections.SOUTH,
        'starting_vertex_name': None,
        'exit_direction': MazeDirections.NORTH,
        'seed': MAZE_SEED
     },
    'new_hoggy': False,
    'add_tomatoes': True,
    'ai_hogs': {'ai_hoggy': 'default',
                'ai_hoggy_1': 'fast',
                'ai_hoggy_2': 'slow'
                }
}
LEVEL_SETTINGS = {1: LEVEL_1_SETTINGS,
                  2: LEVEL_2_SETTINGS,
                  3: LEVEL_3_SETTINGS
                  }
