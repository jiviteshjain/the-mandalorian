import os
import numpy as np
from colorama import init as cinit
from colorama import Fore, Back, Style
import random
from time import monotonic as clock

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

        self.acc = np.array([0, 0])

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



