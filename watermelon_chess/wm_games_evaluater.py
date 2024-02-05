import copy
import time

import Arena
from MCTS import MCTS

import numpy as np
from utils import *
from watermelon_chess.alpha_zero_game import WMGame
from watermelon_chess.common import DISTANCE, MODEL_PATH, MOVE_TO_INDEX_DICT, draw_chessmen, read_image, BACKGROUND
from watermelon_chess.control import computerMove
from watermelon_chess.models.nn_net import WMNNetWrapper


class RandomPlayer:
    def __init__(self, game):
        self.game = game

    def play(self, board):
        a = np.random.randint(self.game.getActionSize())
        valids = self.game.getValidMoves(board, 1)
        while valids[a] != 1:
            a = np.random.randint(self.game.getActionSize())
        return a


class GreedyPlayer:
    @staticmethod
    def greedy_action(point_status):
        level = 1
        point_status_copy = copy.deepcopy(point_status)
        a, _ = computerMove(point_status_copy, DISTANCE, level)
        if a is None:
            draw_chessmen(point_status, read_image(BACKGROUND), False, f"{time.time()}_{a}")

        a = MOVE_TO_INDEX_DICT[a]
        return a


class GamesEvaluate:

    @staticmethod
    def execute_game_test(game, neural_net, name=None):
        rp = RandomPlayer(game).play
        greedy_player = GreedyPlayer.greedy_action

        args = dotdict({'numMCTSSims': 25, 'cpuct': 1.0})

        net_player = neural_net(game)
        if name is not None:
            net_player.load_checkpoint(MODEL_PATH, name)

        mcts = MCTS(game, net_player, args)
        n1p = lambda x: np.argmax(mcts.getActionProb(x, temp=0))

        arena = Arena.Arena(greedy_player, rp, game)
        one_won, two_won, draws = arena.playGames(40, verbose=False)
        print(f"greedy_player won {one_won}, rp Won {two_won}, peace {draws}")

    def wm_pytorch(self):
        self.execute_game_test(WMGame(), WMNNetWrapper, name="temp.pth1024.tar")


if __name__ == '__main__':
    GamesEvaluate().wm_pytorch()
