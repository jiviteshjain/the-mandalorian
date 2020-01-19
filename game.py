import os
import numpy as np
from colorama import init as cinit
from colorama import Fore, Back, Style
import random
from time import monotonic as clock, sleep

from screen import Screen
import config as conf
from thing import Thing
from obstacle import FireBeam, MandalorianBullet
from kbhit import KBHit
from mandalorian import Mandalorian
from utils import intersect, make_coin_group

#    |
#  --+-----> Y
#    |
#    |
#    V
#    X

class Game:

    PLAY_KEYS = ('w', 'a', 'd')
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

        self.lives = conf.MAX_LIVES
        self.score = 0
        self.init_time = clock()

        self.fire_beams = []
        self.coins = []
        self.mandalorian_bullets = []
        self.player = Mandalorian(self.height, self.width, conf.MANDALORIAN_START_Y)

        self.shield = False
        self.shield_time = clock()
        

    def build_firebeam(self):
        num = random.randint(0, 2)
        if num != 0:
            part = (self.height - conf.SKY_DEPTH - conf.GND_HEIGHT) / num
            for i in range(num):
                direc = random.randint(0, 3)
                size = random.randint(
                    conf.MIN_BEAM_SIZE, conf.MAX_BEAM_SIZE - num)
                self.fire_beams.append(FireBeam(self.height, self.width, size, direc, random.randint(
                    conf.SKY_DEPTH, self.height - conf.GND_HEIGHT - size), self.width))

    def build_coins(self):
        h = random.randint(conf.MIN_COIN_SIZE, conf.MAX_COIN_SIZE)
        w = random.randint(conf.MIN_COIN_SIZE, conf.MAX_COIN_SIZE)

        x = random.randint(conf.SKY_DEPTH, self.height - conf.GND_HEIGHT - h)

        self.coins.extend(make_coin_group(self.height, self.width, x, self.width, h, w))

    def build_world(self):
        if self.frame_count % conf.MIN_BEAM_DIST_X == 0:
            self.build_firebeam()

        if random.random() < 0.02:
            self.build_coins()

    def handle_beam_collisions(self):
        for fb in self.fire_beams:
            if self.check_collision(self.player, fb):
                self.lives -= 1
                if self.lives == 0:
                    self.game_over()
                else:
                    self._screen.flash(Back.RED + ' ', self.frame_count)
                    self.fire_beams.remove(fb)

    def handle_coin_collisions(self):
        for co in self.coins:
            if self.check_collision(self.player, co, cheap=True, buffer=True):
                self.score += 1
                self.coins.remove(co)

    def handle_mandalorian_bullet_collisions(self):
        for bu in self.mandalorian_bullets:
            for fb in self.fire_beams:
                if self.check_collision(fb, bu, cheap=True, buffer=True):
                    self.fire_beams.remove(fb)
                    self.mandalorian_bullets.remove(bu)

    def handle_collisions(self):
        self.handle_coin_collisions()
        self.handle_mandalorian_bullet_collisions()

        if not self.shield:
            self.handle_beam_collisions()

    def start_shield(self):
        if self.shield:
            return

        if clock() - self.shield_time > conf.SHIELD_SLEEP_TIME:
            self.shield = True
            self.player.set_shield(True)
            self.shield_time = clock()
            self._screen.flash(Back.CYAN + ' ', self.frame_count)

    def end_shield(self):
        if not self.shield:
            return

        if clock() - self.shield_time > conf.SHIELD_UP_TIME:
            self.shield = False
            self.player.set_shield(False)
            self.shield_time = clock()
            self._screen.flash(Back.CYAN + ' ', self.frame_count)

    def remove_old_objs(self):
        for fb in self.fire_beams:
            if fb.is_out()[1]:
                self.fire_beams.remove(fb)
        
        for co in self.coins:
            if co.is_out()[1]:
                self.coins.remove(co)

        for bu in self.mandalorian_bullets:
            if bu.is_out()[3]:
                self.mandalorian_bullets.remove(bu)

    def paint_objs(self):
        for fb in self.fire_beams:
            self._screen.add(fb)

        for co in self.coins:
            self._screen.add(co)

        for bu in self.mandalorian_bullets:
            self._screen.add(bu)

        self._screen.add(self.player)

    def move_objs(self):
        for fb in self.fire_beams:
            fb.move()

        for co in self.coins:
            co.move()

        for bu in self.mandalorian_bullets:
            bu.move()

        self.player.move()

    def calc_acc_objs(self):
        for fb in self.fire_beams:
            fb.calc_acc()

        for co in self.coins:
            co.calc_acc()

        for bu in self.mandalorian_bullets:
            bu.calc_acc()

        self.player.calc_acc()

    def fire(self):
        pos = self.player.show()[0]

        self.mandalorian_bullets.append(MandalorianBullet(self.height, self.width, int(pos[0]) + 1, int(pos[1]) + 2))

    def handle_input(self):
        if self.keyboard.kbhit():
            inp = self.keyboard.getch()

            if inp in self.PLAY_KEYS:
                self.player.nudge(inp)
                
            elif inp == 'e':
                self.fire()

            elif inp == ' ':
                self.start_shield()

            self.keyboard.flush()

    def game_over(self):
        self.keyboard.set_normal_term()
        print(Style.RESET_ALL)
        raise SystemExit
        pass
    
    def check_collision(self, obj_a, obj_b, cheap=False, buffer=False):
        # Buffering only done for second object
        if buffer and not cheap:
            raise ValueError

        a_pos, a_size, a_repr = obj_a.show()
        b_pos, b_size, b_repr = obj_b.show()

        

        a_rec = [a_pos[0], a_pos[0] + a_size[0] - 1, a_pos[1], a_pos[1] + a_size[1] - 1]
        if buffer:
            b_rec = [b_pos[0] - 1, b_pos[0] + b_size[0], b_pos[1] - 1, b_pos[1] + b_size[1]]
        else:
            b_rec = [b_pos[0], b_pos[0] + b_size[0] - 1, b_pos[1], b_pos[1] + b_size[1] - 1]

        bump, common = intersect(a_rec, b_rec)
        
        if cheap or buffer:
            return bump
        
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
        while True:
            start_time = clock()
            print(random.randint(0, 4))
            self.build_world()
            self.calc_acc_objs()
            self.handle_input()
            self.move_objs()

            self.remove_old_objs()
            self._screen.clear()
            self.paint_objs()

            self.handle_collisions()

            self.end_shield()
            
            self._screen.print_board(self.frame_count)
            self.frame_count += 1
            while clock() - start_time < 0.1:
                pass
            

