import json

from watermelon_chess import data
from watermelon_chess.control import getNeighboors


def get_distance():
    try:
        f = open(data.DISTANCEPATH, 'rb')
        distance = json.loads(f.read())
        return distance
    except Exception as e:
        print(f'file open error {e}')
        return None
    finally:
        f.close()


DISTANCE = get_distance()
MOVE_TO_INDEX_DICT = {}
INDEX_TO_MOVE_DICT = {}
MOVE_LIST = []
for from_point in range(21):
    to_point_list = getNeighboors(from_point, DISTANCE)
    to_point_list = sorted(to_point_list)
    for to_point in to_point_list:
        MOVE_LIST.append((from_point, to_point))
for idx, move_string in enumerate(MOVE_LIST):
    MOVE_TO_INDEX_DICT[move_string] = idx
    INDEX_TO_MOVE_DICT[idx] = move_string
