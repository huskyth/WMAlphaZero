from watermelon_chess.chessBoard import ChessBoard
from watermelon_chess.common import *


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

    def get_legal_moves(self, player):
        assert player in [WHITE, BLACK]
        legal_moves_list = []
        for from_point_idx, chessman in enumerate(self.pointStatus):
            if chessman != player:
                continue
            to_point_idx_list = getNeighboors(from_point_idx, self.distance)
            for to_point_idx in to_point_idx_list:
                to_point = self.pointStatus[to_point_idx]
                if to_point != 0:
                    continue
                legal_moves_list.append((from_point_idx, to_point_idx))
        return legal_moves_list

    def check_winner(self):
        black_num = 0
        white_num = 0
        winner = None
        for color in self.pointStatus:
            if color == BLACK:
                black_num += 1
            elif color == WHITE:
                white_num += 1
        if black_num < 3 or white_num < 3:
            if black_num < 3:
                winner = WHITE
            else:
                winner = BLACK

        return winner


if __name__ == '__main__':
    image = read_image(BACKGROUND)
    wm_board = WMBoard()
    frame_list = []
    for i in range(105):
        np.random.shuffle(wm_board.pointStatus)
        temp = draw_chessmen(wm_board.pointStatus, image, False, f"test_{i}")
        frame_list.append(temp)
    write_video(frame_list, "test")
    print("saved")
