from Game import Game
import numpy as np

from watermelon_chess.alpha_zero_board import WMBoard
from watermelon_chess.common import MOVE_TO_INDEX_DICT, from_array_to_input_tensor, LENGTH_OF_BOARD, INDEX_TO_MOVE_DICT


class WMGame(Game):

    def __init__(self):

        super().__init__()

    def getInitBoard(self):
        b = WMBoard()
        return np.array(b.pointStatus)

    def getBoardSize(self):
        return 7, 7

    def getActionSize(self):
        return len(MOVE_TO_INDEX_DICT)

    def _transfer_action(self, action):
        if isinstance(action, int):
            action = INDEX_TO_MOVE_DICT[action]
        return action

    def getNextState(self, point_status, player, action):
        b = WMBoard()
        b.pointStatus = np.copy(point_status)
        action = self._transfer_action(action)
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

    def getGameEnded(self, point_status, player):
        b = WMBoard()
        b.pointStatus = np.copy(point_status)
        winner = b.check_winner()
        if winner is None:
            return 0
        return 1 if winner == player else -1

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
    # point = wm_ame.getNextState(test_point, 1, (2, 20))
    # legal_moves = wm_ame.getValidMoves(test_point, -1)
    test_point[0:4] = 0
    print(test_point)
    print(wm_ame.getGameEnded(test_point, -1))
