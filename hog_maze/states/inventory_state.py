from hog_maze.states.state import HogMazeState


class InventoryState(HogMazeState):

    def __init__(self, name_instance, default_start_amt=0):
        super(InventoryState, self).__init__('INVENTORY')
        self.default_start_amt = default_start_amt
        self.name_instance = name_instance
        self.owner = None
        self.n_removed = 0
        self.reset_inventory_state()

    def reset_inventory_state(self):
        self.inventory = {self.name_instance:
                          self.default_start_amt
                          }

    def add_item(self, item):
        if item not in self.inventory.keys():
            self.inventory[item] = 1
        else:
            self.inventory[item] += 1

    def remove_item(self, item):
        if item not in self.inventory.keys():
            return
        elif self.inventory[item] == 0:
            return
        else:
            self.n_removed += 1
            self.inventory[item] -= 1
