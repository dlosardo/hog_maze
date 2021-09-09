class HoggyGameState(object):

    def __init__(self):
        self.done = False
        self.next_state = None
        self.state_kwargs = {}
        self.level_settings = {}
        self.initialize_state()

    def empty_current_objects(self, game, object_name_list):
        for object_name in object_name_list:
            game.current_objects[object_name].empty()

    def initialize_state(self):
        raise NotImplementedError

    def set_game_objects(self, game, **kwargs):
        raise NotImplementedError

    def draw_game(self, game):
        raise NotImplementedError

    def draw_debug(self):
        raise NotImplementedError

    def handle_keys(self, game, event):
        raise NotImplementedError

    def handle_collisions(self, game):
        pass

    def handle_event_paused(self):
        pass
