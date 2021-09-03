import math
import sys
import random
import pygame
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
    K_SPACE,
    MOUSEBUTTONDOWN,
    K_LSHIFT,
    K_1,
    K_2,
    K_3,
)

import utils
from bound import Bound
from marble import Marble

pygame.init()

size = width, height = 1280, 640
background_color = 255, 255, 255
marbles = []
bounds = []
selected_marble = None
selected_point = None

gravity = 0.01

marbles.append(Marble(color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))))
bounds.append(Bound(0, height, width, height))
bounds.append(Bound(0, 0, 0, height))
bounds.append(Bound(0, 0, width, 0))
bounds.append(Bound(width, 0, width, height))

screen = pygame.display.set_mode(size)
running = True
while running:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
            elif event.key == K_LEFT:
                for marble in marbles:
                    marble.accelerate(-1, 0)
            elif event.key == K_RIGHT:
                for marble in marbles:
                    marble.accelerate(1, 0)
            elif event.key == K_UP:
                for marble in marbles:
                    marble.accelerate(0, -1)
            elif event.key == K_DOWN:
                for marble in marbles:
                    marble.accelerate(0, 1)
            elif event.key == K_SPACE:
                if gravity == 0:
                    gravity = 0.01
                else:
                    gravity = 0
        elif event.type == MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            found = False
            for marble in marbles:
                distance = utils.get_distance(marble.x, marble.y, pos[0], pos[1])
                if distance <= marble.radius:
                    if selected_marble is None:
                        selected_marble = marble
                    elif selected_marble == marble:
                        marbles.remove(marble)
                        if marble.connection_bound is not None:
                            bounds.remove(marble.connection_bound)
                        selected_marble = None
                    else:
                        connection = selected_marble.connect(marble)
                        bounds.append(connection)
                        selected_marble = None
                    selected_point = None
                    found = True
                    break
            if not found:
                if keys[K_LSHIFT] and selected_point is None:
                    selected_point = (pos[0], pos[1])
                elif keys[K_LSHIFT] and selected_point is not None:
                    bounds.append(Bound(selected_point[0], selected_point[1], pos[0], pos[1]))
                    selected_point = None
                else:
                    selected_point = None
                    if keys[K_1]:
                        marbles.append(
                            Marble(color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
                                   radius=25,
                                   x=pos[0],
                                   y=pos[1]))
                    elif keys[K_2]:
                        marbles.append(
                            Marble(color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
                                   radius=50,
                                   x=pos[0],
                                   y=pos[1]))
                    elif keys[K_3]:
                        marbles.append(
                            Marble(color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
                                   radius=75,
                                   x=pos[0],
                                   y=pos[1]))
                    else:
                        marbles.append(Marble(color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
                                              radius=random.randint(25, 75),
                                              x=pos[0],
                                              y=pos[1]))

        elif event.type == QUIT:
            running = False
    screen.fill(background_color)
    out_of_bounds = []
    for marble in marbles:
        marble.update_location()
        marble.update_connection()
        if marble.x < 0 or marble.x > width or marble.y < 0 or marble.y > height:
            out_of_bounds.append(marble)
        else:
            marble.accelerate(0, gravity)
            for other in marbles:
                if marble != other:
                    marble.collide_ball(other)
            for bound in bounds:
                if marble not in bound.connected:
                    marble.collide_bound(bound)
            marble.draw(screen)
    for m in out_of_bounds:
        marbles.remove(m)
    for bound in bounds:
        bound.draw(screen)
    pygame.display.flip()
