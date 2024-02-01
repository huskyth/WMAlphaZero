from Game import Game
import numpy as np

from watermelon_chess.alpha_zero_board import WMBoard
from watermelon_chess.common import MOVE_TO_INDEX_DICT, from_array_to_input_tensor
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
        valids = [0] * self.getActionSize()
        b = WMBoard()
        b.pointStatus = np.copy(point_status)

        legal_moves_list = b.get_legal_moves(player)
        for move_tuple in legal_moves_list:
            idx = MOVE_TO_INDEX_DICT[move_tuple]
            valids[idx] = 1
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

    def getCanonicalForm(self, point_status, player):
        return player * point_status

    def getSymmetries(self, board, pi):
        # TODO://可以是左右翻转、上下、左右同时上下
        # 此方法暂时不实现，不一定要使用，实现较为复杂
        return None

    def stringRepresentation(self, point_status):
        return point_status.tostring()

    @staticmethod
    def display(board):
        pass


if __name__ == '__main__':
    wm_ame = WMGame()
    test_point = wm_ame.getInitBoard()
    point, _ = wm_ame.getNextState(test_point, 1, (2, 16))
    # legal_moves = wm_ame.getValidMoves(test_point, -1)
    x = from_array_to_input_tensor(point)
    print(x)
