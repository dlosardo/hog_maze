import random
import numpy as np


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


def draw_from_dist(vals):
    v_sum = np.sum([v[1] for v in vals])
    perc = [(v[0], v[1] / v_sum) for v in vals]
    rn = random.uniform(0, 1)
    print(rn)
    cum_perc = perc[0][1]
    for i in range(0, len(perc)):
        if rn <= cum_perc:
            return perc[i][0]
        cum_perc += perc[i+1][1]


def draw_from_dist_1(vals):
    v_perc = min_max_perc(vals)
    v_sorted = sorted(v_perc, key=lambda x: x[1])
    print(v_sorted)
    rn = random.uniform(0, 1)
    for i in range(0, len(v_sorted)):
        if rn <= v_sorted[i][1]:
            return v_sorted[i][0]


def min_max_perc(vals):
    min_ = np.min([v[1] for v in vals])
    max_ = np.max([v[1] for v in vals])
    min_max_ = [(v[0], (v[1] - min_ + 1) / (max_ - min_ + 1))
                for v in vals]
    return min_max_


def index_from_prob_dist(probs_list):
    rn = random.uniform(0, 1)
    cum_perc = probs_list[0]
    for i in range(0, len(probs_list)):
        if rn <= cum_perc:
            return i
        cum_perc += probs_list[i+1]
