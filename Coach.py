import logging
import os
import sys
from collections import deque
from pickle import Pickler, Unpickler
from random import shuffle

import cv2
import numpy as np
from tqdm import tqdm

from Arena import Arena
from MCTS import MCTS
from watermelon_chess.common import create_directory, draw_chessmen, BACKGROUND, \
    write_msg, PROCEDURE_PATH
from watermelon_chess.tensor_board_tool import my_summary
from watermelon_chess.wm_games_evaluater import RandomPlayer

log = logging.getLogger(__name__)


class Coach:
    """
    This class executes the self-play + learning. It uses the functions defined
    in Game and NeuralNet. args are specified in main.py.
    """

    def __init__(self, game, nnet, args):
        self.game = game
        self.nnet = nnet
        self.pnet = self.nnet.__class__(self.game)  # the competitor network
        self.args = args
        self.mcts = MCTS(self.game, self.nnet, self.args)
        self.trainExamplesHistory = []  # history of examples from args.numItersForTrainExamplesHistory latest iterations
        self.skipFirstSelfPlay = False  # can be overriden in loadTrainExamples()

    def write_file(self, epoch_idx, step, self_play_idx, board, key):
        epoch_directory = PROCEDURE_PATH / (key + "_epoch_" + str(epoch_idx))
        self.create_procedure_directory(epoch_directory)

        self_play_directory = epoch_directory / (key + "_self_play_" + str(self_play_idx))
        self.create_procedure_directory(self_play_directory)

        step_directory = self_play_directory / (key + "_step_" + str(step))
        self.create_procedure_directory(step_directory)

        name = step_directory / f"chess_board"
        image = cv2.imread(str(BACKGROUND))
        draw_chessmen(board, image, True, name)

    def create_procedure_directory(self, directory):
        if not os.path.exists(directory):
            create_directory(directory)

    def write_result(self, directory, is_peace, r):
        path = directory / "result.txt"
        if r != 0 or is_peace:
            msg = f'：{"Exist result" if r != 0 else "No Result"}, {"Is Draw" if is_peace else ""}'
            write_msg(msg, path)

    def executeEpisode(self, epoch_idx, self_play_idx, is_write):
        """
        This function executes one episode of self-play, starting with player 1.
        As the game is played, each turn is added as a training example to
        trainExamples. The game is played till the game ends. After the game
        ends, the outcome of the game is used to assign values to each example
        in trainExamples.

        It uses a temp=1 if episodeStep < tempThreshold, and thereafter
        uses temp=0.

        Returns:
            trainExamples: a list of examples of the form (canonicalBoard, currPlayer, pi,v)
                           pi is the MCTS informed policy vector, v is +1 if
                           the player eventually won the game, else -1.
        """
        trainExamples = []
        board = self.game.getInitBoard()
        self.curPlayer = 1
        episodeStep = 0
        while True:
            episodeStep += 1
            canonicalBoard = self.game.getCanonicalForm(board, self.curPlayer)

            temp = int(episodeStep < self.args.tempThreshold)

            pi = self.mcts.getActionProb(canonicalBoard, temp=temp, epoch_idx=epoch_idx, self_play_idx=self_play_idx)
            sym = self.game.getSymmetries(canonicalBoard, pi)
            for b, p in sym:
                trainExamples.append([b, self.curPlayer, p, None])

            action = np.random.choice(len(pi), p=pi)
            board, self.curPlayer = self.game.getNextState(board, self.curPlayer, action)

            r = self.game.getGameEnded(board, self.curPlayer)
            if is_write:
                self.write_file(epoch_idx, episodeStep, self_play_idx, board, "in_episode")
            if r != 0:
                my_summary.add_float(x=epoch_idx * self.args.numEps + self_play_idx, y=episodeStep,
                                     title="Steps of one episode in Play(Training stage)")
                return [(x[0], x[2], r * ((-1) ** (x[1] != self.curPlayer))) for x in trainExamples]

    def _is_write(self):
        if np.random.uniform(0, 1, 1).item() < 0.01:
            return True
        return False

    def learn(self):
        """
        Performs numIters iterations with numEps episodes of self-play in each
        iteration. After every iteration, it retrains neural network with
        examples in trainExamples (which has a maximum length of maxlenofQueue).
        It then pits the new neural network against the old one and accepts it
        only if it wins >= updateThreshold fraction of games.
        """

        for i in range(1, self.args.numIters + 1):
            # bookkeeping
            log.info(f'Starting Iter #{i} ...')
            # examples of the iteration
            if not self.skipFirstSelfPlay or i > 1:
                iterationTrainExamples = deque([], maxlen=self.args.maxlenOfQueue)

                for idx in tqdm(range(self.args.numEps), desc="Self Play"):
                    self.mcts = MCTS(self.game, self.nnet, self.args)  # reset search tree
                    iterationTrainExamples += self.executeEpisode(i, idx, self._is_write())

                # save the iteration examples to the history
                self.trainExamplesHistory.append(iterationTrainExamples)

            if len(self.trainExamplesHistory) > self.args.numItersForTrainExamplesHistory:
                log.warning(
                    f"Removing the oldest entry in trainExamples. len(trainExamplesHistory) = {len(self.trainExamplesHistory)}")
                self.trainExamplesHistory.pop(0)
            # backup history to a file
            # NB! the examples were collected using the model from the previous iteration, so (i-1)
            self.saveTrainExamples(i - 1)

            # shuffle examples before training
            trainExamples = []
            for e in self.trainExamplesHistory:
                trainExamples.extend(e)
            shuffle(trainExamples)

            # training new network, keeping a copy of the old one
            self.nnet.save_checkpoint(folder=self.args.checkpoint, filename='temp.pth.tar')
            self.pnet.load_checkpoint(folder=self.args.checkpoint, filename='temp.pth.tar')
            pmcts = MCTS(self.game, self.pnet, self.args)

            self.nnet.train(trainExamples, i)
            nmcts = MCTS(self.game, self.nnet, self.args)

            second_player = lambda x: np.argmax(nmcts.getActionProb(x, temp=0))

            first_player = lambda x: np.argmax(pmcts.getActionProb(x, temp=0))
            log.info('PITTING AGAINST PREVIOUS VERSION')
            arena = Arena(first_player,
                          second_player, self.game)
            pwins, nwins, draws = arena.playGames(self.args.arenaCompare, iter=i)
            my_summary.add_float(x=i, y=i, title="Training Epoch")
            my_summary.add_float(x=i, y=nwins, title="New Player Winning times")
            my_summary.add_float(x=i, y=pwins, title="Old Player Wining times")
            my_summary.add_float(x=i, y=draws, title="Draws times")

            log.info('NEW/PREV WINS : %d / %d ; DRAWS : %d' % (nwins, pwins, draws))
            if pwins + nwins == 0 or float(nwins) / (pwins + nwins) < self.args.updateThreshold:
                log.info('REJECTING NEW MODEL')
                self.nnet.load_checkpoint(folder=self.args.checkpoint, filename='temp.pth.tar')
            else:
                log.info('ACCEPTING NEW MODEL')
                self.nnet.save_checkpoint(folder=self.args.checkpoint, filename=self.getCheckpointFile(i))
                self.nnet.save_checkpoint(folder=self.args.checkpoint, filename='best.pth.tar')
            if pwins + nwins == 0:
                win_rate = -1
            else:
                win_rate = float(nwins) / (pwins + nwins)
            my_summary.add_float(x=i, y=win_rate, title="Winning Rate")

    def getCheckpointFile(self, iteration):
        return 'checkpoint_' + str(iteration) + '.pth.tar'

    def saveTrainExamples(self, iteration):
        folder = self.args.checkpoint
        if not os.path.exists(folder):
            os.makedirs(folder)
        filename = os.path.join(folder, self.getCheckpointFile(iteration) + ".examples")
        with open(filename, "wb+") as f:
            Pickler(f).dump(self.trainExamplesHistory)
        f.closed

    def loadTrainExamples(self):
        modelFile = os.path.join(self.args.load_folder_file[0], self.args.load_folder_file[1])
        examplesFile = modelFile + ".examples"
        if not os.path.isfile(examplesFile):
            log.warning(f'File "{examplesFile}" with trainExamples not found!')
            r = input("Continue? [y|n]")
            if r != "y":
                sys.exit()
        else:
            log.info("File with trainExamples found. Loading it...")
            with open(examplesFile, "rb") as f:
                self.trainExamplesHistory = Unpickler(f).load()
            log.info('Loading done!')

            # examples based on the model were already collected (loaded)
            self.skipFirstSelfPlay = True
