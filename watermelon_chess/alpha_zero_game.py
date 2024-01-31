from Game import Game
import numpy as np

from watermelon_chess.alpha_zero_board import WMBoard
from watermelon_chess.common import MOVE_TO_INDEX_DICT
from watermelon_chess.data import LENGTH_OF_BOARD


class WMGame(Game):

    def __init__(self):

        super().__init__()

    def getInitBoard(self):
        b = WMBoard()
        return np.array(b.pointStatus)

    def getBoardSize(self):
        return LENGTH_OF_BOARD

    def getActionSize(self):
        return len(MOVE_TO_INDEX_DICT)

    def getNextState(self, point_status, player, action):
        b = WMBoard()
        b.pointStatus = np.copy(point_status)
        b.execute_move(action, player)
        return b.pointStatus, -player

    def getValidMoves(self, point_status, player):
        # TODO://压缩一下空间，因为邻接点固定，还没想好，可以使用固定的映射，这个方法没测试
        valids = [0] * self.getActionSize()
        b = WMBoard()
        b.pointStatus = np.copy(point_status)

        legal_moves_list = b.get_legal_moves(player)
        for x, y in legal_moves_list:
            valids[LENGTH_OF_BOARD * x + y] = 1
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


if __name__ == '__main__':
    wm_ame = WMGame()
    test_point = wm_ame.getInitBoard()
    # point = wm_ame.getNextState(test_point, 1, (2, 20))
    legal_moves = wm_ame.getValidMoves(test_point, 1)
    print(legal_moves)
