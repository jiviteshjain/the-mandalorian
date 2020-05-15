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
        self._acc = np.array([conf.GRAVITY_X, conf.GRAVITY_Y])
        self._repr = np.array([
            [' ', Fore.CYAN + Style.BRIGHT + '_', ' '],
            [Fore.CYAN + Style.BRIGHT + '|', Fore.GREEN +
                Style.BRIGHT + 'O', Fore.CYAN + Style.BRIGHT + '`'],
            [Fore.CYAN + Style.BRIGHT + '[', Style.BRIGHT + Back.GREEN + ' ', Fore.CYAN + Style.BRIGHT + ']'],
            [' ', Fore.CYAN + Style.BRIGHT + 'J', Fore.CYAN + Style.BRIGHT + 'L']
        ], dtype='object')
        self._repr_shield = np.array([
            [' ', Fore.CYAN + Style.BRIGHT + '_', ' '],
            [Fore.CYAN + Style.BRIGHT + '|', Fore.GREEN +
                Style.BRIGHT + 'O', Fore.CYAN + Style.BRIGHT + '`'],
            [Fore.CYAN + Style.BRIGHT + '[', Style.BRIGHT +
                Back.BLACK + ' ', Fore.CYAN + Style.BRIGHT + ']'],
            [' ', Fore.CYAN + Style.BRIGHT + 'J', Fore.CYAN + Style.BRIGHT + 'L']
        ], dtype='object')
        self._shield = False

    def is_out(self):
        '''
        overriden to return false as soon as any part of the object goes off screen, because mandalorian can not go off screen
        '''
        # T, L, B, R
        return (self._pos[0] < 0), (self._pos[1] < 0), (self._pos[0] + self._size[0] - 1 >= self._game_h), (self._pos[1] + self._size[1] - 1 >= self._game_w)

    def show(self):
        '''
        overriden to accomodate shield
        '''

        if not self._shield:
            return np.round(self._pos).astype(np.int32), self._size, self._repr
        else:
            return np.round(self._pos).astype(np.int32), self._size, self._repr_shield

    def set_shield(self, what):
        if type(what) != bool:
            raise ValueError
        self._shield = what

    def nudge(self, key):
        if key == 'w':
            self._acc[0] -= conf.KEY_FORCE
        elif key == 'a':
            self._acc[1] -= conf.KEY_FORCE
        elif key == 'd':
            self._acc[1] += conf.KEY_FORCE

    def reset_acc(self):
        '''
        overriden to accomodate gravity and drag force
        '''

        super().reset_acc()

        self._acc[0] += conf.GRAVITY_X
        self._acc[1] += conf.GRAVITY_Y

        # drag force added so that velocity changes due to user inputs do not accumulate
        # drag force tends to align the player's velocities to the game's velocity
        if (self._vel[1] + conf.GAME_SPEED) > 0:
            drag = -conf.DRAG_COEFF * ((self._vel[1] + conf.GAME_SPEED)** 2)
        else:
            drag = conf.DRAG_COEFF * ((self._vel[1] + conf.GAME_SPEED)** 2)
            
        self._acc[1] += drag

    def move(self):
        super().move()

        t, l, b, r = self.is_out() # don't let it go out

        if l:
            if self._vel[1] < 0:
                self._pos[1] = 0
                self._vel[1] = 0
            if self._acc[1] < 0:
                self._acc[1] = 0

        if r:
            if self._vel[1] > 0:
                self._pos[1] = self._game_w - self._size[1]
                self._vel[1] = 0
            if self._acc[1] > 0:
                self._acc[1] = 0
