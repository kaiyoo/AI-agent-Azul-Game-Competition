import heapq
import math
from typing import Union, List
import copy

from advance_model import *
from utils import *
import numpy as np
import players.myPlayer as mp
import players.random_player
import players.naive_player


class MCTNode(object):
    def __init__(self, parent, game_state: GameState, id, current_move):
        self.q_value = 0
        self.parent = parent
        self.visit_times = 0
        self.children: List[MCTNode] = []
        self.moves = game_state.players[id].GetAvailableMoves(game_state)
        self.current_move = current_move
        self.g_state: GameState = game_state
        self.player_id = id

    def is_fully_expanded(self):
        for child in self.children:
            if child.visit_times == 0:
                return False
        return True

    def get_unexpanded_move(self):
        for child in self.children:
            if child.visit_times == 0:
                return child

        return None

    def get_best_value_child(self):

        best_child = self.children[0]
        for child in self.children:
            if child.q_value > best_child.q_value:
                best_child = child
        return best_child

    def get_best_uct_child(self):

        best_child = self.children[0]
        for child in self.children:
            if child.calculate_uct() > best_child.calculate_uct():
                best_child = child
        return best_child

    def calculate_uct(self):
        uct = self.q_value + 2 / math.sqrt((math.log(self.parent.visit_times)) / self.visit_times)
        return uct

    def update(self):

        self.visit_times += 1
        s1, s2 = 0, 0
        for child in self.children:
            s1 += child.visit_times * child.q_value
            s2 += child.visit_times
        self.q_value = s1 / s2

    def is_round_end(self):
        return not self.g_state.TilesRemaining()


class myPlayer(AdvancePlayer):
    def __init__(self, _id):
        super().__init__(_id)
        self.current_node = None

    def get_player_state(self, game_state: GameState) -> Union[PlayerState, None]:

        for ps in game_state.players:
            if ps.id == self.id:
                return ps
        return None

    def get_competitor_player_state(self, game_state: GameState) -> Union[PlayerState, None]:

        for ps in game_state.players:
            if ps.id != self.id:
                return ps
        return None

    def SelectMove(self, moves, game_state):
        # initialization
        my_player_state = self.get_player_state(game_state)
        c_player_state = self.get_competitor_player_state(game_state)
        best_move = None
        current = MCTNode(parent=None, game_state=game_state, id=self.id, current_move=None)
        mcts = MCTS(current)
        best_move = mcts.search()
        return best_move


class MCTS(object):
    """A simple implementation of Monte Carlo Tree Search.
    """

    def __init__(self, root):
        self.root: MCTNode = root

    def run_rollout(self):
        expand_node = self.Select(self.root)
        if expand_node is None:
            return True
        self.Expand(expand_node)

        reward = self.Simulation(expand_node)

        self.Backpropagate(expand_node, reward)
        return False

    def Select(self, current: MCTNode):
        current = self.root
        while not current.is_round_end():
            if len(current.children) == 0:
                return current
            if not current.is_fully_expanded():
                child = current.get_unexpanded_move()
                return child
            else:
                child = current.get_best_uct_child()
                current = child
        return None

    def Expand(self, expand_node):
        id = None
        for i in expand_node.g_state.players:
            if i.id != expand_node.player_id:
                id = i.id
        for m in expand_node.moves:
            game_state: GameState = copy.deepcopy(expand_node.g_state)
            game_state.ExecuteMove(expand_node.player_id, m)
            c = MCTNode(parent=expand_node, game_state=game_state, id=id, current_move=m)
            expand_node.children.append(c)
    def Backpropagate(self, expand_node, reward):

        expand_node.visit_times += 1

        op_id = None
        for i in expand_node.g_state.players:
            if i.id != expand_node.player_id:
                op_id = i.id
        expand_node.q_value = reward[self.root.player_id] - reward[op_id]
        node = expand_node.parent
        while node:
            node.update()
            node = node.parent

    def Simulation(self, node: MCTNode):

        state = copy.deepcopy(node.g_state)
        while state.TilesRemaining():
            for p in state.players:
                if not state.TilesRemaining():
                    break
                player =players.random_player.myPlayer(p.id)
                state.ExecuteMove(p.id, player.SelectMove(p.GetAvailableMoves(state),state))
        state.ExecuteEndOfRound()
        reward = {}
        for p in state.players:
            reward[p.id] = p.score
        return reward

    def search(self):
        for i in range(20):
            self.run_rollout()
            if self.run_rollout is True:
                break
        child: MCTNode
        child = self.root.get_best_value_child()
        move = child.current_move
        return move


class PriorityQueue:
    """
      Implements a priority queue data structure. Each inserted item
      has a priority associated with it and the client is usually interested
      in quick retrieval of the lowest-priority item in the queue. This
      data structure allows O(1) access to the lowest-priority item.
    """

    def __init__(self):
        self.heap = []
        self.count = 0

    def push(self, item, priority):
        entry = (priority, self.count, item)
        heapq.heappush(self.heap, entry)
        self.count += 1

    def pop(self):
        (_, _, item) = heapq.heappop(self.heap)
        return item

    def isEmpty(self):
        return len(self.heap) == 0

    def update(self, item, priority):
        # If item already in priority queue with higher priority, update its priority and rebuild the heap.
        # If item already in priority queue with equal or lower priority, do nothing.
        # If item not in priority queue, do the same thing as self.push.
        for index, (p, c, i) in enumerate(self.heap):
            if i == item:
                if p <= priority:
                    break
                del self.heap[index]
                self.heap.append((priority, c, item))
                heapq.heapify(self.heap)
                break
        else:
            self.push(item, priority)
