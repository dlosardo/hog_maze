import numpy as np
from pathlib import Path
path = Path(__file__).parent / "assets"

WINDOW_WIDTH = 32 * 30  # 640
# WINDOW_HEIGHT = 32 * 23  # 480
WINDOW_HEIGHT = 32 * 22
HUD_OFFSETX = 0
HUD_OFFSETY = 32 * 2
FPS = 30  # frames per second setting
IS_DEBUG = True

HOGGY_ANIMATION_DELAY = 45
# MAZE_SEED = 10
MAZE_SEED = 11

sprite_sheet_dict = {0: {'image_filename':
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
                         'animation_delay': 400}
                     }

maze_starting_state = {
    'maze_width': 6,
    'maze_height': 6,
    'area_width': WINDOW_WIDTH,
    'area_height': WINDOW_HEIGHT,
    'wall_scale': 8,
    # 'reward_dict': {'exit_reward': 10000,
    # 'tomato_reward': 10,
    # 'valid_move_reward': -1,
    # 'invalid_move_reward': -10
    # }
    'reward_dict': {'exit_reward': 10,
                    'tomato_reward': 1000,
                    'valid_move_reward': -1,
                    'invalid_move_reward': -10000
                    }
}

learning_state = {
    'alpha': 0.3,
    'gamma': 0.9,
    'epsilon': 0.0
}
max_alg = True

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
