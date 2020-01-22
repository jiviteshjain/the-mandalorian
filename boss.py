import os
import numpy as np
from colorama import init as cinit
from colorama import Fore, Back, Style
import random
from time import monotonic as clock
import math

import config as conf
from thing import Thing
from obstacle import BossBullet

class Boss(Thing):
    def __init__(self, game_height, game_width):
        
        h = 15
        w = 39
        x = game_height - conf.GND_HEIGHT - h
        y = game_width - w - 4

        super().__init__(game_height, game_width, np.array([x, y], dtype='float32'), np.array([h, w]))

        self._vel = np.array([0, 0], dtype='float32')

        self._strength = conf.BOSS_MAX_STRENGTH

        self._repr = np.array([[' ', Style.BRIGHT + Fore.RED + '<', Style.BRIGHT + Fore.RED + '>', Style.BRIGHT + Fore.RED + '=', Style.BRIGHT + Fore.RED + '=', Style.BRIGHT + Fore.RED + '=', Style.BRIGHT + Fore.RED + '=', Style.BRIGHT + Fore.RED + '=', Style.BRIGHT + Fore.RED + '=', Style.BRIGHT + Fore.RED + '=', Style.BRIGHT + Fore.RED + '(',
        Style.BRIGHT + Fore.RED + ')', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
        ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
        ' ', ' ', ' ', ' ', ' ', ' '],
       [Style.BRIGHT + Fore.RED + '(', Style.BRIGHT + Fore.RED + '/', Style.BRIGHT + Fore.RED + '\\', Style.BRIGHT + Fore.RED + '_', Style.BRIGHT + Fore.RED + '_', Style.BRIGHT + Fore.RED + '_', ' ', ' ', ' ', Style.BRIGHT + Fore.RED + '/',
        Style.BRIGHT + Fore.RED + '|', Style.BRIGHT + Fore.RED + '\\', Style.BRIGHT + Fore.RED + '\\', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
        ' ', ' ', ' ', Style.BRIGHT + Fore.RED + '(', Style.BRIGHT + Fore.RED + ')', Style.BRIGHT + Fore.RED + '=', Style.BRIGHT + Fore.RED + '=', Style.BRIGHT + Fore.RED + '=', Style.BRIGHT + Fore.RED + '=', Style.BRIGHT + Fore.RED + '=', Style.BRIGHT + Fore.RED + '=',
        Style.BRIGHT + Fore.RED + '=', Style.BRIGHT + Fore.RED + '=', Style.BRIGHT + Fore.RED + '=', Style.BRIGHT + Fore.RED + '=', Style.BRIGHT + Fore.RED + '<', Style.BRIGHT + Fore.RED + '>', Style.BRIGHT + Fore.RED + '_', ' '],
       [' ', ' ', ' ', ' ', ' ', ' ', Style.BRIGHT + Fore.RED + '\\', Style.BRIGHT + Fore.RED + '_', Style.BRIGHT + Fore.RED + '/', ' ',
        Style.BRIGHT + Fore.RED + '|', ' ', Style.BRIGHT + Fore.RED + '\\', Style.BRIGHT + Fore.RED + '\\', ' ', ' ', ' ', ' ', ' ', ' ',
        ' ', ' ', Style.BRIGHT + Fore.RED + '/', Style.BRIGHT + Fore.RED + '/', Style.BRIGHT + Fore.RED + '|', Style.BRIGHT + Fore.RED + '\\', ' ', ' ', ' ', Style.BRIGHT + Fore.RED + '_',
        Style.BRIGHT + Fore.RED + '_', Style.BRIGHT + Fore.RED + '_', Style.BRIGHT + Fore.RED + '_', Style.BRIGHT + Fore.RED + '_', Style.BRIGHT + Fore.RED + '_', Style.BRIGHT + Fore.RED + '/', ' ', Style.BRIGHT + Fore.RED + '\\', Style.BRIGHT + Fore.RED + ')'],
       [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', Style.BRIGHT + Fore.RED + '\\', Style.BRIGHT + Fore.RED + '_',
        Style.BRIGHT + Fore.RED + '|', ' ', ' ', Style.BRIGHT + Fore.RED + '\\', Style.BRIGHT + Fore.RED + '\\', ' ', ' ', ' ', ' ', ' ',
        ' ', Style.BRIGHT + Fore.RED + '/', Style.BRIGHT + Fore.RED + '/', ' ', Style.BRIGHT + Fore.RED + '|', ' ', Style.BRIGHT + Fore.RED + '\\', Style.BRIGHT + Fore.RED + '_', Style.BRIGHT + Fore.RED + '/', ' ',
        ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
       [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
        Style.BRIGHT + Fore.RED + '\\', Style.BRIGHT + Fore.RED + '|', Style.BRIGHT + Fore.RED + '\\', Style.BRIGHT + Fore.RED + '/', Style.BRIGHT + Fore.RED + '|', Style.BRIGHT + Fore.RED + '\\', Style.BRIGHT + Fore.RED + '_', ' ', ' ', ' ',
        Style.BRIGHT + Fore.RED + '/', Style.BRIGHT + Fore.RED + '/', ' ', ' ', Style.BRIGHT + Fore.RED + '/', Style.BRIGHT + Fore.RED + '\\', Style.BRIGHT + Fore.RED + '/', ' ', ' ', ' ',
        ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
       [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
        Style.BRIGHT + Fore.RED + '(', Style.BRIGHT + Fore.RED + 'o', Style.BRIGHT + Fore.RED + 'o', Style.BRIGHT + Fore.RED + ')', Style.BRIGHT + Fore.RED + '\\', ' ', Style.BRIGHT + Fore.RED + '\\', Style.BRIGHT + Fore.RED + '_', Style.BRIGHT + Fore.RED + '/', Style.BRIGHT + Fore.RED + '/',
        ' ', ' ', Style.BRIGHT + Fore.RED + '/', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
        ' ', ' ', ' ', ' ', ' ', ' ', ' '],
       [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', Style.BRIGHT + Fore.RED + '/',
        Style.BRIGHT + Fore.RED + '/', Style.BRIGHT + Fore.RED + '_', Style.BRIGHT + Fore.RED + '/', Style.BRIGHT + Fore.RED + '\\', Style.BRIGHT + Fore.RED + '_', Style.BRIGHT + Fore.RED + '\\', Style.BRIGHT + Fore.RED + '/', ' ', Style.BRIGHT + Fore.RED + '/', ' ',
        ' ', Style.BRIGHT + Fore.RED + '|', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
        ' ', ' ', ' ', ' ', ' ', ' ', ' '],
       [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', Style.BRIGHT + Fore.RED + '@', Style.BRIGHT + Fore.RED + '@',
        Style.BRIGHT + Fore.RED + '/', ' ', ' ', Style.BRIGHT + Fore.RED + '|', Style.BRIGHT + Fore.RED + '=', Style.BRIGHT + Fore.RED + '\\', ' ', ' ', Style.BRIGHT + Fore.RED + '\\', ' ',
        ' ', Style.BRIGHT + Fore.RED + '|', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
        ' ', ' ', ' ', ' ', ' ', ' ', ' '],
       [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
        ' ', ' ', ' ', Style.BRIGHT + Fore.RED + '\\', Style.BRIGHT + Fore.RED + '_', Style.BRIGHT + Fore.RED + '=', Style.BRIGHT + Fore.RED + '\\', Style.BRIGHT + Fore.RED + '_', ' ', Style.BRIGHT + Fore.RED + '\\',
        ' ', Style.BRIGHT + Fore.RED + '|', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
        ' ', ' ', ' ', ' ', ' ', ' ', ' '],
       [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
        ' ', ' ', ' ', ' ', ' ', Style.BRIGHT + Fore.RED + '\\', Style.BRIGHT + Fore.RED + '=', Style.BRIGHT + Fore.RED + '=', Style.BRIGHT + Fore.RED + '\\', ' ',
        Style.BRIGHT + Fore.RED + '\\', Style.BRIGHT + Fore.RED + '|', Style.BRIGHT + Fore.RED + '\\', Style.BRIGHT + Fore.RED + '_', ' ', ' ', ' ', ' ', ' ', ' ',
        ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
       [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
        ' ', ' ', Style.BRIGHT + Fore.RED + '_', Style.BRIGHT + Fore.RED + '_', Style.BRIGHT + Fore.RED + '(', Style.BRIGHT + Fore.RED + '\\', Style.BRIGHT + Fore.RED + '=', Style.BRIGHT + Fore.RED + '=', Style.BRIGHT + Fore.RED + '=', Style.BRIGHT + Fore.RED + '\\',
        Style.BRIGHT + Fore.RED + '(', ' ', ' ', Style.BRIGHT + Fore.RED + ')', Style.BRIGHT + Fore.RED + '\\', ' ', ' ', ' ', ' ', ' ',
        ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
       [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
        ' ', Style.BRIGHT + Fore.RED + '(', Style.BRIGHT + Fore.RED + '(', Style.BRIGHT + Fore.RED + '(', Style.BRIGHT + Fore.RED + '~', Style.BRIGHT + Fore.RED + ')', ' ', Style.BRIGHT + Fore.RED + '_', Style.BRIGHT + Fore.RED + '_', Style.BRIGHT + Fore.RED + '(', Style.BRIGHT + Fore.RED + '_',
        Style.BRIGHT + Fore.RED + '/', ' ', ' ', ' ', Style.BRIGHT + Fore.RED + '|', ' ', ' ', ' ', ' ', ' ', ' ',
        ' ', ' ', ' ', ' ', ' ', ' '],
       [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
        ' ', ' ', ' ', ' ', ' ', ' ', Style.BRIGHT + Fore.RED + '(', Style.BRIGHT + Fore.RED + '(', Style.BRIGHT + Fore.RED + '(', Style.BRIGHT + Fore.RED + '~', Style.BRIGHT + Fore.RED + ')',
        ' ', Style.BRIGHT + Fore.RED + '\\', ' ', ' ', Style.BRIGHT + Fore.RED + '/', ' ', ' ', ' ', ' ', ' ',
        ' ', ' ', ' ', ' ', ' ', ' ', ' '],
       [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
        ' ', ' ', ' ', ' ', ' ', ' ', Style.BRIGHT + Fore.RED + '_', Style.BRIGHT + Fore.RED + '_', Style.BRIGHT + Fore.RED + '_', Style.BRIGHT + Fore.RED + '_', Style.BRIGHT + Fore.RED + '_',
        Style.BRIGHT + Fore.RED + '_', Style.BRIGHT + Fore.RED + '/', ' ', Style.BRIGHT + Fore.RED + '/', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
        ' ', ' ', ' ', ' ', ' ', ' '],
       [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
        ' ', ' ', ' ', ' ', ' ', ' ', Style.BRIGHT + Fore.RED + "'", Style.BRIGHT + Fore.RED + '-', Style.BRIGHT + Fore.RED + '-', Style.BRIGHT + Fore.RED + '-', Style.BRIGHT + Fore.RED + '-',
        Style.BRIGHT + Fore.RED + '-', Style.BRIGHT + Fore.RED + '-', Style.BRIGHT + Fore.RED + "'", ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
        ' ', ' ', ' ', ' ', ' ', ' ']], dtype = 'object')
        
    def follow(self, obj):
        pos, size = obj.show()[0:2]

        obj_top = pos[0]
        obj_bottom = pos[0] + size[0]

        self_top = self._pos[0]
        self_bottom = self._pos[0] + self._size[0]

        if obj_top < self_top:
            self._pos[0] = obj_top

        if obj_bottom > self_bottom:
            self._pos[0] = obj_bottom - self._size[0]

    def take_hit(self):
        self._strength -= 1
        return self._strength <= 0

    def shoot(self, obj):
        return BossBullet(self._game_h, self._game_w, int(self._pos[0] + 7), int(self._pos[1] + 8), obj)

    def get_strength(self):
        return self._strength
