from data import *
from chessBoard import *


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


class WMGame(Game):
    square_content = {
        -1: "X",
        +0: "-",
        +1: "O"
    }

    def __init__(self):
        self.n = LENGTH_OF_BOARD

    def getInitBoard(self):
        '''
        按照顶部为0，广度优先标记Board
        '''
        # return initial board (numpy board)
        b = WMBoard(self.n)
        return np.array(b.pieces)

    def getBoardSize(self):
        return self.n

    def getActionSize(self):
        # return number of actions
        return self.n * self.n + 1

    def getNextState(self, board, player, action):
        # if player takes action on board, return next (board,player)
        # action must be a valid move
        if action == self.n * self.n:
            return (board, -player)
        b = Board(self.n)
        b.pieces = np.copy(board)
        move = (int(action / self.n), action % self.n)
        b.execute_move(move, player)
        return (b.pieces, -player)

    def getValidMoves(self, board, player):
        # return a fixed size binary vector
        valids = [0] * self.getActionSize()
        b = Board(self.n)
        b.pieces = np.copy(board)
        legalMoves = b.get_legal_moves(player)
        if len(legalMoves) == 0:
            valids[-1] = 1
            return np.array(valids)
        for x, y in legalMoves:
            valids[self.n * x + y] = 1
        return np.array(valids)

    def getGameEnded(self, board, player):
        # return 0 if not ended, 1 if player 1 won, -1 if player 1 lost
        # player = 1
        b = Board(self.n)
        b.pieces = np.copy(board)
        if b.has_legal_moves(player):
            return 0
        if b.has_legal_moves(-player):
            return 0
        if b.countDiff(player) > 0:
            return 1
        return -1

    def getCanonicalForm(self, board, player):
        # return state if player==1, else return -state if player==-1
        return player * board

    def getSymmetries(self, board, pi):
        # mirror, rotational
        assert (len(pi) == self.n ** 2 + 1)  # 1 for pass
        pi_board = np.reshape(pi[:-1], (self.n, self.n))
        l = []

        for i in range(1, 5):
            for j in [True, False]:
                newB = np.rot90(board, i)
                newPi = np.rot90(pi_board, i)
                if j:
                    newB = np.fliplr(newB)
                    newPi = np.fliplr(newPi)
                l += [(newB, list(newPi.ravel()) + [pi[-1]])]
        return l

    def stringRepresentation(self, board):
        return board.tostring()

    def stringRepresentationReadable(self, board):
        board_s = "".join(self.square_content[square] for row in board for square in row)
        return board_s

    def getScore(self, board, player):
        b = Board(self.n)
        b.pieces = np.copy(board)
        return b.countDiff(player)

    @staticmethod
    def display(board):
        n = board.shape[0]
        print("   ", end="")
        for y in range(n):
            print(y, end=" ")
        print("")
        print("-----------------------")
        for y in range(n):
            print(y, "|", end="")  # print the row #
            for x in range(n):
                piece = board[y][x]  # get the piece to print
                print(OthelloGame.square_content[piece], end=" ")
            print("|")

        print("-----------------------")
