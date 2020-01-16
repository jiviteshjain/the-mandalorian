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

        self.game_h = game_height
        self.game_w = game_width
        
        self.pos = pos
        self.size = size # h, w
        self.vel = np.array([0, -conf.GAME_SPEED], dtype='float32')  # v_x, v_y
        self.acc = np.array([0, 0], dtype='float32')  # a_x, a_y

        self.repr = np.array([[' ' for j in range(self.size[1])] for i in range(self.size[0])], dtype='object')

    def show(self):
        return np.round(self.pos).astype(np.int32), self.size, self.repr

    def is_aground(self):
        return int(round(self.pos[0] + self.size[0])) >= self.game_h - conf.GND_HEIGHT

    def is_high(self):
        return int(round(self.pos[0])) <= conf.SKY_DEPTH

    def is_out(self):
        # T, L, B, R
        # Returns true iff all of the object is out in that direction
        return (self.pos[0] + self.size[0] - 1 < 0), (self.pos[1] + self.size[1] - 1 < 0), (self.pos[0] >= self.game_h), (self.pos[1] >= self.game_w)

    def calc_acc(self):
        self.acc = np.array([0, 0], dtype='float32')

    def move(self):
        # print(self.acc)
        self.vel = self.vel + self.acc
        self.pos = self.pos + self.vel

        if self.is_aground():
            if self.vel[0] > 0:
                self.pos[0] = self.game_h - conf.GND_HEIGHT - self.size[0]
                self.vel[0] = 0
                # conf.GRAVITY_X = -conf.GRAVITY_X
            if self.acc[0] > 0:
                self.acc[0] = 0

        elif self.is_high():
            if self.vel[0] < 0:
                self.pos[0] = conf.SKY_DEPTH
                self.vel[0] = 0
                # conf.GRAVITY_X = -conf.GRAVITY_X
            if self.acc[0] < 0:
                self.acc[0] = 0


    
