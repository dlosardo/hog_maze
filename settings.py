from util.util import Point

WINDOW_WIDTH = 32 * 30  # 640
WINDOW_HEIGHT = 32 * 23  # 480
FPS = 30  # frames per second setting
IS_DEBUG = True

HOGGY_ANIMATION_DELAY = 80

hoggy_starting_state = {
    'point': Point(x=0, y=12),
    'speed_x': 6, 'speed_y': 6,
    'image_filename': "assets/hoggy_spritesheet_2.png",
    'frame_width': 32,
    'frame_height': 32,
    'ncols': 4,
    'animation_delay': 80
}

maze_starting_state = {
    'maze_width': 10,
    'maze_height': 10,
    'area_width': WINDOW_WIDTH,
    'area_height': WINDOW_HEIGHT,
    'wall_scale': 8
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
