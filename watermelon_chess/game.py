from chessBoard import *
from watermelon_chess.common import *


class Game:

    def __init__(self):
        self.msg = None
        self.fullScreenMod = 0
        self.fullScreenModChanged = True
        self.status = 'menu'
        self.lastStatus = 'menu'
        self.nextStatus = 'menu'
        self.isOnline = False
        self.turn = 'none'
        self.opponentColor = BLACK
        self.playerColor = WHITE
        self.winner = None
        self.chessBoard = ChessBoard()
        self.gameMap = self.chessBoard.getGameMap()
        self.distance = self.chessBoard.getDistance()
        self.enableButton = [LOCALGAME_RECT,
                             NETWORKGAME_RECT, MENU_QUIT_RECT]
        self.roomID = 'local'
        self.name = 'default'
        self.opponent = 'computer'
        # self.url = 'http://localhost:8080/room/'
        self.url = 'http://xiguaqi.applinzi.com/room/'
        self.time = None
        self.resetGame()

    def resetGame(self):
        self.chessBoard.initPointStatus()
        self.chessBoard.initChessmanNum()
        self.over = False
        self.pointStatus = self.chessBoard.getPointStatus()
        self.chessmanInHand = False
        self.chosenChessmanColor = None
        self.chosenChessman = None
        self.checkedChessmen = []
        self.deadChessmen = []
        self.msg = 'initial'

    def strColor(self, color):
        if color == BLACK:
            color = 'BLACK'
        else:
            color = 'WHITE'
        return color
