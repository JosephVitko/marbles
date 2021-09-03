import math
import utils
from pygame import draw

from bound import Bound


class Marble:
    def __init__(self, x=640, y=320, x_vel=0, y_vel=0, radius=50, color=(0, 0, 0), elasticity=0.7):
        self.x = x
        self.y = y
        self.x_vel = x_vel
        self.y_vel = y_vel
        self.total_velocity = None  # always use getter
        self.x_accel = 0
        self.y_accel = 0
        self.radius = radius
        self.color = color
        self.elasticity = elasticity
        self.connected_marble = None
        self.connection_bound = None

    # draw the ball on the screen
    def draw(self, screen):
        draw.circle(screen, self.color, (self.x, self.y), self.radius)

    # update ball location and velocity based on acceleration. Reset acceleration and cached values
    def update_location(self):
        self.x_vel += self.x_accel
        self.y_vel += self.y_accel
        self.x_accel = 0
        self.y_accel = 0
        self.x += self.x_vel
        self.y += self.y_vel
        self.reset_cached_values()

    # reset any values that were temporarily stored
    def reset_cached_values(self):
        self.total_velocity = None

    # accelerate the ball (presumably because of a force), which will affect its motion next frame
    def accelerate(self, x_magnitude=0, y_magnitude=0):
        self.x_accel += x_magnitude
        self.y_accel += y_magnitude

    # handle collision with a linear bound
    def collide_bound(self, bound):
        # get the point along the bound closest to the ball
        closest_x, closest_y = bound.get_closest_to_point(self.x, self.y)

        # calculate the distance between the ball and that point
        distance = utils.get_distance(self.x, self.y, closest_x, closest_y)

        # if the distance between the ball and point is less than the ball's radius, a collision has occurred
        if distance <= self.radius:
            dx = self.x - closest_x
            dy = self.y - closest_y

            # if the distance is less than the ball's radius, seperate the ball from the bound
            if distance < self.radius:
                self.x = closest_x + dx * self.radius / distance
                self.y = closest_y + dy * self.radius / distance

            # calculate phi, the collision angle
            if dx == 0:
                # if the balls are at the same x, their collision angle is 90 degrees (in radians)
                phi = math.pi / 2
            else:
                # otherwise, calculate collision angle by taking the arc tangent of the collision slope
                phi = math.atan(dy / dx)

            # special case when colliding with the "underside" of a bound, add 180 degrees to the angle
            if dy > 0 or bound.vertical and dx > 0:
                phi += math.pi
            if not bound.vertical and bound.slope > 0:
                phi += math.pi
            self_angle = math.atan2(self.y_vel, self.x_vel)
            if len(bound.connected) > 0:
                # incorporate center of mass in the future
                if bound.vertical:
                    relative_pos = (closest_y - bound.min) / (bound.max - bound.min)
                else:
                    relative_pos = (closest_x - bound.start_x) / (bound.end_x - bound.start_x)
                midpoint_x_vel = (bound.connected[0].x_vel + bound.connected[1].x_vel) / 2
                midpoint_y_vel = (bound.connected[0].y_vel + bound.connected[1].y_vel) / 2
                if relative_pos > 0.5:
                    if bound.connected[0].x < bound.connected[1].x:
                        tangential_x_vel = (relative_pos - .5) * 2 * (bound.connected[1].x_vel - midpoint_x_vel)
                        tangential_y_vel = (relative_pos - .5) * 2 * (bound.connected[1].y_vel - midpoint_y_vel)
                    else:
                        tangential_x_vel = (relative_pos - .5) * 2 * (bound.connected[0].x_vel - midpoint_x_vel)
                        tangential_y_vel = (relative_pos - .5) * 2 * (bound.connected[0].y_vel - midpoint_y_vel)
                else:
                    if bound.connected[0].x < bound.connected[1].x:
                        tangential_x_vel = (.5 - relative_pos) * 2 * (bound.connected[0].x_vel - midpoint_x_vel)
                        tangential_y_vel = (.5 - relative_pos) * 2 * (bound.connected[0].y_vel - midpoint_y_vel)
                    else:
                        tangential_x_vel = (.5 - relative_pos) * 2 * (bound.connected[1].x_vel - midpoint_x_vel)
                        tangential_y_vel = (.5 - relative_pos) * 2 * (bound.connected[1].y_vel - midpoint_y_vel)
                point_x_vel = tangential_x_vel + midpoint_x_vel
                point_y_vel = tangential_y_vel + midpoint_y_vel
                bound_angle = math.atan2(point_y_vel, point_x_vel)
                new_x_vel = math.sqrt(point_x_vel ** 2 + point_y_vel ** 2) * math.cos(bound_angle - phi) * math.cos(
                    phi) + math.sqrt(self.x_vel ** 2 + self.y_vel ** 2) * math.sin(self_angle - phi) * math.cos(
                    phi + math.pi / 2)
                new_y_vel = math.sqrt(point_x_vel ** 2 + point_y_vel ** 2) * math.cos(bound_angle - phi) * math.sin(
                    phi) + math.sqrt(self.x_vel ** 2 + self.y_vel ** 2) * math.sin(self_angle - phi) * math.sin(
                    phi + math.pi / 2)
                self.x_accel += (new_x_vel - self.x_vel) * bound.elasticity
                self.y_accel += (new_y_vel - self.y_vel) * bound.elasticity
            else:
                # print('bound slope:', bound.slope)
                total_velocity = math.sqrt(self.x_vel ** 2 + self.y_vel ** 2)
                normal_x_vel = - math.cos(phi) * total_velocity
                normal_y_vel = - math.sin(phi) * total_velocity
                normal_angle = math.atan2(normal_y_vel, normal_x_vel)
                new_x_vel = math.sqrt(normal_x_vel ** 2 + normal_y_vel ** 2) * math.cos(normal_angle - phi) * math.cos(
                    phi) + math.sqrt(self.x_vel ** 2 + self.y_vel ** 2) * math.sin(self_angle - phi) * math.cos(
                    phi + math.pi / 2)
                new_y_vel = math.sqrt(normal_x_vel ** 2 + normal_y_vel ** 2) * math.cos(normal_angle - phi) * math.sin(
                    phi) + math.sqrt(self.x_vel ** 2 + self.y_vel ** 2) * math.sin(self_angle - phi) * math.sin(
                    phi + math.pi / 2)
                self.x_accel += (new_x_vel - self.x_vel) * bound.elasticity
                self.y_accel += (new_y_vel - self.y_vel) * bound.elasticity

    # handle collision with another ball
    def collide_ball(self, other):
        # get the distance between balls
        distance = utils.get_distance(self.x, self.y, other.x, other.y)

        # if the distance between the two balls is close to or less than the sum of their radii, a collision occurred
        if math.isclose(self.radius + other.radius, distance) or self.radius + other.radius >= distance > 0:
            dx = self.x - other.x
            dy = self.y - other.y

            # if the distance is smaller than the sum of the ball's radii, move them apart
            if distance < self.radius + other.radius:
                self.x = other.x + dx * (self.radius + other.radius) / distance
                self.y = other.y + dy * (self.radius + other.radius) / distance

            # calculate phi, the collision angle
            if dx == 0:
                # if the balls are at the same x, their collision angle is 90 degrees (in radians)
                phi = math.pi / 2
            else:
                # otherwise, calculate collision angle by taking the arc tangent of the collision slope
                phi = math.atan(dy / dx)

            # calculate the angle the ball was travelling at using the arc tangent of its velocity components
            self_angle = math.atan2(self.y_vel, self.x_vel)
            other_angle = math.atan2(other.y_vel, other.x_vel)

            # calculate the ball's new x and y velocities.
            new_x_vel = other.get_total_velocity() * math.cos(other_angle - phi) * math.cos(
                phi) + self.get_total_velocity() * math.sin(self_angle - phi) * math.cos(phi + math.pi / 2)
            new_y_vel = other.get_total_velocity() * math.cos(other_angle - phi) * math.sin(
                phi) + self.get_total_velocity() * math.sin(self_angle - phi) * math.sin(phi + math.pi / 2)

            # accelerate the ball by its change in velocity * elasticity
            self.x_accel = (new_x_vel - self.x_vel) * self.elasticity
            self.y_vel = (new_y_vel - self.y_vel) * self.elasticity

    # connect two balls with a linear bound
    def connect(self, other):
        self.connected_marble = other
        self.connection_bound = Bound(self.x, self.y, other.x, other.y)
        self.connection_bound.connected.append(self)
        self.connection_bound.connected.append(other)
        return self.connection_bound

    # update the location of a connecting bound
    def update_connection(self):
        if self.connection_bound is not None:
            self.connection_bound.update_location(self.x, self.y, self.connected_marble.x, self.connected_marble.y)
            # print(self.connection_bound.angle / math.pi * 180)

    # calculate and temporarily store the ball's total velocity
    def get_total_velocity(self):
        if self.total_velocity is None:
            self.total_velocity = utils.norm(self.x_vel, self.y_vel)
        return self.total_velocity

    def __str__(self):
        return "Marble(x: " + str(self.x) + ", y: " + str(self.y) + ")"
