import json

from watermelon_chess import data


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
