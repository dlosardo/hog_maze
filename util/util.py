class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Vector2D(object):
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.get_slope()
        self.get_intercept()

    def get_slope(self):
        if (self.p2.x - self.p1.x) == 0:
            self.slope = 1
        else:
            self.slope = (self.p2.y - self.p1.y) / (self.p2.x - self.p1.x)

    def get_intercept(self):
        self.intercept = self.p1.y - self.slope*self.p1.x

    def __eq__(self, other):
        return self.intercept == other.intercept and self.slope == other.slope


def point_of_intersection(vec1, vec2):
    x_intersect = (vec2.intercept - vec1.intercept) / (
        vec1.slope - vec2.slope)
    y_intersect = vec1.intercept + vec1.slope*x_intersect
    return (x_intersect, y_intersect)
