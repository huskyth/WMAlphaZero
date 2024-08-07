import logging
import math

import cv2
import numpy as np

from utils import dotdict
from watermelon_chess.alpha_zero_game import WMGame
from watermelon_chess.common import WHITE, BLACK, INDEX_TO_MOVE_DICT, draw_chessmen, BACKGROUND, DISTRIBUTION_PATH, \
    create_directory, bar_show, ROOT_PATH
from watermelon_chess.models.nn_net import WMNNetWrapper

EPS = 1e-8

log = logging.getLogger(__name__)


class _MCTS:
    """
    This class handles the MCTS tree.
    """

    def __init__(self, game, nnet, args):
        self.game = game
        self.nnet = nnet
        self.args = args
        self.Qsa = {}  # stores Q values for s,a (as defined in the paper)
        self.Nsa = {}  # stores #times edge s,a was visited
        self.Ns = {}  # stores #times board s was visited
        self.Ps = {}  # stores initial policy (returned by neural net)

        self.Es = {}  # stores game.getGameEnded ended for board s
        self.Vs = {}  # stores game.getValidMoves for board s

        self.VL = {}  # stores game.getValidMoves for board s
        self.is_write = False

    def reset(self):
        self.Qsa = {}  # stores Q values for s,a (as defined in the paper)
        self.Nsa = {}  # stores #times edge s,a was visited
        self.Ns = {}  # stores #times board s was visited
        self.Ps = {}  # stores initial policy (returned by neural net)

        self.Es = {}  # stores game.getGameEnded ended for board s
        self.Vs = {}  # stores game.getValidMoves for board s

        self.VL = {}  # stores game.getValidMoves for board s

    def getActionProb(self, canonicalBoard, temp=1, epoch_idx=-1, self_play_idx=-1, episode_step=-1,
                      train_or_test="training", player="None"):
        """
        This function performs numMCTSSims simulations of MCTS starting from
        canonicalBoard.

        Returns:
            probs: a policy vector where the probability of the ith action is
                   proportional to Nsa[(s,a)]**(1./temp)
        """
        for i in range(self.args.numMCTSSims):
            self.search(canonicalBoard, epoch_idx, self_play_idx, i, 0, episode_step, train_or_test, player)

        s = self.game.stringRepresentation(canonicalBoard)
        counts = [self.Nsa[(s, a)] if (s, a) in self.Nsa else 0 for a in range(self.game.getActionSize())]

        if temp == 0:
            bestAs = np.array(np.argwhere(counts == np.max(counts))).flatten()
            bestA = np.random.choice(bestAs)
            probs = [0] * len(counts)
            probs[bestA] = 1
            return probs

        counts = [x ** (1. / temp) for x in counts]
        counts_sum = float(sum(counts))
        probs = [x / counts_sum for x in counts]
        return probs

    @staticmethod
    def judge_peace_by_chessman_num(board, no_change_num_list, max_step=1200):
        '''
            no_change_num = [前一次的数目，计数]
        '''
        assert len(no_change_num_list) == 2
        sum_of_all = WMGame.count_chessman(board, WHITE) + WMGame.count_chessman(board, BLACK)
        if no_change_num_list[0] is None and no_change_num_list[1] is None:
            no_change_num_list[0] = sum_of_all
            no_change_num_list[1] = 1
            return False
        if sum_of_all == no_change_num_list[0]:
            no_change_num_list[1] += 1
            if no_change_num_list[1] == max_step:
                return True
        else:
            no_change_num_list[0] = sum_of_all
            no_change_num_list[1] = 0
            return False
        return False

    def write_txt(self, path, epoch_idx=-1, self_play_idx=-1, search_idx=-1, board=None, key="", depth=-1, x=None,
                  y=None,
                  type_str=None):
        with open(path, 'a') as f:
            n = len(x)
            f.write(f"{search_idx}th searching\n")
            f.write(f"\t{depth}th depth\n")
            content = "\t"
            for i in range(n):
                x_item, y_item = x[i], y[i]
                content += f"action_idx {x_item} {type_str} {y_item} "
            f.write(content + '\n')

    def write_file(self, epoch_idx=-1, self_play_idx=-1, search_idx=-1, board=None, key="", depth=-1, x=None, y=None,
                   type_str=None, episode_step=-1, train_or_test="training", player="None"):

        root_directory = f"{train_or_test}_epoch_{epoch_idx}_self_play_{self_play_idx}_{player}"
        root_directory = DISTRIBUTION_PATH / root_directory
        create_directory(root_directory)

        step_directory = root_directory / f"{episode_step}th_step"
        create_directory(step_directory)

        name = step_directory / f"distribute_{type_str}"

        self.write_txt(str(name) + '.txt', epoch_idx, self_play_idx, search_idx, board, key, depth, x, y, type_str)
        # image = cv2.imread(str(BACKGROUND))
        # draw_chessmen(board, image, True, str(name) + "_image")
        #
        # bar_show(x, y, is_show=False, name=str(name) + ".png")

    def search(self, canonicalBoard, epoch_idx=-1, self_play_idx=-1, search_idx=-1, depth=-1, episode_step=-1,
               train_or_test="training", player="None"):
        """
        This function performs one iteration of MCTS. It is recursively called
        till a leaf node is found. The action chosen at each node is one that
        has the maximum upper confidence bound as in the paper.

        Once a leaf node is found, the neural network is called to return an
        initial policy P and a value v for the state. This value is propagated
        up the sepath. In case the leaf node is a terminal state, the
        outcome is propagated up the search path. The values of Ns, Nsa, Qsa are
        updated.

        NOTE: the return values are the negative of the value of the current
        state. This is done since v is in [-1,1] and if v is the value of a
        state for the current player, then its value is -v for the other player.

        Returns:
            v: the negative of the value of the current canonicalBoard
        """

        s = self.game.stringRepresentation(canonicalBoard)

        if s not in self.Es:
            self.Es[s] = self.game.getGameEnded(canonicalBoard, 1)
        if self.Es[s] != 0:
            # terminal node
            return -self.Es[s]

        if s not in self.Ps:
            # leaf node
            self.Ps[s], v = self.nnet.predict(canonicalBoard)
            valids = self.game.getValidMoves(canonicalBoard, 1)
            self.Ps[s] = self.Ps[s] * valids  # masking invalid moves
            sum_Ps_s = np.sum(self.Ps[s])
            if sum_Ps_s > 0:
                self.Ps[s] /= sum_Ps_s  # renormalize
            else:
                # if all valid moves were masked make all valid moves equally probable

                # NB! All valid moves may be masked if either your NNet architecture is insufficient or you've get overfitting or something else.
                # If you have got dozens or hundreds of these messages you should pay attention to your NNet and/or training process.   
                log.error("All valid moves were masked, doing a workaround.")
                self.Ps[s] = self.Ps[s] + valids
                self.Ps[s] /= np.sum(self.Ps[s])

            self.Vs[s] = valids
            self.Ns[s] = 0
            return -v.item()

        valids = self.Vs[s]
        cur_best = -float('inf')
        best_act = -1

        temp_x, temp_u, temp_n = [], [], []
        # pick the action with the highest upper confidence bound
        for a in range(self.game.getActionSize()):
            if valids[a]:
                visual_loss = self.VL[(s, a)] if (s, a) in self.VL else 0
                visual_loss = visual_loss / (1 + self.Nsa[(s, a)]) if (s, a) in self.Nsa else visual_loss
                if (s, a) in self.Qsa:
                    u = self.Qsa[(s, a)] + self.args.cpuct * self.Ps[s][a] * math.sqrt(self.Ns[s]) / (
                            1 + self.Nsa[(s, a)])
                else:
                    u = self.args.cpuct * self.Ps[s][a] * math.sqrt(self.Ns[s] + EPS)  # Q = 0 ?
                u -= visual_loss
                temp_u.append(u)
                temp_x.append(a)

                temp_n.append(self.Nsa[(s, a)] if (s, a) in self.Nsa else -1)
                if u > cur_best:
                    cur_best = u
                    best_act = a
        temp_x, temp_u, temp_n = np.array(temp_x), np.array(temp_u), np.array(temp_n)
        if train_or_test == 'testing' or self.is_write:
            self.write_file(epoch_idx, self_play_idx, search_idx, canonicalBoard, "search", depth, temp_x, temp_u,
                            type_str="UValue", episode_step=episode_step, train_or_test=train_or_test, player=player)
            self.write_file(epoch_idx, self_play_idx, search_idx, canonicalBoard, "search", depth, temp_x, temp_n,
                            type_str="Count", episode_step=episode_step, train_or_test=train_or_test, player=player)

        a = best_act
        next_s, next_player = self.game.getNextState(canonicalBoard, 1, a)
        next_s = self.game.getCanonicalForm(next_s, next_player)
        temp = 1
        if (s, a) in self.VL:
            self.VL[(s, a)] += temp
        else:
            self.VL[(s, a)] = temp
        v = self.search(next_s, epoch_idx, self_play_idx, search_idx, depth + 1, episode_step, train_or_test, player)
        self.VL[(s, a)] -= temp
        if (s, a) in self.Qsa:
            self.Qsa[(s, a)] = (self.Nsa[(s, a)] * self.Qsa[(s, a)] + v) / (self.Nsa[(s, a)] + 1)
            self.Nsa[(s, a)] += 1

        else:
            self.Qsa[(s, a)] = v
            self.Nsa[(s, a)] = 1

        self.Ns[s] += 1
        return -v


def control_by_net_work(network, board, wm_game):
    board = np.array(board)
    board = wm_game.getCanonicalForm(board, 1)
    args = dotdict({'numMCTSSims': 9600, 'cpuct': 1.0})
    mcts = MCTS(wm_game, network, args)
    a = np.argmax(mcts.getActionProb(board, temp=0))
    a = INDEX_TO_MOVE_DICT[a]
    return a, -1


if __name__ == '__main__':
    temp = [0, 1, 1, 1, 1, -1, -1, 0, 1, 0, 0, 0, 0, 0, 1, 0, -1, -1, -1, -1, 0]
    image = cv2.imread(str(BACKGROUND))
    draw_chessmen(temp, image, True, "test")
    wm_game = WMGame()
    network = WMNNetWrapper(wm_game)
    network.load_checkpoint((ROOT_PATH / "temp"), "temp.pth.tar")
    y = control_by_net_work(network, temp, wm_game)
    print(y)
