import settings
from component import HogMazeComponent


class PlayerInputComponent(HogMazeComponent):
    def __init__(self):
        super(PlayerInputComponent, self).__init__('PLAYER_INPUT')
        self.key_dict = {'up': False,
                         'down': False,
                         'left': False,
                         'right': False,
                         'eat': False}

    def set_key_down(self, event):
        self.key_dict[event] = True

    def set_key_up(self, event):
        self.key_dict[event] = False

    def update(self, **kwargs):
        self.owner.component_dict['MOVABLE'].reset_velocity()
        if self.key_dict['up']:
            if self.owner.y <= 0:
                self.owner.y = 0
            else:
                self.owner.component_dict['MOVABLE'].velocity['y']\
                        = -self.owner.component_dict['MOVABLE'].speed
        elif self.key_dict['down']:
            if self.owner.y >= \
               (settings.WINDOW_HEIGHT - self.owner.height):
                self.owner.component_dict['MOVABLE'].velocity['y'] = 0
            else:
                self.owner.component_dict['MOVABLE'].velocity['y']\
                        = self.owner.component_dict['MOVABLE'].speed
        elif self.key_dict['left']:
            if self.owner.x <= 0:
                self.owner.component_dict['MOVABLE'].velocity['x'] = 0
            else:
                self.owner.component_dict['MOVABLE'].velocity['x']\
                        = -self.owner.component_dict['MOVABLE'].speed
        elif self.key_dict['right']:
            if self.owner.x >= (settings.WINDOW_WIDTH -
                                self.owner.width):
                self.owner.component_dict['MOVABLE'].velocity['x'] = 0
            else:
                self.owner.component_dict['MOVABLE'].velocity['x']\
                        = self.owner.component_dict['MOVABLE'].speed
        elif self.key_dict['eat']:
            print("EAT TOMATO")
            if self.owner.get_state('INVENTORY').inventory['tomato'] > 0:
                self.owner.get_state('INVENTORY').inventory['tomato'] -= 1

        if self.owner.component_dict['MOVABLE'].is_moving():
            self.owner.component_dict['ANIMATION'].is_animating = True
        else:
            self.owner.component_dict['ANIMATION'].is_animating = False
