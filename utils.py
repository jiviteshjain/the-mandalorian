import os
import numpy as np
from colorama import init as cinit
from colorama import Fore, Back, Style
import random
from time import monotonic as clock
import random

import config as conf
from obstacle import Coin

def intersect(rec_a, rec_b):
    if type(rec_a) != list or type(rec_b) != list or len(rec_a) != 4 or len(rec_b) != 4:
        raise ValueError

    # [x_start, x_end, y_start, y_end]

    x_start = max(rec_a[0], rec_b[0])
    x_end = min(rec_a[1], rec_b[1])
    y_start = max(rec_a[2], rec_b[2])
    y_end = min(rec_a[3], rec_b[3])

    if x_start > x_end or y_start > y_end:
        return False, [0, 0, 0, 0]
    else:
        return True, [x_start, x_end, y_start, y_end]


def get_art(path):
    path = os.path.join(conf.ART_BASE_PATH, path)
    arr = []
    try:
        with open(path, 'r') as f:
            for line in f:
                arr.append(list(line.strip('\n')))
    except FileNotFoundError as e:
        return None

    return np.array(arr, dtype='object')

def make_coin_group(game_height, game_width, x=0, y=0, h=1, w=1):
    
    coins = []
    for i in range(h):
        drawing = False
        for j in range(w):
            if not drawing:
                if random.random() < 0.65:
                    drawing = True
            if drawing:
                coins.append(Coin(game_height, game_width, x + i, y + j))
                if random.random() < 0.3:
                    drawing = False
                    break
    
    return coins