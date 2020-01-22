import math
import time
import numpy as np

def shift_up(arr):
    temp = np.array([[' ' for j in range(arr.shape[1])] for i in range(arr.shape[0])], dtype='object')
    for i in range(1, arr.shape[0]):
        temp[i - 1] = arr[i]
    return temp

def shift_down(arr):
    temp = np.array([[' ' for j in range(arr.shape[1])] for i in range(arr.shape[0])], dtype='object')
    for i in range(arr.shape[0] - 1):
        temp[i + 1] = arr[i]
    return temp

h = 6
w = 30
total_range = 2 * math.pi
part = total_range / w

phase = 0
counter = 0
big_counter = 0
head = np.array([[' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                 ['~', '~', '%', '%', 'z', ' ', ' ', ' ', ' ', ' '],
                 ['~', '~', '~', '(', 'O', 'O', ')', ' ', ' ', ' '],
                 ['~', '~', ' ', '*', '`', ':', ':', '\\', '\\', ' '],
                 [' ', ' ', ' ', ' ', ' ', ' ', ' ', '`', '@', '@'],
                 [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']], dtype='object')
while True:
    input_arr = [(-math.pi + (i * part) + phase) for i in range(w)]
    sin_arr = np.sin(np.array(input_arr, dtype='float32')) * (3)

    dragon = np.array([['~' for j in range(w)] for i in range(h)], dtype='object')

    for j in range(w):
        for i in range(min(0, int(round(sin_arr[j]))), max(0, int(round(sin_arr[j])))):
            dragon[i][j] = ' '

    dragon = np.concatenate((dragon, head), axis=1)
    print(dragon.shape)
    # print("\033[0;0H")
    # print("\033[2J")
    for i in range(dragon.shape[0]):
        for j in range(dragon.shape[1]):
            print(dragon[i][j], end='')
        print('')
    phase += 0.1
    big_counter += 1
    if big_counter % 15 == 0:
        if counter % 4 == 0:
            head = shift_up(head)
        elif counter % 4 == 1:
            head = shift_down(head)
        elif counter % 4 == 2:
            head = shift_down(head)
        else:
            head = shift_up(head)
        counter += 1
    time.sleep(0.1)
