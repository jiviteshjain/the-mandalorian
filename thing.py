import os
import numpy as np
from colorama import init as cinit
from colorama import Fore, Back, Style
import random
from time import monotonic as clock

import config as conf

class Thing:
    def __init__(self, game_height, game_width, pos=np.array([0, 0], dtype='float32'), size=np.array([1, 1])):

        if type(game_height) != int or type(game_width) != int\
             or type(pos) != np.ndarray or type(size) != np.ndarray:
            raise ValueError('Invalid arguments')

        self._game_h = game_height
        self._game_w = game_width
        
        self._pos = pos
        self._size = size # h, w
        self._vel = np.array([0, -conf.GAME_SPEED], dtype='float32')  # v_x, v_y
        self._acc = np.array([0, 0], dtype='float32')  # a_x, a_y

        self._repr = np.array([[' ' for j in range(self._size[1])] for i in range(self._size[0])], dtype='object')

    def show(self):
        return np.round(self._pos).astype(np.int32), self._size, self._repr

    def is_aground(self):
        return int(round(self._pos[0] + self._size[0])) >= self._game_h - conf.GND_HEIGHT

    def is_high(self):
        return int(round(self._pos[0])) <= conf.SKY_DEPTH

    def is_out(self):
        # T, L, B, R
        # Returns true iff all of the object is out in that direction
        return (self._pos[0] + self._size[0] - 1 < 0), (self._pos[1] + self._size[1] - 1 < 0), (self._pos[0] >= self._game_h), (self._pos[1] >= self._game_w)

    def reset_acc(self):
        self._acc = np.array([0, 0], dtype='float32')

    def add_acc(self, acc):
        # call after reset_acc
        if type(acc) != np.ndarray:
            raise ValueError

        self._acc = self._acc + acc

    def move(self):
        # print(self.acc)
        self._vel = self._vel + self._acc
        self._pos = self._pos + self._vel

        if self.is_aground():
            if self._vel[0] > 0:
                self._pos[0] = self._game_h - conf.GND_HEIGHT - self._size[0]
                self._vel[0] = 0
                # conf.GRAVITY_X = -conf.GRAVITY_X
            if self._acc[0] > 0:
                self._acc[0] = 0

        elif self.is_high():
            if self._vel[0] < 0:
                self._pos[0] = conf.SKY_DEPTH
                self._vel[0] = 0
                # conf.GRAVITY_X = -conf.GRAVITY_X
            if self._acc[0] < 0:
                self._acc[0] = 0


    
