import os
import numpy as np
from colorama import init as cinit
from colorama import Fore, Back, Style
import random
from time import monotonic as clock

from screen import Screen
import config as conf
from thing import Thing


class Game:

    def __init__(self):
        rows, cols = os.popen('stty size', 'r').read().split()
        self.height = int(rows) - conf.BUFFER_DOWN
        self.width = int(cols) - conf.BUFFER_RIGHT
        
        if self.height < conf.MIN_HEIGHT or self.width < conf.MIN_WIDTH:
            print(Fore.RED + 'Fatal Error: Not enough legroom. Try playing with a larger terminal window.')
            raise SystemExit

        self._screen = Screen(self.height, self.width)

    def setup(self):
        self.obj = Thing(self.height, self.width, x = conf.SKY_DEPTH)

    def play(self):
        self.setup()
        while True:
            start_time = clock()
            print(random.randint(0, 4))
            self._screen.add(self.obj)
            self._screen.print_board()
            self._screen.clear()
            self.obj.move()
            while clock() - start_time < 0.1:
                pass

