import os
import numpy as np
from colorama import init as cinit
from colorama import Fore, Back, Style
import random
from time import monotonic as clock
import math

import config as conf
import utils
from thing import Thing

class FireBeam(Thing):
    '''
    firebeam obstacle object
    uses physics inherited from Thing
    '''

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
            for i in range(self._size[0]):
                for j in range(self._size[1]):
                    self._repr[i][j] = Back.YELLOW + Style.BRIGHT + Fore.RED + '#'
        elif direction == self.DIR_DIA_DOWN:
            for i in range(size):
                self._repr[i][i] = Back.YELLOW + Style.BRIGHT + Fore.RED + '#' 
        else:
            for i in range(size):
                self._repr[i][size - 1 - i] = Back.YELLOW + Style.BRIGHT + Fore.RED + '#'

class Coin(Thing):
    '''
    coin object
    uses physics inherited from Thing
    '''

    def __init__(self, game_height, game_width, x=0, y=0):
        if type(x) != int or type(y) != int:
            raise ValueError

        super().__init__(game_height, game_width, np.array([x, y], dtype='float32'), np.array([1, 1]))

        self._repr = np.array([[Fore.YELLOW + Style.BRIGHT + '$']], dtype='object')

class MandalorianBullet(Thing):
    '''
    mandalorian's bullet
    overrides physics to implement gravity (parabolic paths)
    '''
    
    def __init__(self, game_height, game_width, x=0, y=0):
        if type(x) != int or type(y) != int:
            raise ValueError

        super().__init__(game_height, game_width, np.array([x, y], dtype='float32'), np.array([1, 3]))

        self._repr = np.array([[Back.WHITE + ' ', Back.WHITE + ' ', Style.BRIGHT + Fore.WHITE + 'D']], dtype='object')
        self._vel = np.array([0, conf.MANDALORIAN_BULLET_SPEED], dtype='float32')

    def reset_acc(self):
        '''
        overriden to add gravity
        '''

        super().reset_acc()

        self._acc[0] += conf.GRAVITY_X * 0.1
        self._acc[1] += conf.GRAVITY_Y

class BossBullet(Thing):
    '''
    encapsulates the enemy's bullet
    initially points towards the mandalorian, does not follow continuously, unaffected by gravity
    '''

    def __init__(self, game_height, game_width, x, y, target):
        if type(x) != int or type(y) != int:
            raise ValueError

        super().__init__(game_height, game_width, np.array([x, y], dtype='float32'), np.array([3, 5]))

        self._repr = np.array([
            [' ', Style.BRIGHT + Fore.YELLOW + '.', Style.BRIGHT + Fore.YELLOW + ':', Style.BRIGHT + Fore.YELLOW + '.', ' '],
            [Style.BRIGHT + Fore.YELLOW + '{',
                ' ', Style.BRIGHT + Fore.YELLOW + '@', ' ', Style.BRIGHT + Fore.YELLOW + '}'],
            [' ', Style.BRIGHT + Fore.YELLOW + "'", Style.BRIGHT +
                Fore.YELLOW + ':', Style.BRIGHT + Fore.YELLOW + "'", ' '],
        ], dtype='object')

        # point towards the mandalorian
        target_pos = target.show()[0]
        vel = utils.vector_decompose(conf.BOSS_BULLET_SPEED, self._pos, target_pos)
        self._vel = np.array(vel, dtype='float32')

class Boost(Thing):
    '''
    Boost speeds up the game by adding a backward accelaration to all objects while it is visible
    '''

    def __init__(self, game_height, game_width):
        # places itself
        x = random.randint(conf.SKY_DEPTH, game_height - conf.GND_HEIGHT - 3)
        y = game_width

        super().__init__(game_height, game_width, np.array([x, y], dtype='float32'), np.array([3, 5]))

        self._repr = np.array([
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
    '''
    magnet object affects another object by adding an accelaration towards itself
    '''

    def __init__(self, game_height, game_width):
        # places itself

        x = random.randint(conf.SKY_DEPTH, game_height - conf.GND_HEIGHT - 3)
        y = game_width

        super().__init__(game_height, game_width, np.array([x, y], dtype='float32'), np.array([3, 5]))
        self._repr = np.array([
            [' ', ' ', Fore.RED + '~', ' ', ' '],
            [Fore.RED + '~', ' ', Fore.RED + 'M', ' ', Fore.RED + '~'],
            [' ', ' ', Fore.RED + '~', ' ', ' '],
        ])

    def affect(self, obj):
        pos = obj.show()[0]
        force = utils.vector_decompose(conf.MAGNET_FORCE, pos, self._pos)

        obj.add_acc(np.array(force, dtype='float32'))
