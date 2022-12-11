from hog_maze.states.state import HogMazeState


class InventoryState(HogMazeState):

    def __init__(self, name_instance, default_start_amt=0):
        super(InventoryState, self).__init__('INVENTORY')
        self.default_start_amt = default_start_amt
        self.name_instance = name_instance
        self.set_inventory_dict()
        self.owner = None

    def set_inventory_dict(self):
        self.inventory_dict = {}

    def add_inventory_type(self, inventory_type, starting_amt):
        if inventory_type not in self.inventory_dict.keys():
            self.inventory_dict.update({inventory_type:
                                        Inventory(inventory_type,
                                                  starting_amt)})

    def add_item(self, item):
        if item in self.inventory_dict.keys():
            self.inventory_dict[item].add_item()

    def remove_item(self, item):
        if item not in self.inventory_dict.keys():
            return
        else:
            self.inventory_dict[item].remove_item()

    def get_total_for_item(self, item):
        if item not in self.inventory_dict.keys():
            return 0
        return self.inventory_dict[item].current_amt

    def get_nremoved_for_item(self, item):
        if item not in self.inventory_dict.keys():
            return 0
        return self.inventory_dict[item].removal_tracking

    def reset_inventory_state(self):
        self.inventory = {self.name_instance:
                          self.default_start_amt
                          }


class Inventory(object):
    def __init__(self, inventory_type, default_starting_amt):
        self.inventory_type = inventory_type
        self.default_starting_amt = default_starting_amt
        self.current_amt = self.default_starting_amt
        self.removal_tracking = 0

    def add_item(self):
        self.current_amt += 1

    def remove_item(self):
        if self.current_amt == 0:
            return
        else:
            self.current_amt -= 1
            self.removal_tracking += 1

    def reset(self):
        self.current_amt = self.default_starting_amt
        self.removal_tracking = 0
