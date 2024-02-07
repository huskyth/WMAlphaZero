import numpy as np


class LeafNode:
    def __init__(self, in_parent, in_prior_p, in_state):
        self.P = in_prior_p
        self.Q = 0
        self.N = 0
        self.v = 0
        self.U = 0
        self.W = 0
        self.parent = in_parent
        self.child = {}
        self.state = in_state

    def is_leaf(self):
        return self.child == {}

    def get_Q_plus_U_new(self, c_puct):
        """Calculate and return the value for this node: a combination of leaf evaluations, Q, and
        this node's prior adjusted for its visit count, u
        c_puct -- a number in (0, inf) controlling the relative impact of values, Q, and
            prior probability, P, on this node's score.
        """
        U = c_puct * self.P * np.sqrt(self.parent.N) / (1 + self.N)
        return self.Q + U

    def get_Q_plus_U(self, c_puct):
        """Calculate and return the value for this node: a combination of leaf evaluations, Q, and
        this node's prior adjusted for its visit count, u
        c_puct -- a number in (0, inf) controlling the relative impact of values, Q, and
            prior probability, P, on this node's score.
        """
        self.U = c_puct * self.P * np.sqrt(self.parent.N) / (1 + self.N)
        return self.Q + self.U

    def select_new(self, c_puct):
        return max(self.child.items(), key=lambda node: node[1].get_Q_plus_U_new(c_puct))

    def select(self, c_puct):
        return max(self.child.items(), key=lambda node: node[1].get_Q_plus_U(c_puct))

    # @profile
    def expand(self, moves, action_probs):
        tot_p = 1e-8
        action_probs = action_probs.flatten()  # .squeeze()
        for action in moves:
            in_state = GameBoard.sim_do_action(action, self.state)
            mov_p = action_probs[label2i[action]]
            new_node = leaf_node(self, mov_p, in_state)
            self.child[action] = new_node
            tot_p += mov_p

        for a, n in self.child.items():
            n.P /= tot_p

    def back_up_value(self, value):
        self.N += 1
        self.W += value
        self.v = value
        self.Q = self.W / self.N  # node.Q += 1.0*(value - node.Q) / node.N
        self.U = c_PUCT * self.P * np.sqrt(self.parent.N) / (1 + self.N)

    def backup(self, value):
        node = self
        while node is not None:
            node.N += 1
            node.W += value
            node.v = value
            node.Q = node.W / node.N
            node = node.parent
            value = -value
