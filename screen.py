import os
import numpy as np
from colorama import init as cinit
from colorama import Fore, Back, Style
import random

import config as conf

class Screen:

    CURSOR_0 = "\033[0;0H"

    def __init__(self, height, width):
        self._height = height
        self._width = width
        
        self._color_board = np.array([[conf.BG_COLOR for j in range(self._width)] for i in range(self._height)])
        for i in range(self._height):
            for j in range(self._width):
                if random.random() < conf.ACCENT_AMT:
                    self._color_board[i][j] = conf.BG_ACCENT_COLOR

        for i in range(self._height - conf.GND_HEIGHT, self._height):
            for j in range(self._width):
                self._color_board[i][j] = conf.GND_COLOR

        for i in range(conf.SKY_DEPTH):
            for j in range(self._width):
                self._color_board[i][j] = conf.SKY_COLOR

        self._char_board = np.array([[' ' for j in range(self._width)] for i in range(self._height)])

    def print_board(self):
        print(self.CURSOR_0)
        for i in range(self._height):
            for j in range(self._width):
                print(self._color_board[i][j] + self._char_board[i][j], end='')
            print('')
