import copy
import json
import os

import cv2
import numpy
import numpy as np

from pathlib import Path

MENU = 'resources/images/menu.png'
BACKGROUND = 'resources/images/watermelon.png'
QUERY_BKG = 'resources/images/queryBkg.png'
BLACKTILE = 'resources/images/black.png'
WHITETILE = 'resources/images/white.png'
HAND = 'resources/images/hand.png'
START = 'resources/images/start.png'
CONGRATULATION = 'resources/images/congratulation.png'
PITY = 'resources/images/pity.png'
BACK = 'resources/images/back.png'
BACK_RECT = ((460, 400), 117, 50)
REPLAY = 'resources/images/replay.png'
REPLAY_RECT = ((460, 300), 117, 50)
LOCALGAME = 'resources/images/localGame.png'
LOCALGAME_RECT = ((232, 200), 117, 50)
NETWORKGAME = 'resources/images/networkGame.png'
NETWORKGAME_RECT = ((232, 300), 117, 50)
QUIT = 'resources/images/quit.png'
MENU_QUIT_RECT = ((232, 400), 117, 50)
PLAY_QUIT_RECT = ((460, 400), 117, 50)
CONFIRM = 'resources/images/confirm.png'
CONFIRM_RECT = ((173, 400), 80, 49)
CANCEL = 'resources/images/cancel.png'
CANCEL_RECT = ((291, 400), 80, 49)

SCREEN_WIDTH = 580
SCREEN_HEIGHT = 580
FULLSCREENMOD = False
CHESSMAN_WIDTH = 20
CHESSMAN_HEIGHT = 20
BLACK = 1
BLACK_COLOR = (0, 0, 0)
WHITE = -1
WHITE_COLOR = (255, 255, 255)
COMPUTER = 1
PLAYER = 2

LENGTH_OF_BOARD = 21

ROOT_PATH = Path(os.path.abspath(__file__)).parent.parent
DISTANCEPATH = str(ROOT_PATH / 'watermelon_chess/resources/data/distance.txt')
FONT = str(ROOT_PATH / 'watermelon_chess/resources/font/arial.ttf')
MAPPATH = str(ROOT_PATH / 'watermelon_chess/resources/data/pointPos.txt')


def getNeighboors(chessman, distance):
    neighboorChessmen = []
    for eachChessman, eachDistance in enumerate(distance[chessman]):
        if eachDistance == 1:
            neighboorChessmen.append(eachChessman)
    return neighboorChessmen


def get_distance():
    try:
        f = open(DISTANCEPATH, 'rb')
        distance = json.loads(f.read())
        return distance
    except Exception as e:
        print(f'file open error {e}')
        return None
    finally:
        f.close()


def get_map():
    try:
        f = open(MAPPATH, 'rb')
        point_pos = json.loads(f.read())
        return point_pos
    except Exception as e:
        print(f'file open error {e}')
        return None
    finally:
        f.close()


DISTANCE = get_distance()
GAME_MAP = get_map()
MOVE_TO_INDEX_DICT = {}
INDEX_TO_MOVE_DICT = {}
MOVE_LIST = []
# MOVE_LIST从小到大排列
for from_point in range(21):
    to_point_list = getNeighboors(from_point, DISTANCE)
    to_point_list = sorted(to_point_list)
    for to_point in to_point_list:
        MOVE_LIST.append((from_point, to_point))
for idx, move_string in enumerate(MOVE_LIST):
    MOVE_TO_INDEX_DICT[move_string] = idx
    INDEX_TO_MOVE_DICT[idx] = move_string

# TODO://对于7x7的矩阵映射关系
ARRAY_TO_IMAGE = {
    0: (0, 3), 15: (6, 3), 6: (3, 0), 10: (3, 6),
    1: (0, 2), 3: (0, 4), 2: (1, 3),
    4: (2, 0), 7: (4, 0), 5: (3, 1),
    8: (2, 6), 9: (3, 5), 11: (4, 6),
    12: (5, 3), 13: (6, 2), 14: (6, 4),
    20: (3, 3),
    16: (2, 3), 17: (3, 2), 18: (3, 4), 19: (4, 3)
}


def from_array_to_input_tensor(numpy_array):
    assert len(numpy_array) == 21
    assert isinstance(numpy_array, numpy.ndarray)
    input_tensor = np.zeros((7, 7))
    for i, chessman in enumerate(numpy_array):
        row, column = ARRAY_TO_IMAGE[i]
        input_tensor[row, column] = chessman
    return input_tensor


def create_directory(path):
    if not os.path.exists(str(path)):
        os.mkdir(str(path))


def draw_circle(image, x, y, color):
    cv2.circle(image, (int(x + CHESSMAN_WIDTH / 2), int(y + CHESSMAN_HEIGHT / 2)), CHESSMAN_HEIGHT // 2, color, -1)


def write_image(name, image):
    cv2.imwrite(f"{name}.png", image)


def read_image(path):
    return cv2.imread(path)


def draw_chessmen(point_status, image, is_write, name):
    image = copy.deepcopy(image)
    for index, point in enumerate(point_status):
        if point == 0:
            continue
        (x, y) = fix_xy(index)
        if point == BLACK:
            draw_circle(image, x, y, BLACK_COLOR)
        elif point == WHITE:
            draw_circle(image, x, y, (255, 0, 0))
    if is_write:
        write_image(name, image)


def fix_xy(target):
    x = GAME_MAP[target][0] * \
        SCREEN_WIDTH - CHESSMAN_WIDTH * 0.5
    y = GAME_MAP[target][1] * \
        SCREEN_HEIGHT - CHESSMAN_HEIGHT * 1
    return x, y
