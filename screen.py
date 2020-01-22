import os
import numpy as np
from colorama import init as cinit
from colorama import Fore, Back, Style
import random
import time

import config as conf
import utils

class Screen:

    CURSOR_0 = "\033[0;0H"
    CLEAR = "\033[2J"

    def __init__(self, height, width):
        self._height = height
        self._width = width
        
        self._back_board = np.array([[conf.BG_COLOR for j in range(self._width)] for i in range(self._height)], dtype='object')
        for i in range(self._height):
            for j in range(self._width):
                # if (i + j) % 30 == 0 or (i - j) % 30 == 0:
                if random.random() < conf.ACCENT_AMT:
                    self._back_board[i][j] = conf.BG_ACCENT_COLOR

        for i in range(self._height - conf.GND_HEIGHT, self._height):
            for j in range(self._width):
                self._back_board[i][j] = conf.GND_COLOR

        for i in range(conf.SKY_DEPTH):
            for j in range(self._width):
                self._back_board[i][j] = conf.SKY_COLOR
        

        # self.CLOUD_REPR = get_art(conf.ART_CLOUD_PATH)
        # if conf.NUM_CLOUDS > 0:
        #     cloud_part = int(self._width / conf.NUM_CLOUDS)
        #     for i in range(conf.NUM_CLOUDS):
        #         start_y = random.randint(i * cloud_part, (i + 1) * cloud_part - self.CLOUD_REPR.shape[1])
        #         start_x = random.randint(conf.SKY_DEPTH, conf.SKY_DEPTH + 3)
        #         for j in range(self.CLOUD_REPR.shape[0]):
        #             for k in range(self.CLOUD_REPR.shape[1]):
        #                 self._back_board[start_x + j][start_y + k] += (Fore.BLACK + self.CLOUD_REPR[j][k])
        

        self._fore_board = np.array([[' ' for j in range(self._width)] for i in range(self._height)], dtype='object')

        # self.bottom_bar = np.array([[conf.BOTTOM_BAR_COLOR + ' ' for j in range(self._width)] for i in range(conf.BOTTOM_BAR_HEIGHT)])

    def clear(self):
        # for i in range(self._height):
        #     for j in range(self._width):
        #         if random.random() < conf.ACCENT_AMT:
        #             self._back_board[i][j] = conf.BG_ACCENT_COLOR
        #         else:
        #             self._back_board[i][j] = conf.BG_COLOR
        
        # for i in range(self._height - conf.GND_HEIGHT, self._height):
        #     for j in range(self._width):
        #         self._back_board[i][j] = conf.GND_COLOR

        # for i in range(conf.SKY_DEPTH):
        #     for j in range(self._width):
        #         self._back_board[i][j] = conf.SKY_COLOR

        for i in range(self._height):
            for j in range(self._width):
                self._fore_board[i][j] = ' '

    def add(self, obj):
        if True in obj.is_out():
            return

        pos, size, front = obj.show()
        
        x_start = pos[0]
        x_start_ = 0
        x_end = pos[0] + size[0]
        x_end_ = size[0]
        y_start = pos[1]
        y_start_ = 0
        y_end = pos[1] + size[1]
        y_end_ = size[1]

        # Now make sure if half the object is visible, it is rendered correctly

        if x_start < 0:
            x_start_ = 0 - x_start
            x_start = 0

        if y_start < 0:
            y_start_ = 0 - y_start
            y_start = 0

        if x_end > self._height:
            x_end_ = self._height - pos[0]
            x_end = self._height

        if y_end > self._width:
            y_end_ = self._width - pos[1]
            y_end = self._width

        try:
            self._fore_board[x_start:x_end, y_start:y_end] = front[x_start_:x_end_, y_start_:y_end_]
        except (IndexError, ValueError) as e:
            return

    def print_board(self, frame_count):
        print(self.CURSOR_0)
        for i in range(self._height):
            for j in range(self._width):
                print(self._back_board[i][(j + frame_count) % self._width] + self._fore_board[i][j], end='')
            print('')

    def flash(self, color, frame_count, times=3):
        temp = np.array([[color for j in range(self._width)] for i in range(self._height)], dtype='object')
        for _ in range(times):
            print(self.CURSOR_0)
            for i in range(self._height):
                for j in range(self._width):
                    print(temp[i][j], end='')
                print('')
            time.sleep(0.1)
            self.print_board(frame_count)
            time.sleep(0.2)

    def game_over(self, won, game_score, game_time):
        print(Style.RESET_ALL + self.CLEAR + self.CURSOR_0 + '\n\n\n')
        
        if won:
            yoda = utils.get_art('yoda.txt')
            if yoda is not None:
                print(Fore.YELLOW, end='')
                for i in range(yoda.shape[0]):
                    for j in range(yoda.shape[1]):
                        print(yoda[i][j], end='')
                    print('')
                time.sleep(2)
                print(Style.RESET_ALL + self.CLEAR + self.CURSOR_0 + '\n\n\n')
        
        go_text = utils.get_art('game-over.txt')
        if go_text is not None:
            print(Fore.GREEN, end='')
            for i in range(go_text.shape[0]):
                for j in range(go_text.shape[1]):
                    print(go_text[i][j], end='')
                print('')
        
        print('\n\n', end='')

        if won:
            print(Style.BRIGHT + Fore.YELLOW + 'YOU WON :)')
        else:
            print(Style.BRIGHT + Fore.RED + 'YOU LOST :(')

        print(Fore.WHITE, end='')
        print('Score:', game_score)
        print('Time:', game_time)

        print(Style.DIM + '\nPress F to exit')
        print(Style.RESET_ALL)
        

        


