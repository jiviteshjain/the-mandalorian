import os
import numpy as np
from colorama import init as cinit
from colorama import Fore, Back, Style
import random
from time import monotonic as clock

import config as conf

class Thing:
    def __init__(self, game_height, game_width, x=0, y=0):
        self.game_h = game_height
        self.game_w = game_width
        
        self.pos = np.array([x, y])
        self.size = np.array([3, 3]) # h, w
        self.vel = np.array([0, 0])  # v_x, v_y
        self.acc = np.array([conf.GRAVITY_X, conf.GRAVITY_Y]) # a_x, a_y

        self.repr_back = None
        self.repr_front = np.array([['Q' for j in range(self.size[1])] for i in range(self.size[0])])

    def show(self):
        return np.round(self.pos).astype(np.int32), np.round(self.size).astype(np.int32), self.repr_back, self.repr_front

    def is_aground(self):
        return int(round(self.pos[0] + self.size[0])) >= self.game_h - conf.GND_HEIGHT

    def is_high(self):
        return int(round(self.pos[0])) <= conf.SKY_DEPTH

    def move(self):
        
        self.acc[0] = conf.GRAVITY_X # TODO: see where to set this
        self.acc[1] = conf.GRAVITY_Y
        self.vel = self.vel + self.acc
        self.pos = self.pos + self.vel

        if self.is_aground():
            if self.vel[0] > 0:
                self.pos[0] = self.game_h - conf.GND_HEIGHT - self.size[0]
                self.vel[0] = 0
                conf.GRAVITY_X = -conf.GRAVITY_X
            if self.acc[0] > 0:
                self.acc[0] = 0
            return
        
        if self.is_high():
            if self.vel[0] < 0:
                self.pos[0] = conf.SKY_DEPTH
                self.vel[0] = 0
                conf.GRAVITY_X = -conf.GRAVITY_X
            if self.acc[0] < 0:
                self.acc[0] = 0
            return


    
