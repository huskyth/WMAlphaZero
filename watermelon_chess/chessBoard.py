from watermelon_chess.common import *


class ChessBoard:

    def __init__(self):
        self.gameMap = []
        self.pointStatus = []
        self.distance = []
        self.status = None
        self.whiteNum = 6
        self.blackNum = 6
        self.msg = None
        self.initDistance()
        self.initPointStatus()
        self.initGameMap()

    def getGameMap(self):
        return self.gameMap

    def getPointStatus(self):
        return self.pointStatus

    def getDistance(self):
        return self.distance

    def initDistance(self):
        self.distance = DISTANCE

    def initPointStatus(self):
        self.pointStatus = []
        black = [0, 1, 2, 3, 4, 8]
        white = [7, 11, 12, 13, 14, 15]
        for x in range(LENGTH_OF_BOARD):
            self.pointStatus.append(0)
        for x in black:
            self.pointStatus[x] = BLACK
        for x in white:
            self.pointStatus[x] = WHITE

    def initChessmanNum(self):
        self.whiteNum = 6
        self.blackNum = 6

    def initGameMap(self):
        self.gameMap = GAME_MAP
