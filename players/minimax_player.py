# Written by Michelle Blom, 2019
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
from advance_model import *
from utils import *
import math
import copy 

class myPlayer(AdvancePlayer):
    def __init__(self, _id):
        super().__init__(_id)

    def evaluate(self, game_state):
        """
        Simple evaluation of game state using player scores 
        """
        return game_state.players[self.id].score - game_state.players[self.id*-1 + 1].score


    def minimax(self, game_state, depth, alpha, beta, maximizing=True):
       
        # check terminal state 
        is_terminal = False
        for plr_state in game_state.players:
            if plr_state.GetCompletedRows() > 0 :
                is_terminal = True
                break

        # reached end of round but not end of game
        is_round_end = False
        if not is_terminal and game_state.TilesRemaining() ==0:
            is_round_end = True
            

        # base case 
        if depth == 0 or is_terminal or is_round_end :

            V = self.evaluate(game_state)

            if is_terminal or is_round_end:
                if V > 0: # we win
                    return (None, 100000000)
                elif V < 0: # opponent wins
                    return (None, -100000000)
                else: # draw
                    return (None, 0)
            else: # depth is zero or we reached end of the round
                return (None, V)

        # maximizing player case 
        if maximizing: 
            value = -math.inf
            # node expansion 
            moves = game_state.players[self.id].GetAvailableMoves(game_state)
            best_move = moves[0]
            for move in moves: 
                game_state_copy = copy.deepcopy(game_state)
                game_state_copy.ExecuteMove(self.id, move)
                new_value = self.minimax(game_state_copy, depth-1, alpha, beta, False)[1]
                if new_value > value:
                    value = new_value
                    best_move = move
                alpha = max(alpha, value)
                if alpha >= beta:
                    break

            return best_move, value 
        
        # minimizing player case
        else: 
            value = math.inf
            moves = game_state.players[self.id*-1 + 1].GetAvailableMoves(game_state)
            best_move = moves[0]
            for move in moves:
                game_state_copy = copy.deepcopy(game_state)
                game_state_copy.ExecuteMove(self.id*-1 + 1, move)
                new_value = self.minimax(game_state_copy, depth-1, alpha, beta, True)[1]
                if new_value < value:
                    value = new_value
                    best_move = move
                beta = min(beta, value)
                if alpha >= beta:
                    break

            return best_move , value 

    def SelectMove(self, moves, game_state):
        
        plr_state = game_state.players[self.id]
        print("AZUL > Player {} is now in control\n".format(self.id))

        print("------------")
        print("Game State") 
        print("------------")
        print(BoardToString(game_state))

        print("------------")
        print("Player State") 
        print("------------")
        print(PlayerToString(self.id, plr_state))

        depth = 3
        move, minimax_score = self.minimax(game_state, depth, -math.inf, math.inf, True)
        print(minimax_score)

        return move
