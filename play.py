import os
import numpy as np
from colorama import init as cinit

from game import Game
import config as conf

cinit()

game = Game()
game.play()