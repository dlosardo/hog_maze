class LevelStatsList(object):

    def __init__(self):
        self.level_stats_list = []

    def add_level(self, level_stats):
        self.level_stats_list.append(level_stats)


class LevelStats(object):

    def __init__(self):
        self.n_ai_hogs = 0
        self.ntomatoes = 0
        self.main_player_time_to_finish = 0
        self.main_player_ntomatoes_picked_up = 0
        self.main_player_ntomatoes_eaten = 0
