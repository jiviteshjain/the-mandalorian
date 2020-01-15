import os
import numpy as np
from colorama import init as cinit
from colorama import Fore, Back, Style
import random
from time import monotonic as clock

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