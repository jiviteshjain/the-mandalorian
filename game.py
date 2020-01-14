import os
import numpy as np
from colorama import init as cinit
from colorama import Fore, Back, Style
import random
from time import monotonic as clock

from screen import Screen
import config as conf
from thing import Thing
from obstacle import FireBeam

#    |
#  --+-----> Y
#    |
#    |
#    V
#    X

class Game:

    def __init__(self):
        rows, cols = os.popen('stty size', 'r').read().split()
        self.height = int(rows) - conf.BUFFER_DOWN
        self.width = int(cols) - conf.BUFFER_RIGHT
        
        # if self.height < conf.MIN_HEIGHT or self.width < conf.MIN_WIDTH:
        #     print(Fore.RED + 'Fatal Error: Not enough legroom. Try playing with a larger terminal window.')
        #     raise SystemExit

        self._screen = Screen(self.height, self.width)

    def setup(self):
        # self.obj = Thing(self.height, self.width, x = conf.SKY_DEPTH, y = self.width - conf.BUFFER_RIGHT - 3)
        self.fire_beams = []
        self.fire_beams.append(FireBeam(self.height, self.width, 4, FireBeam.DIR_DIA_DOWN, conf.SKY_DEPTH, self.width - 4))

    def remove_old_objs(self):
        for fb in self.fire_beams:
            if fb.is_out()[1]:
                self.fire_beams.remove(fb)

    def paint_objs(self):
        for fb in self.fire_beams:
            self._screen.add(fb)

    def move_objs(self):
        for fb in self.fire_beams:
            fb.move()

    def play(self):
        self.setup()
        while True:
            start_time = clock()
            print(random.randint(0, 4))

            self.move_objs()
            self.remove_old_objs()
            self.paint_objs()
            self._screen.print_board()
            self._screen.clear()

            while clock() - start_time < 0.1:
                pass

