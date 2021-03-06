import sys
import math
from typing import Tuple, List, Optional
import numpy
import time
from numpy import array


def idebug(*args):
    return
    print(*args, file=sys.stderr, flush=True)


def debug(*args):
    # return
    print(*args, file=sys.stderr, flush=True)


BORDER = 300
WIDTH, HEIGHT = 1700, 1080


# Move your ship, fire, win!

class Unit:
    def __init__(self, unit_id, faction, unit_type, health, x, y, vx, vy, gun_cooldown=None):
        self.unit_id = unit_id
        self.faction = faction
        self.unit_type = unit_type
        self.health = health
        self.x = x
        self.y = y
        self.location = array([self.x, self.y])
        self.vx = int(vx)
        self.vy = int(vy)
        self.velocity = array([self.vx, self.vy])
        self.gun_cooldown = gun_cooldown

        self.speed = numpy.linalg.norm(self.velocity)
        self.target = None  # type: Entity

    def distance(self, unit):
        return numpy.linalg.norm(self.location - unit.location)

    def change_direction(self):
        x, y = self.location
        if y > BORDER and abs(HEIGHT - y) > BORDER:
            if x < BORDER or abs(WIDTH - x) < BORDER:
                return array([-self.vx, self.vy])
            else:
                return self.velocity
        else:
            if x > BORDER and abs(WIDTH - x) > BORDER:
                return array([self.vx, -self.vy])
            else:
                return array([-self.vx, -self.vy])

    def __repr__(self):
        team = 'me' if self.faction == 1 else 'op'
        return f'{self.unit_id} {team} {self.unit_type} h: {self.health} speed: {self.speed} p: {self.location} v: {self.velocity} gun: {self.gun_cooldown}'


missiles_count = 8

# game loop
while True:
    units_count = int(input())  # number of units on the map
    idebug(units_count)
    units: List[Unit] = []
    for i in range(units_count):
        line = input()
        idebug(line)
        inputs = line.split()
        unit_id = int(inputs[0])  # unit's unique ID
        faction = int(inputs[1])  # 1 if the unit belongs to the player, -1 if to opponent
        unit_type = inputs[2]  # 'S' for ship, 'B' for bullet, 'M' for missile
        health = float(inputs[3])  # remaining unit's health points
        position_x = float(inputs[4])  # X coordinate of the unit's position
        position_y = float(inputs[5])  # Y coordinate of the unit's position
        velocity_x = float(inputs[6])  # X coordinate of the unit's velocity
        velocity_y = float(inputs[7])  # Y coordinate of the unit's velocity
        gun_cooldown = float(inputs[8])  # number of rounds till the next bullet can be fired if this is a ship, -1 otherwise
        units.append(Unit(unit_id, faction, unit_type, health, position_x, position_y, velocity_x, velocity_y, gun_cooldown))

    for unit in units:
        debug(f'unit: {unit}')

    my_ship = [u for u in units if u.faction == 1][0]
    enemy_ship = [u for u in units if u.faction == -1][0]

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)

    my_ship.target = enemy_ship

    # One line for each of the (actively) controlled unit with at least one action specified
    # unitId [| A x y] [| F x y] [| M x y] [| W]
    actions = ['S']

    enemy_bullets = [u for u in units if u.unit_type == 'B' and u.faction == -1]
    closest_bullet = min(enemy_bullets, key=lambda b: b.distance(my_ship)) if enemy_bullets else None

    if closest_bullet:
        debug(f'closest bullet: {closest_bullet.distance(my_ship)}')

    near_border = lambda x, y: x < BORDER or abs(WIDTH - x) < BORDER or y < BORDER or abs(HEIGHT - y) < BORDER

    if near_border(*my_ship.location) and my_ship.speed > 0:
        thrust = 10
        new_direction = my_ship.change_direction()
        norm = numpy.linalg.norm(new_direction)
        vector = new_direction / norm * thrust
        debug(f'DANGER BORDER!! changing speed from {my_ship.velocity} to {vector}')
        x, y = vector
        action = f'A {x} {y}'
        actions.append(action)
    elif closest_bullet and closest_bullet.distance(my_ship) < 700:
        _dir = closest_bullet.location - my_ship.location
        norm = numpy.linalg.norm(_dir)
        # vector = -my_ship.velocity
        vector = enemy_ship.velocity
        x, y = vector
        action = f'A {x} {y}'
        actions.append(action)
    # elif my_ship.distance(enemy_ship) > 1000:
    #     thrust = 6
    #     direction = enemy_ship.location - my_ship.location
    #     norm = numpy.linalg.norm(direction)
    #     vector = direction / norm * thrust
    #     x, y = vector
    #     action = f'A {x} {y}'
    #     actions.append(action)

    # Infinite bullets
    thrust = 100
    direction = enemy_ship.location - my_ship.location
    norm = numpy.linalg.norm(direction)
    vector = direction / norm * thrust
    x, y = vector
    action = f'F {x} {y}'
    actions.append(action)

    # Only 8 missiles
    missiles = [u for u in units if u.unit_type == 'M']
    my_missiles = [u for u in units if u.faction == 1 and u.unit_type == 'M']
    enemy_missiles = [u for u in units if u.faction == -1 and u.unit_type == 'M']
    closest_my_missile = min(my_missiles, key=lambda b: b.distance(my_ship)) if my_missiles else None
    farthest_my_missile = max(my_missiles, key=lambda b: b.distance(my_ship)) if my_missiles else None
    closest_enemy_missile = min(enemy_missiles, key=lambda b: b.distance(my_ship)) if enemy_missiles else None
    closest_missile = min(missiles, key=lambda b: b.distance(my_ship)) if missiles else None

    closest_enemy_bullet = min(enemy_bullets, key=lambda b: b.distance(farthest_my_missile)) if farthest_my_missile and enemy_bullets else None

    # can_launch_missile = closest_my_missile is not None and closest_my_missile.distance(my_ship) > 400
    # can_launch_missile |= closest_enemy_missile is not None and closest_enemy_missile.distance(my_ship) > 600
    # can_launch_missile &= missiles_count and closest_missile is not None

    # can_launch_missile = closest_enemy_bullet is not None and farthest_my_missile.distance(closest_enemy_bullet) > 240
    # can_launch_missile &= closest_enemy_missile is not None and farthest_my_missile.distance(closest_enemy_missile) > 400
    # can_launch_missile &= closest_my_missile is not None and closest_my_missile.distance(my_ship) > 400
    # can_launch_missile |= missiles_count and closest_missile is None

    if closest_enemy_bullet is not None and farthest_my_missile.distance(closest_enemy_bullet) > 240:
        can_launch_missile = True
    else:
        can_launch_missile = False

    debug(f'closest_my_missile: {closest_my_missile}')
    debug(f'closest_enemy_missile: {closest_enemy_missile}')
    debug(f'farthest_my_missile: {farthest_my_missile}')

    if closest_enemy_missile and farthest_my_missile and farthest_my_missile.distance(closest_enemy_missile) > 400:
        can_launch_missile = True
    else:
        can_launch_missile = False

    if closest_my_missile is not None and closest_my_missile.distance(my_ship) > 400:
        can_launch_missile = True
    else:
        can_launch_missile = False

    if not can_launch_missile:
        can_launch_missile = missiles_count and closest_missile is None

    if can_launch_missile:
        thrust = 30
        vector = direction / norm * thrust
        x, y = vector
        action = f'M {x} {y}'
        missiles_count -= 1
        actions.append(action)

    print(' | '.join(actions))

    if my_missiles:
        for m in my_missiles:
            if m.distance(enemy_ship) > 10:
                thrust = 30
                direction = enemy_ship.location - m.location
                norm = numpy.linalg.norm(direction)
                vector = direction / norm * thrust
                x, y = vector
                action = f'{m.unit_id} | A {x} {y}'
            else:
                action = f'{m.unit_id} | D'

            print(action)

