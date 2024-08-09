import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from neural_network import ResidualBlock
from watermelon_chess.common import from_array_to_input_tensor


class WMNNet(nn.Module):
    def __init__(self, game, args):
        # game params
        self.board_x, self.board_y = game.getBoardSize()
        self.action_size = game.getActionSize()
        self.args = args
        self.num_channels = 256
        self.action_size = 21
        self.n = 7
        super(WMNNet, self).__init__()
        # residual block
        res_list = [ResidualBlock(3, self.num_channels)] + [ResidualBlock(self.num_channels, self.num_channels) for _ in
                                                            range(self.num_channels - 1)]
        self.res_layers = nn.Sequential(*res_list)

        # policy head
        self.p_conv = nn.Conv2d(self.num_channels, 4, kernel_size=1, padding=0, bias=False)
        self.p_bn = nn.BatchNorm2d(num_features=4)
        self.relu = nn.ReLU(inplace=True)

        self.p_fc = nn.Linear(4 * self.n ** 2, self.action_size)
        self.log_softmax = nn.LogSoftmax(dim=1)

        # value head
        self.v_conv = nn.Conv2d(self.num_channels, 2, kernel_size=1, padding=0, bias=False)
        self.v_bn = nn.BatchNorm2d(num_features=2)

        self.v_fc1 = nn.Linear(2 * self.n ** 2, 256)
        self.v_fc2 = nn.Linear(256, 1)
        self.tanh = nn.Tanh()

    @staticmethod
    def transfer_board(board):
        if isinstance(board, np.ndarray) and len(board) == 21:
            input_tensor = from_array_to_input_tensor(board)
            return input_tensor
        return board

    def forward(self, inputs):
        # residual block
        out = self.res_layers(inputs)

        # policy head
        p = self.p_conv(out)
        p = self.p_bn(p)
        p = self.relu(p)

        p = self.p_fc(p.view(p.size(0), -1))
        p = self.log_softmax(p)

        # value head
        v = self.v_conv(out)
        v = self.v_bn(v)
        v = self.relu(v)

        v = self.v_fc1(v.view(v.size(0), -1))
        v = self.relu(v)
        v = self.v_fc2(v)
        v = self.tanh(v)

        return p, v
