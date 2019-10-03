from state import HogMazeState


class InventoryState(HogMazeState):

    def __init__(self, name_instance):
        super(InventoryState, self).__init__('INVENTORY')
        self.inventory = {}
        self.name_instance = name_instance
        self.owner = None

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
            self.inventory[item] -= 1
