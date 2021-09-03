import math

from pygame import draw

from utils import get_distance


class Bound:
    def __init__(self, start_x, start_y, end_x, end_y, elasticity=.8, friction=.001):
        self.update_location(start_x, start_y, end_x, end_y)
        self.elasticity = elasticity
        self.friction = friction
        self.connected = []

    def update_location(self, start_x, start_y, end_x, end_y):

        if start_x == end_x:
            self.vertical = True
            self.x = start_x
            if end_y > start_y:
                self.min = start_y
                self.max = end_y
            else:
                self.min = end_y
                self.max = start_y
            self.angle = math.pi / 2
            self.length = self.max - self.min
        else:
            self.vertical = False
            if start_x > end_x:
                self.end_x = start_x
                self.end_y = start_y
                self.start_x = end_x
                self.start_y = end_y
            else:
                self.start_x = start_x
                self.end_x = end_x
                self.start_y = start_y
                self.end_y = end_y
            self.slope = (self.end_y - self.start_y) / (self.end_x - self.start_x)
            self.y_intercept = self.start_y - self.slope * self.start_x
            self.angle = math.atan(self.slope)
            self.length = get_distance(self.start_x, self.start_y, self.end_x, self.end_y)

    def draw(self, screen):
        if self.vertical:
            draw.line(screen, (0, 0, 0), (self.x, self.min), (self.x, self.max), width=5)
        else:
            draw.line(screen, (0, 0, 0), (self.start_x, self.start_y), (self.end_x, self.end_y), width=5)

    # returns the closest point along the line to a given point in space
    def get_closest_to_point(self, x, y):
        if self.vertical:
            # special case when bound is vertical, slope is infinite and cannot be used
            closest_x = self.x
            if y > self.max:
                closest_y = self.max
            elif y < self.min:
                closest_y = self.min
            else:
                closest_y = y
        elif self.slope == 0:
            # special case if bound is horizontal, reciprocal slope is infinite and cannot be used.
            closest_y = self.y_intercept
            if x > self.end_x:
                closest_x = self.end_x
            elif x < self.start_x:
                closest_x = self.start_x
            else:
                closest_x = x
        else:
            intersect_slope = - 1 / self.slope
            intersect_intercept = y - x * intersect_slope
            closest_x = (intersect_intercept - self.y_intercept) / (self.slope - intersect_slope)
            if closest_x > self.end_x:
                closest_x = self.end_x
            elif closest_x < self.start_x:
                closest_x = self.start_x
            closest_y = self.slope * closest_x + self.y_intercept
        return closest_x, closest_y
