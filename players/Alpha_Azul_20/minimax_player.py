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

    def get_player_order(self, game_state):
        player_order = []
        for i in range(self.id + 1, len(game_state.players)):
            player_order.append(i)
        for i in range(0, self.id + 1):
            player_order.append(i)
        return player_order

    def evaluate(self, game_state):
        """
        Simple evaluation of game state using player scores 
        """
        enemy_id = self.id*-1 + 1
        game_state_eval = copy.deepcopy(game_state)            

        #score, tiles = game_state_eval.players[self.id].ScoreRound()
        #score2, tiles2 = game_state_eval.players[enemy_id].ScoreRound()
        round_num = (4 - len(game_state.bag) // 20) 

        game_state_eval.ExecuteEndOfRound()                       

        #player_order = self.get_player_order(game_state_eval) 
        #player_expect_score = Reward(game_state_eval, self.id, player_order).get_round_expection()
        #opponent_expect_score = Reward(game_state_eval, enemy_id, player_order).get_round_expection()        

        player_score_change = game_state_eval.players[self.id].player_trace.round_scores[-1]
        enemy_score_change = game_state_eval.players[enemy_id].player_trace.round_scores[-1]

        player_bonus = game_state_eval.players[self.id].EndOfGameScore()
        opponent_bonus =game_state_eval.players[enemy_id].EndOfGameScore() 

        player_bonus = player_bonus*0.7**(4-round_num)
        opponent_bonus = opponent_bonus*0.7**(4-round_num)


        player_final =  player_score_change + player_bonus
        opponent_final = enemy_score_change + opponent_bonus

        return player_final - opponent_final


    def minimax(self, game_state, depth, alpha, beta, maximizing=True):
       
        # check terminal state 
        is_terminal = False
        for plr_state in game_state.players:
            if plr_state.GetCompletedRows() > 0 :
                is_terminal = True
                break

        # reached end of round but not end of game
        is_round_end = False
        if not is_terminal and game_state.TilesRemaining() == 0:
            is_round_end = True            

        # base case 
        if depth == 0 or is_terminal or is_round_end :
            V = self.evaluate(game_state)
            return (None, V)

            '''
            if is_terminal or is_round_end:
                if V > 0: # we win
                    return (None, 100000000)
                elif V < 0: # opponent wins
                    return (None, -100000000)
                else: # draw
                    return (None, 0)
            else: # depth is zero or we reached end of the round
                return (None, V)
            '''

        # maximizing player case 
        if maximizing: 
            value = -math.inf
            # node expansion 
            moves = game_state.players[self.id].GetAvailableMoves(game_state)            
            best_move = moves[0]

            p1, p2, p3, p4, p5 = [], [], [], [], []
            move_dict = {}

            for move in moves: 
                if move[2].num_to_floor_line>1 or move[2].pattern_line_dest == -1:
                    continue                

                tile_type = move[2].tile_type
                p_dest = move[2].pattern_line_dest

                numoffset = move[2].num_to_pattern_line - move[2].num_to_floor_line

                if (tile_type, p_dest) not in move_dict or numoffset>move_dict[(tile_type, p_dest)][0]:
                    move_dict[(tile_type, p_dest)] = (numoffset, move)

            moves = [v[1] for k, v  in move_dict.items() ]

            #print('====lenmove', len(moves))
            #print('lenDICT', len(move_dict))
            #print(move_dict)
            
            #print('len: ', len(moves) , moves)

            for move in moves: 
                game_state_copy = copy.deepcopy(game_state)
                #c_score_player,_ = Reward(game_state_copy, self.id, self.get_player_order(game_state_copy)).estimate(move)
                game_state_copy.ExecuteMove(self.id, move)                
                new_value = self.minimax(game_state_copy, depth-1, alpha, beta,  False)[1]
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

            move_dict = {}
            
            for move in moves: 
                if move[2].num_to_floor_line>1 or move[2].pattern_line_dest == -1:
                    continue                

                tile_type = move[2].tile_type
                p_dest = move[2].pattern_line_dest

                numoffset = move[2].num_to_pattern_line - move[2].num_to_floor_line

                if (tile_type, p_dest) not in move_dict or numoffset>move_dict[(tile_type, p_dest)][0]:
                    move_dict[(tile_type, p_dest)] = (numoffset, move)

            moves = [v[1] for k, v  in move_dict.items() ]

            for move in moves:
                #floor = move[2].num_to_floor_line
                #if len(moves) > 2 and floor>1:
                #    continue
                game_state_copy = copy.deepcopy(game_state)
                #c_score_enemy,_ = Reward(game_state_copy, self.id*-1 + 1, self.get_player_order(game_state_copy)).estimate(move)
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

        depth = 2

        move, minimax_score = self.minimax(game_state, depth, -math.inf, math.inf, True)
        #print(minimax_score)

        return move


