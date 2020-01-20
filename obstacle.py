import os
import numpy as np
from colorama import init as cinit
from colorama import Fore, Back, Style
import random
from time import monotonic as clock
import math

import config as conf
from thing import Thing

class FireBeam(Thing):

    DIR_HOR = 0 # --
    DIR_VERT = 1 # |
    DIR_DIA_DOWN = 2 # \
    DIR_DIA_UP = 3  # /

    def __init__(self, game_height, game_width, size, direction, x=0, y=0):

        if type(size) != int or direction not in (self.DIR_HOR, self.DIR_VERT, self.DIR_DIA_DOWN, self.DIR_DIA_UP):
            raise ValueError('Invalid arguments')

        if direction == self.DIR_HOR:
            size_arr = np.array([1, size])
        elif direction == self.DIR_VERT:
            size_arr = np.array([size, 1])
        else:
            size_arr = np.array([size, size])

        super().__init__(game_height, game_width, np.array([x, y]), size_arr)

        if direction == self.DIR_HOR or direction == self.DIR_VERT:
            for i in range(self.size[0]):
                for j in range(self.size[1]):
                    self.repr[i][j] = Back.YELLOW + Style.BRIGHT + Fore.RED + '#'
        elif direction == self.DIR_DIA_DOWN:
            for i in range(size):
                self.repr[i][i] = Back.YELLOW + Style.BRIGHT + Fore.RED + '#' 
        else:
            for i in range(size):
                self.repr[i][size - 1 - i] = Back.YELLOW + Style.BRIGHT + Fore.RED + '#'

class Coin(Thing):

    def __init__(self, game_height, game_width, x=0, y=0):
        if type(x) != int or type(y) != int:
            raise ValueError

        super().__init__(game_height, game_width, np.array([x, y], dtype='float32'), np.array([1, 1]))

        self.repr = np.array([[Fore.YELLOW + Style.BRIGHT + '$']], dtype='object')

class MandalorianBullet(Thing):
    
    def __init__(self, game_height, game_width, x=0, y=0):
        if type(x) != int or type(y) != int:
            raise ValueError

        super().__init__(game_height, game_width, np.array([x, y], dtype='float32'), np.array([1, 3]))

        self.repr = np.array([[Back.WHITE + ' ', Back.WHITE + ' ', Style.BRIGHT + Fore.WHITE + 'D']], dtype='object')
        self.vel = np.array([0, conf.MANDALORIAN_BULLET_SPEED], dtype='float32')

    def reset_acc(self):
        super().reset_acc()

        self.acc[0] += conf.GRAVITY_X * 0.1
        self.acc[1] += conf.GRAVITY_Y

class Boost(Thing):
    def __init__(self, game_height, game_width):
        # places itself
        x = random.randint(conf.SKY_DEPTH, game_height - conf.GND_HEIGHT - 3)
        y = game_width

        super().__init__(game_height, game_width, np.array([x, y], dtype='float32'), np.array([3, 5]))

        self.repr = np.array([
            [Style.BRIGHT + ' ', Style.BRIGHT + ' ', Style.BRIGHT + Fore.MAGENTA + '~', Style.BRIGHT + ' ', Style.BRIGHT + ' '],
            [Style.BRIGHT + Fore.MAGENTA + '~', Style.BRIGHT + ' ', Style.BRIGHT + Fore.MAGENTA + 'B', Style.BRIGHT + ' ', Style.BRIGHT + Fore.MAGENTA + '~'],
            [Style.BRIGHT + ' ', Style.BRIGHT + ' ', Style.BRIGHT +
                Fore.MAGENTA + '~', Style.BRIGHT + ' ', Style.BRIGHT + ' ']
        ])

    def affect(self, obj):
        obj.add_acc(np.array([0, -conf.BOOST_SPEED], dtype='float32'))

    def unaffect(self, obj):
        obj.add_acc(np.array([0, conf.BOOST_SPEED], dtype='float32'))

class Magnet(Thing):
    def __init__(self, game_height, game_width):
        # places itself

        x = random.randint(conf.SKY_DEPTH, game_height - conf.GND_HEIGHT - 3)
        y = game_width

        super().__init__(game_height, game_width, np.array([x, y], dtype='float32'), np.array([3, 5]))
        self.repr = np.array([
            [' ', ' ', Fore.RED + '~', ' ', ' '],
            [Fore.RED + '~', ' ', Fore.RED + 'M', ' ', Fore.RED + '~'],
            [' ', ' ', Fore.RED + '~', ' ', ' '],
        ])

    def affect(self, obj):
        pos = obj.show()[0]
        x_cap = abs(self.pos[0] - pos[0])
        y_cap = abs(self.pos[1] - pos[1])

        theta = math.atan2(x_cap, y_cap)
        x_force = abs(conf.MAGNET_FORCE * math.sin(theta))
        y_force = abs(conf.MAGNET_FORCE * math.cos(theta))

        if self.pos[0] < pos[0]:
            x_force = -x_force
            
        if self.pos[1] < pos[1]:
            y_force = -y_force

        obj.add_acc(np.array([x_force, y_force], dtype='float32'))
