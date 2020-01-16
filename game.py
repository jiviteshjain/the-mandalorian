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
from kbhit import KBHit
from mandalorian import Mandalorian
from utils import intersect

#    |
#  --+-----> Y
#    |
#    |
#    V
#    X

class Game:

    PLAY_KEYS = ('w', 'a', 'd', ' ', 'e')
    CONTROL_KEYS = ('q', )

    def __init__(self):
        rows, cols = os.popen('stty size', 'r').read().split()
        self.height = int(rows) - conf.BUFFER_DOWN
        self.width = int(cols) - conf.BUFFER_RIGHT
        
        if self.height < conf.MIN_HEIGHT or self.width < conf.MIN_WIDTH:
            print(Fore.RED + 'Fatal Error: Not enough legroom. Try playing with a larger terminal window.')
            raise SystemExit

        self._screen = Screen(self.height, self.width)
        self.keyboard = KBHit()
        self.frame_count = 0

    def setup(self):
        # self.obj = Thing(self.height, self.width, x = conf.SKY_DEPTH, y = self.width - conf.BUFFER_RIGHT - 3)
        self.fire_beams = []
        self.player = Mandalorian(self.height, self.width, conf.MANDALORIAN_START_Y)

    def build_world(self):
        if self.frame_count % conf.MIN_BEAM_DIST_X == 0:
            num = random.randint(0, 2)
            if num != 0:
                part = (self.height - conf.SKY_DEPTH - conf.GND_HEIGHT) / num
                for i in range(num):
                    direc = random.randint(0, 3)
                    size = random.randint(conf.MIN_BEAM_SIZE, conf.MAX_BEAM_SIZE - num)
                    self.fire_beams.append(FireBeam(self.height, self.width, size, direc, random.randint(conf.SKY_DEPTH, self.height - conf.GND_HEIGHT - size), self.width))


    def remove_old_objs(self):
        for fb in self.fire_beams:
            if fb.is_out()[1]:
                self.fire_beams.remove(fb)

    def paint_objs(self):
        for fb in self.fire_beams:
            self._screen.add(fb)
        self._screen.add(self.player)

    def move_objs(self):
        for fb in self.fire_beams:
            fb.move()
        self.player.move()

    def calc_acc_objs(self):
        for fb in self.fire_beams:
            fb.calc_acc()
        self.player.calc_acc()

    def handle_input(self):
        if self.keyboard.kbhit():
            inp = self.keyboard.getch()

            if inp in self.PLAY_KEYS:
                self.player.nudge(inp)
                
            elif inp in self.CONTROL_KEYS:
                pass

            self.keyboard.flush()

    def game_over(self):
        self.keyboard.set_normal_term()
        pass
    
    def check_collision(self, obj_a, obj_b):

        a_pos, a_size, a_repr = obj_a.show()
        b_pos, b_size, b_repr = obj_b.show()

        a_rec = [a_pos[0], a_pos[0] + a_size[0] - 1, a_pos[1], a_pos[1] + a_size[1] - 1]
        b_rec = [b_pos[0], b_pos[0] + b_size[0] - 1, b_pos[1], b_pos[1] + b_size[1] - 1]

        bump, common = intersect(a_rec, b_rec)

        if not bump:
            return False

        a_idx = [common[0] - a_pos[0], common[1] - a_pos[0] + 1, common[2] - a_pos[1], common[3] - a_pos[1] + 1]
        b_idx = [common[0] - b_pos[0], common[1] - b_pos[0] + 1, common[2] - b_pos[1], common[3] - b_pos[1] + 1]

        for i in range(common[1] + 1 - common[0]):
            for j in range(common[3] + 1 - common[2]):
                a_i = a_idx[0] + i
                a_j = a_idx[2] + j

                b_i = b_idx[0] + i
                b_j = b_idx[2] + j

                if a_repr[a_i][a_j] != ' ' and b_repr[b_i][b_j] != ' ':
                    return True

        return False

    def play(self):
        self.setup()
        while True:
            start_time = clock()
            print(random.randint(0, 4))
            self.build_world()
            self.calc_acc_objs()
            self.handle_input()
            self.move_objs()

            self.remove_old_objs()
            self.paint_objs()
            
            self._screen.print_board()
            self._screen.clear()
            self.frame_count += 1
            while clock() - start_time < 0.1:
                pass

