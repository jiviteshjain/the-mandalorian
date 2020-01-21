import os
import numpy as np
from colorama import init as cinit

from game import Game
import config as conf

cinit()
print('\033[2J')
game = Game()
game.play()
