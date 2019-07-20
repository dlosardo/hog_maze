class StackArray(object):
    def __init__(self, max_size):
        self.max_size = max_size
        self.array = [None] * self.max_size
        self.size = 0

    def push(self, key):
        if self.size == self.max_size:
            raise IndexError("Stack is full")
        self.array[self.size] = key
        self.size = self.size + 1

    def top(self):
        return self.array[self.size - 1]

    def pop(self):
        top_element = self.array[self.size - 1]
        self.array[self.size - 1] = None
        self.size = self.size - 1
        return top_element

    def is_empty(self):
        return self.size == 0
