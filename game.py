import os
import numpy as np
from colorama import init as cinit
from colorama import Fore, Back, Style
import random
from time import monotonic as clock, sleep

from screen import Screen
import config as conf
from thing import Thing
from obstacle import FireBeam, MandalorianBullet, Boost, Magnet
from kbhit import KBHit
from mandalorian import Mandalorian
import utils
from boss import Boss
from dragon import Dragon

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
        self.money = 0

        self.fire_beams = []
        self.coins = []
        self.mandalorian_bullets = []
        self.boosts = []
        self.boost = None
        self.magnets = []
        self.player = Mandalorian(self.height, self.width, conf.MANDALORIAN_START_Y)

        self.shield = False
        self.shield_time = clock()

        self.boss = None
        self.boss_bullets = []

        self.dragon = None
        self.dragon_done = False
        self.dragon_time = None
        
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

        self.coins.extend(utils.make_coin_group(self.height, self.width, x, self.width, h, w))

    def build_boost(self):
        if random.random() < conf.BOOST_PROBAB:
            self.boosts.append(Boost(self.height, self.width))

    def build_magnet(self):
        if random.random() < conf.MAGNET_PROBAB:
            self.magnets.append(Magnet(self.height, self.width))

    def build_boss_bullet(self):
        self.boss_bullets.append(self.boss.shoot(self.player))

    def build_world(self):
        if self.boss is None:
            if self.frame_count % conf.MIN_BEAM_DIST_X == 0:
                self.build_firebeam()

            if random.random() < conf.COIN_PROBAB:
                self.build_coins()

            if self.boost is None and len(self.boosts) == 0:
                self.build_boost()

            if len(self.magnets) == 0:
                self.build_magnet()
        else:
            if random.random() < conf.BOSS_SHOOT_PROBAB:
                self.build_boss_bullet()

    def handle_beam_collisions(self):
        
        if self.dragon is not None:
            return

        for fb in self.fire_beams:
            if self.check_collision(self.player, fb):
                self.lives -= 1
                if self.lives == 0:
                    self.game_over(won=False)
                else:
                    self._screen.flash(Back.RED + ' ', self.frame_count)
                    self.fire_beams.remove(fb)

    def handle_coin_collisions(self):
        if self.dragon is None:
            obj = self.player
        else:
            obj = self.dragon

        for co in self.coins:
            if self.check_collision(obj, co, cheap=True, buffer=True):
                self.money += 1
                self.score += conf.SCORE_COIN_FACTOR
                self.coins.remove(co)

    def handle_mandalorian_bullet_collisions(self):
        for bu in self.mandalorian_bullets:
            for fb in self.fire_beams:
                if self.check_collision(fb, bu, cheap=True, buffer=True):
                    self.score += conf.SCORE_BEAM_FACTOR
                    self.fire_beams.remove(fb)
                    self.mandalorian_bullets.remove(bu)

            if self.boss is not None:
                if self.check_collision(self.boss, bu, cheap=False, buffer=False):
                    self.score += conf.SCORE_BOSS_HIT_FACTOR
                    self.mandalorian_bullets.remove(bu)
                    if self.boss.take_hit():
                        raise self.game_over(won=True)

                for fi in self.boss_bullets:
                    if self.check_collision(fi, bu, cheap=True, buffer=True):
                        self.score += conf.SCORE_BOSS_BULLET_FACTOR
                        self.boss_bullets.remove(fi)
                        self.mandalorian_bullets.remove(bu)

    def handle_boost_collisions(self):

        if self.dragon is not None:
            return

        for bo in self.boosts:
            if self.check_collision(self.player, bo, cheap=True):
                for obj in self.fire_beams:
                    bo.affect(obj)
                for obj in self.coins:
                    bo.affect(obj)
                for obj in self.magnets:
                    bo.affect(obj)
                for obj in self.boosts:
                    bo.affect(obj)
                self.move_objs()
                conf.GAME_SPEED += conf.BOOST_SPEED # for drag and for new objects
                self.boost = [bo, clock()]
                self.boosts.remove(bo)
                self._screen.flash(Back.MAGENTA + ' ', self.frame_count)
                self.score += conf.SCORE_BOOST_FACTOR
    
    def handle_boss_collisions(self):

        if self.check_collision(self.player, self.boss, cheap=False, buffer=False):
            self.game_over(won=False)

    def handle_boss_bullet_collisions(self):
        for bu in self.boss_bullets:
            if self.check_collision(self.player, bu, cheap=True, buffer=True):
                self.boss_bullets.remove(bu)
                self.lives -= 1
                if self.lives <= 0:
                    self.game_over(won=False)
                else:
                    pass

    def handle_collisions(self):
        self.handle_coin_collisions()
        self.handle_mandalorian_bullet_collisions()
        self.handle_boost_collisions()
        if not self.shield:
            self.handle_beam_collisions()
        
        if self.boss is not None:
            self.handle_boss_collisions()
            if not self.shield:
                self.handle_boss_bullet_collisions()

    def end_boost(self, forceful=False):
        if self.boost is None:
            return

        if not forceful and clock() - self.boost[1] > conf.BOOST_UP_TIME:
            bo = self.boost[0]
            for obj in self.fire_beams:
                bo.unaffect(obj)
            for obj in self.coins:
                bo.unaffect(obj)
            for obj in self.magnets:
                bo.unaffect(obj)
            for obj in self.boosts:
                bo.unaffect(obj)
            self.move_objs()
            conf.GAME_SPEED -= conf.BOOST_SPEED # for drag and for new objects
            self.boost = None
            self._screen.flash(Back.MAGENTA + ' ', self.frame_count)

    def pull_magnet(self):

        if self.dragon is not None:
            return

        if len(self.magnets) != 0:
            for ma in self.magnets:
                ma.affect(self.player)

    def start_shield(self):
        if self.dragon is not None:
            return

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

        for ma in self.magnets:
            if ma.is_out()[1]:
                self.magnets.remove(ma)

        for bo in self.boosts:
            if bo.is_out()[1]:
                self.boosts.remove(bo)

        for bu in self.mandalorian_bullets:
            if bu.is_out()[3]:
                self.mandalorian_bullets.remove(bu)

        if self.boss is not None:
            for bu in self.boss_bullets:
                if bu.is_out()[3]:
                    self.boss_bullets.remove(bu)

    def paint_objs(self):
        for fb in self.fire_beams:
            self._screen.add(fb)

        for co in self.coins:
            self._screen.add(co)

        for ma in self.magnets:
            self._screen.add(ma)

        for bo in self.boosts:
            self._screen.add(bo)
        
        if self.boss is not None:
            self._screen.add(self.boss)

            for bu in self.boss_bullets:
                self._screen.add(bu)


        for bu in self.mandalorian_bullets:
            self._screen.add(bu)

        if self.dragon is None:
            self._screen.add(self.player)
        else:
            self._screen.add(self.dragon)

    def move_objs(self):
        for fb in self.fire_beams:
            fb.move()

        for co in self.coins:
            co.move()

        for ma in self.magnets:
            ma.move()

        for bo in self.boosts:
            bo.move()

        for bu in self.mandalorian_bullets:
            bu.move()

        if self.dragon is None:
            self.player.move()
        else:
            self.dragon.move()

        if self.boss is not None:
            self.boss.follow(self.player)
            self.boss.move()
            
            for bu in self.boss_bullets:
                bu.move()

    def reset_acc_objs(self):
        for fb in self.fire_beams:
            fb.reset_acc()

        for bo in self.boosts:
            bo.reset_acc()

        for ma in self.magnets:
            ma.reset_acc()

        for co in self.coins:
            co.reset_acc()

        for bu in self.mandalorian_bullets:
            bu.reset_acc()

        if self.dragon is None:
            self.player.reset_acc()
        else:
            self.dragon.reset_acc()

        if self.boss is not None:
            self.boss.reset_acc()

            for bu in self.boss_bullets:
                bu.reset_acc()

    def fire(self):
        if self.dragon is not None:
            return

        pos = self.player.show()[0]

        self.mandalorian_bullets.append(MandalorianBullet(self.height, self.width, int(pos[0]) + 1, int(pos[1]) + 2))

    def handle_input(self):
        if self.keyboard.kbhit():
            inp = self.keyboard.getch()

            if inp in self.PLAY_KEYS:
                if self.dragon is None:
                    self.player.nudge(inp)
                else:
                    self.dragon.nudge(inp)
                
            elif inp == 'e':
                self.fire()

            elif inp == ' ':
                self.start_shield()

            elif inp == 'g':
                self.setup_dragon()

            elif inp == 'q':
                self.game_over(won=False)

            self.keyboard.flush()

    def game_over(self, won=False):
        sleep(1)
        self._screen.game_over(won, self.score, int(clock() - self.init_time))
        while (True):
            if self.keyboard.kbhit():
                if self.keyboard.getch() == 'f':
                    break
        self.keyboard.set_normal_term()
        raise SystemExit
    
    def setup_boss(self):
        if self.boss is not None:
            return

        if clock() - self.init_time <= conf.BOSS_ARRIVAL_TIME:
            return

        self._screen.flash(Back.YELLOW + ' ', self.frame_count)
        self.boss = Boss(self.height, self.width)

        self.end_boost(forceful=True)
        self.end_dragon(forceful=True)
        self.fire_beams.clear()
        self.coins.clear()
        self.mandalorian_bullets.clear()
        self.boosts.clear()
        self.magnets.clear()

    def setup_dragon(self):
        if self.dragon is not None or self.dragon_done:
            return

        self.dragon_time = clock()
        self.dragon = Dragon(self.height, self.width)
        self.end_boost(forceful=True)
        
    def end_dragon(self, forceful = False):
        if self.dragon is None:
            return
        
        if not forceful and clock() - self.dragon_time <= conf.DRAGON_TIME:
            return

        self.dragon = None
        self.dragon_done = True

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

        bump, common = utils.intersect(a_rec, b_rec)
        
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

    def print_info(self):
        print(Style.RESET_ALL + Style.BRIGHT, end='')
        print('LIVES:', str(self.lives).rjust(1), end='\t')
        print('COINS:', str(self.money).rjust(3), end='\t')
        print('SCORE:', str(self.score).rjust(5), end='\t')
        time = int(clock() - self.init_time)
        print('TIME:', str(time).rjust(5), end='\t')
        
        if self.shield:
            time_left = int(conf.SHIELD_UP_TIME - (clock()- self.shield_time))
            print('SHIELD ACTIVE:', str(time_left).rjust(2), end='')
        else:
            time_left = int(conf.SHIELD_SLEEP_TIME - (clock() - self.shield_time))
            if time_left <= 0:
                print('SHIELD AVAIL', end='')
            else:
                print('SHIELD IN:', str(time_left).rjust(2), end='')
        print('            ', end='')

    def play(self):
        while True:
            self.setup_boss()
            start_time = clock()
            
            self.build_world()
            self.reset_acc_objs()
            self.handle_input()
            self.pull_magnet()
            self.move_objs()
            self.remove_old_objs()
            self.handle_collisions()
            
            self._screen.clear()
            self.paint_objs()

            self.end_shield()
            self.end_boost()
            self.end_dragon()
            
            self._screen.print_board(self.frame_count)
            self.print_info()
            self.frame_count += 1
            self.score += conf.SCORE_TIME_FACTOR
            while clock() - start_time < 0.1:
                pass
            

