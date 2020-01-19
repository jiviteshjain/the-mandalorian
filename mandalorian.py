import os
import numpy as np
from colorama import init as cinit
from colorama import Fore, Back, Style
import random
from time import monotonic as clock

import config as conf
from thing import Thing

class Mandalorian(Thing):

    def __init__(self, game_height, game_width, y=0):

        super().__init__(game_height, game_width, np.array([game_height - conf.GND_HEIGHT - 4, y]), np.array([4, 3]))
        self.acc = np.array([conf.GRAVITY_X, conf.GRAVITY_Y])
        self.repr = np.array([
            [' ', Fore.CYAN + Style.BRIGHT + '_', ' '],
            [Fore.CYAN + Style.BRIGHT + '|', Fore.GREEN +
                Style.BRIGHT + 'O', Fore.CYAN + Style.BRIGHT + '`'],
            [Fore.CYAN + Style.BRIGHT + '[', Style.BRIGHT + Back.GREEN + ' ', Fore.CYAN + Style.BRIGHT + ']'],
            [' ', Fore.CYAN + Style.BRIGHT + 'J', Fore.CYAN + Style.BRIGHT + 'L']
        ], dtype='object')
        self.repr_shield = np.array([
            [' ', Fore.CYAN + Style.BRIGHT + '_', ' '],
            [Fore.CYAN + Style.BRIGHT + '|', Fore.GREEN +
                Style.BRIGHT + 'O', Fore.CYAN + Style.BRIGHT + '`'],
            [Fore.CYAN + Style.BRIGHT + '[', Style.BRIGHT +
                Back.BLACK + ' ', Fore.CYAN + Style.BRIGHT + ']'],
            [' ', Fore.CYAN + Style.BRIGHT + 'J', Fore.CYAN + Style.BRIGHT + 'L']
        ], dtype='object')
        self.shield = False

    def is_out(self):
        # T, L, B, R
        # Checks if entire mandalorian is on screen
        return (self.pos[0] < 0), (self.pos[1] < 0), (self.pos[0] + self.size[0] - 1 >= self.game_h), (self.pos[1] + self.size[1] - 1 >= self.game_w)

    def show(self):
        if not self.shield:
            return np.round(self.pos).astype(np.int32), self.size, self.repr
        else:
            return np.round(self.pos).astype(np.int32), self.size, self.repr_shield

    def set_shield(self, what):
        if type(what) != bool:
            raise ValueError
        self.shield = what

    def nudge(self, key):
        if key == 'w':
            self.acc[0] -= conf.KEY_FORCE
        elif key == 'a':
            self.acc[1] -= conf.KEY_FORCE
        elif key == 'd':
            self.acc[1] += conf.KEY_FORCE

    def calc_acc(self):
        super().calc_acc()

        self.acc[0] += conf.GRAVITY_X
        self.acc[1] += conf.GRAVITY_Y

        if (self.vel[1] + conf.GAME_SPEED) > 0:
            drag = -conf.DRAG_COEFF * ((self.vel[1] + conf.GAME_SPEED)** 2)
        else:
            drag = conf.DRAG_COEFF * ((self.vel[1] + conf.GAME_SPEED)** 2)
            
        self.acc[1] += drag

    def move(self):
        super().move()

        t, l, b, r = self.is_out()

        if l:
            if self.vel[1] < 0:
                self.pos[1] = 0
                self.vel[1] = 0
            if self.acc[1] < 0:
                self.acc[1] = 0

        if r:
            if self.vel[1] > 0:
                self.pos[1] = self.game_w - self.size[1]
                self.vel[1] = 0
            if self.acc[1] > 0:
                self.acc[1] = 0
