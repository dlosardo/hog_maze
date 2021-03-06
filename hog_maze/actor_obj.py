import pygame
from hog_maze.settings import SPRITE_SHEET_DICT


class ActorObjectGroup(pygame.sprite.Group):
    def __init__(self, name):
        pygame.sprite.Group.__init__(self)
        self.name = name


class ActorObjectGroupSingle(pygame.sprite.GroupSingle):
    def __init__(self, name):
        pygame.sprite.GroupSingle.__init__(self)
        self.name = name


class ActorObject(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height,
                 name_object, sprite_sheet_key,
                 in_hud=False,
                 movable=None,
                 orientation=None,
                 animation=None,
                 clickable=None,
                 player_input=None,
                 pickupable=None,
                 ai=None,
                 rilearning=None,
                 inventory=None,
                 maze=None
                 ):
        pygame.sprite.Sprite.__init__(self)
        self.width = width
        self.height = height
        self.name_object = name_object
        self.sprite_sheet_key = sprite_sheet_key
        self.sprite_sheet = pygame.image.load(
            SPRITE_SHEET_DICT[sprite_sheet_key]['image_filename']
        ).convert_alpha()
        self.ncols = SPRITE_SHEET_DICT[sprite_sheet_key]['ncols']
        self.animation_delay = SPRITE_SHEET_DICT[
            sprite_sheet_key].get('animation_delay')
        rect = (0, 0, self.width, self.height)
        self.image = self.sprite_sheet.subsurface(rect)
        self.rect = self.image.get_rect()
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = y
        self.is_dead = False
        self.in_hud = in_hud
        # states
        self.state_dict = {
            'INVENTORY': None,
            'MAZE': None
        }
        self.state_dict['INVENTORY'] = inventory
        if self.state_dict['INVENTORY']:
            self.state_dict['INVENTORY'].owner = self
        self.state_dict['MAZE'] = maze
        if self.state_dict['MAZE']:
            self.state_dict['MAZE'].owner = self
        # components
        self.component_dict = {
            'MOVABLE': None,
            'ORIENTATION': None,
            'ANIMATION': None,
            'PLAYER_INPUT': None,
            'CLICKABLE': None,
            'PICKUPABLE': None,
            'AI': None,
            'RILEARNING': None}
        self.component_dict['MOVABLE'] = movable
        if self.component_dict['MOVABLE']:
            self.component_dict['MOVABLE'].owner = self
        self.component_dict['ORIENTATION'] = orientation
        if self.component_dict['ORIENTATION']:
            self.component_dict['ORIENTATION'].owner = self
        self.component_dict['ANIMATION'] = animation
        if self.component_dict['ANIMATION']:
            self.component_dict['ANIMATION'].owner = self
            self.component_dict['ANIMATION'].last_frame = self.ncols - 1
        self.component_dict['PLAYER_INPUT'] = player_input
        if self.component_dict['PLAYER_INPUT']:
            self.component_dict['PLAYER_INPUT'].owner = self
        self.component_dict['CLICKABLE'] = clickable
        if self.component_dict['CLICKABLE']:
            self.component_dict['CLICKABLE'].owner = self
        self.component_dict['PICKUPABLE'] = pickupable
        if self.component_dict['PICKUPABLE']:
            self.component_dict['PICKUPABLE'].owner = self
        self.component_dict['AI'] = ai
        if self.component_dict['AI']:
            self.component_dict['AI'].owner = self
        self.component_dict['RILEARNING'] = rilearning
        if self.component_dict['RILEARNING']:
            self.component_dict['RILEARNING'].owner = self

    def __getstate__(self):
        state = self.__dict__.copy()
        image = state.pop("image")
        sprite_sheet = state.pop("sprite_sheet")
        state["image_string"] = (pygame.image.tostring(image, "RGB"),
                                 image.get_size())
        state["sprite_sheet_string"] = (pygame.image.tostring(sprite_sheet,
                                                              "RGB"),
                                        sprite_sheet.get_size())
        return state

    def __setstate__(self, state):
        image_string, size = state.pop("image_string")
        state["image"] = pygame.image.fromstring(image_string, size, "RGB")
        sprite_sheet_string, size = state.pop("sprite_sheet_string")
        state["sprite_sheet"] = pygame.image.fromstring(
            sprite_sheet_string, size, "RGB")
        self.__dict__.update(state)

    def has_component(self, component):
        return self.component_dict[component] is not None

    def get_component(self, component):
        return self.component_dict[component]

    def has_state(self, state):
        return self.state_dict[state] is not None

    def get_state(self, state):
        return self.state_dict[state]

    def set_pos(self, x, y):
        self.x = x
        self.y = y

    @property
    def x(self):
        return self.rect.x

    @x.setter
    def x(self, x):
        self.rect.x = x

    @property
    def y(self):
        return self.rect.y

    @y.setter
    def y(self, y):
        self.rect.y = y

    @property
    def coords(self):
        return (self.x,
                self.y)

    @coords.setter
    def coords(self, x, y):
        self.x = x
        self.y = y
