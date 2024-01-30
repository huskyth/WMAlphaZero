import copy

from watermelon_chess.chessBoard import ChessBoard
from watermelon_chess.control import shiftOutChessman
from watermelon_chess.data import BLACK, WHITE


class WMBoard(ChessBoard):

    def __init__(self):
        super().__init__()

    # TODO:// test it
    def execute_move(self, move, color):
        from_int, to_int = move
        assert color == WHITE or color == BLACK
        assert self.pointStatus[from_int] == color
        assert self.pointStatus[to_int] == 0
        assert self.distance[from_int][to_int] == 1
        self.pointStatus[from_int] = 0
        self.pointStatus[to_int] = color
        bake_point_status = copy.deepcopy(self.pointStatus)
        self.pointStatus = shiftOutChessman(
            bake_point_status, self.distance)
