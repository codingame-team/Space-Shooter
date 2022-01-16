import sys
import math
from typing import Tuple, List, Optional
import numpy
import time
from numpy import array

def idebug(*args):
    # return
    print(*args, file=sys.stderr, flush=True)


def debug(*args):
    return
    print(*args, file=sys.stderr, flush=True)

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

        self.target = None  # type: Entity

    def distance(self, unit):
        return numpy.linalg.norm(self.location - unit.location)

    def __repr__(self):
        team = 'me' if self.faction == 1 else 'op'
        return f'{self.unit_id} {team} {self.unit_type} h: {self.health} p: {self.location} v: {self.velocity} gun: {self.gun_cooldown}'

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

    if closest_bullet and closest_bullet.distance(my_ship) < 300:
        _dir = closest_bullet.location - my_ship.location
        norm = numpy.linalg.norm(_dir)
        vector = -my_ship.velocity
        x, y = vector
        action = f'A {x} {y}'
        actions.append(action)
    elif my_ship.distance(enemy_ship) > 800:
        thrust = 6
        direction = enemy_ship.location - my_ship.location
        norm = numpy.linalg.norm(direction)
        vector = direction / norm * thrust
        x, y = vector
        action = f'A {x} {y}'
        actions.append(action)

    # Infinite bullets
    thrust = 100
    direction = enemy_ship.location - my_ship.location
    norm = numpy.linalg.norm(direction)
    vector = direction / norm * thrust
    x, y = vector
    action = f'F {x} {y}'
    actions.append(action)

    # Only 8 missiles
    if missiles_count:
        thrust = 30
        vector = direction / norm * thrust
        x, y = vector
        action = f'M {x} {y}'
        missiles_count -= 1
        actions.append(action)

    print(' | '.join(actions))

    missiles = [u for u in units if u.faction == 1 and u.unit_type == 'M']
    if missiles:
        for m in missiles:
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
