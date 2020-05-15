import os
import numpy as np
from colorama import init as cinit
from colorama import Fore, Back, Style
import random
import time

import config as conf
import utils

class Screen:
    '''
    encapsulates printing and screen management
    in each frame, all objects are added to the screen according to updated positions, sizes and representations provided by them, and screen prints it all
    manages a static background array and a dynamic foreground array
    '''

    CURSOR_0 = "\033[0;0H"
    CLEAR = "\033[2J"

    def __init__(self, height, width):
        self._height = height
        self._width = width
        
        self._back_board = np.array([[conf.BG_COLOR for j in range(self._width)] for i in range(self._height)], dtype='object')
        for i in range(self._height):
            for j in range(self._width):
                if random.random() < conf.ACCENT_AMT: # random black dots
                    self._back_board[i][j] = conf.BG_ACCENT_COLOR

        # color the ground and the ceiling
        for i in range(self._height - conf.GND_HEIGHT, self._height):
            for j in range(self._width):
                self._back_board[i][j] = conf.GND_COLOR

        for i in range(conf.SKY_DEPTH):
            for j in range(self._width):
                self._back_board[i][j] = conf.SKY_COLOR
        

        self._fore_board = np.array([[' ' for j in range(self._width)] for i in range(self._height)], dtype='object')

    def clear(self):
        '''
        clears the foreground
        '''

        for i in range(self._height):
            for j in range(self._width):
                self._fore_board[i][j] = ' '

    def add(self, obj):
        '''
        add an object to the screen
        '''

        # object is not visible, prevent index out of bounds errors
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
        except (IndexError, ValueError) as e: # skip rendering for this frame in case of error
            return

    def print_board(self, frame_count):
        '''
        renders the screen
        '''

        print(self.CURSOR_0)
        for i in range(self._height):
            for j in range(self._width): # frame count is used to move the black dots at the same rate as the game
                print(self._back_board[i][(j + frame_count) % self._width] + self._fore_board[i][j], end='')
            print('')

    def flash(self, color, frame_count, times=3):
        '''
        flashes the screen while halting and maintaining state to alert the user
        '''

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
        '''
        print the game over screen
        '''

        print(Style.RESET_ALL + self.CLEAR + self.CURSOR_0 + '\n\n\n')
        
        if won:
            yoda = utils.get_art('yoda.txt')
            if yoda is not None: # if file not available, skip
                print(Fore.YELLOW, end='')
                for i in range(yoda.shape[0]):
                    for j in range(yoda.shape[1]):
                        print(yoda[i][j], end='')
                    print('')
                time.sleep(2)
                print(Style.RESET_ALL + self.CLEAR + self.CURSOR_0 + '\n\n\n')
        
        go_text = utils.get_art('game-over.txt')
        if go_text is not None: # if file not available, skip
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
        

        


