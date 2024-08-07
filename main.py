import logging
import os.path
import sys

import coloredlogs

from Coach import Coach
from utils import *
from watermelon_chess.alpha_zero_game import WMGame
from watermelon_chess.common import ROOT_PATH
from watermelon_chess.models.nn_net import WMNNetWrapper

log = logging.getLogger(__name__)

coloredlogs.install(level='INFO')  # Change this to DEBUG to see more info.

args = dotdict({
    'numIters': 1000,
    'numEps': 10,  # Number of complete self-play games to simulate during a new iteration.
    'tempThreshold': 150,  #
    'updateThreshold': 0.6,
    # During arena playoff, new neural net will be accepted if threshold or more of games are won.
    'maxlenOfQueue': 200000,  # Number of game examples to train the neural networks.
    'numMCTSSims': 1600,  # Number of games moves for MCTS to simulate.
    'arenaCompare': 10,  # Number of games to play during arena play to determine if new net will be accepted.
    'cpuct': 1,

    'checkpoint': str(ROOT_PATH / "temp"),
    'load_model': False,
    'load_folder_file': (str(ROOT_PATH / "temp"), 'best.pth.tar'),
    'numItersForTrainExamplesHistory': 20,

})


def judge_best_file():
    if os.path.exists(args.load_folder_file[0] + os.sep + args.load_folder_file[1]):
        args['load_model'] = True


def main():
    judge_best_file()
    log.info('Loading %s...', WMGame.__name__)
    g = WMGame()

    log.info('Loading %s...', WMNNetWrapper.__name__)
    nnet = WMNNetWrapper(g)

    if args.load_model:
        log.info('Loading checkpoint "%s/%s"...', args.load_folder_file[0], args.load_folder_file[1])
        nnet.load_checkpoint(args.load_folder_file[0], args.load_folder_file[1])
    else:
        log.warning('Not loading a checkpoint!')

    log.info('Loading the Coach...')
    c = Coach(g, nnet, args)

    if args.load_model:
        log.info("Loading 'trainExamples' from file...")
        c.loadTrainExamples()

    log.info('Starting the learning process 🎉')
    c.learn()


if __name__ == "__main__":
    main()
