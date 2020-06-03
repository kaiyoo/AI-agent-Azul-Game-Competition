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
from keras.models import model_from_json
import json
import numpy as np
import tensorflow as tf
from tensorflow.python.keras.backend import set_session
from display_utils import *

class myPlayer(AdvancePlayer):
    def __init__(self, _id):
        super().__init__(_id)
        self.tmp_idx = 9999
        self.err_count = 0
        self.total_count = 0

        #self.base_state = np.zeros(85) #47 7 132 85 (1,85)
        self.sess = tf.Session()
        self.graph = tf.get_default_graph()
        self.sess.run(tf.global_variables_initializer())
        set_session(self.sess)        

        json_file = open('players/model.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()        
        loaded_model = model_from_json(loaded_model_json)
        loaded_model.load_weights("players/model.h5")
        loaded_model.compile(loss='mse', optimizer = 'rmsprop', metrics=['accuracy'])
        loaded_model._make_predict_function()
        self.loaded_model = loaded_model       

        json_file = open('players/generalized_moves.json')
        json_str = json_file.read()
        self.generalized_moves=json.loads(json_str)     


    def get_player_order(self, game_state):
        player_order = []
        for i in range(self.id + 1, len(game_state.players)):
            player_order.append(i)
        for i in range(0, self.id + 1):
            player_order.append(i)
        return player_order


    def get_move(self, move):  

        move =  str(TileToShortString(move[2].tile_type)) + '/' \
             + str(move[2].pattern_line_dest) + '/'+ str(move[2].num_to_pattern_line) + '/' + str(move[2].num_to_floor_line)
        return move

    def get_FactoryCentre(self, game_state):
        factory_list = []
        for i in range(5):             
            factory = game_state.factories[i].tiles
            for j in range(len(factory)):
                factory_list.append(factory[j])            

        for j in range(len(game_state.centre_pool.tiles)):
            factory_list.append(game_state.centre_pool.tiles[j])
        
        return factory_list


    def get_fullfeatures(self, move, game_state, state_feature, round_count):   

        state_feature_copy = copy.deepcopy(state_feature)
        move_idx = self.get_int(move) 
        move_idx.append(round_count)
        factory_list = self.get_FactoryCentre(game_state)
        state_feature_copy.extend(factory_list)
        state_feature_copy.extend(move_idx) 
        base = state_feature_copy

        return base, move_idx

    def get_statefeatures(self, game_state, state_feature, round_count):  

        state_feature_copy = copy.deepcopy(state_feature)
        #factory_list = self.get_FactoryCentre(game_state)
        #state_feature_copy.extend(factory_list)
        state_feature_copy.append(round_count)

        return state_feature_copy


    def SelectMove(self, moves, game_state):
        best_move = None        
        self.total_count +=1

        plr_state = game_state.players[self.id]
        enemy_state = game_state.players[self.id*-1 + 1]

        gs_copy = copy.deepcopy(game_state)
        moves_copy = copy.deepcopy(moves)
        state_feature = StateToArray(self.id, plr_state)
        state_feature_enemy = StateToArray(self.id*-1 + 1, enemy_state)      
        state_feature.extend(state_feature_enemy)

        round_num = (4 - len(game_state.bag) // 20) #from 0
        state = []

        s_features = self.get_statefeatures(gs_copy, state_feature, round_num)  
        state = s_features 

        available_actions_list = []
        total_idx = 0
        for available_idx, move in enumerate(moves_copy):              
            try:
                total_idx = self.generalized_moves[self.get_move(move)]
            except:
                total_idx = 0
                self.err_count +=1
                pass

            available_actions_list.append([total_idx, available_idx])


        inp = np.array([state])    

        with self.graph.as_default():
            set_session(self.sess)

            preds = self.loaded_model.predict(inp)[0]      
            maxval = 0
            maxtotalidx = 0
            maxavailidx = 0
            for total_idx, available_idx in available_actions_list:
                val = preds[total_idx]
                if val > maxval:
                    maxval = val
                    maxtotalidx = total_idx
                    maxavailidx = available_idx

        best_move = moves_copy[maxavailidx]  

        return best_move


def B2N(binary, i, j):
    arr = [[],[],[],[],[]]
    #arr [0] = ['B', 'Y', 'R', 'K', 'W']
    #arr [1] = ['W' ,'B','Y','R','K']
    #arr [2] = ['K', 'W', 'B', 'Y', 'R']
    #arr [3] = ['R', 'K', 'W', 'B', 'Y']
    #arr [4] = ['Y', 'R', 'K', 'W', 'B']
    arr [0] = [2, 5, 1, 4, 3]
    arr [1] = [3 ,2, 5, 1, 4]
    arr [2] = [4, 3, 2, 5, 1]
    arr [3] = [1, 4, 3, 2, 5]
    arr [4] = [5, 1, 4, 3, 2]

    if binary == 0:
        return 0
    else:
        return arr[i][j]

def StateToArray(player_id, ps):

    pattern_line_arr = []
    grid_arr = []

    for i in range(ps.GRID_SIZE):
        if ps.lines_tile[i] != -1:
            tt = ps.lines_tile[i]
            ts = TileToNum(tt)
            num = ps.lines_number[i]

            for j in range(num):
                pattern_line_arr.append(ts)

            for j in range(num, i+1):
                pattern_line_arr.append(0)

        else:
            assert ps.lines_number[i] == 0
            for j in range(i+1):
                pattern_line_arr.append(0)


    for i in ps.floor:        
        if i == 1:
            pattern_line_arr.append(-1)
        else:
            pattern_line_arr.append(0)

    grid_arr.append(B2N(ps.grid_state[0][0], 0, 0))
    grid_arr.append(B2N(ps.grid_state[0][1], 0, 1))
    grid_arr.append(B2N(ps.grid_state[0][2], 0, 2))
    grid_arr.append(B2N(ps.grid_state[0][3], 0, 3))
    grid_arr.append(B2N(ps.grid_state[0][4], 0, 4))                

    #i == 1:
    grid_arr.append(B2N(ps.grid_state[1][0], 1, 0))
    grid_arr.append(B2N(ps.grid_state[1][1], 1, 1))
    grid_arr.append(B2N(ps.grid_state[1][2], 1, 2))
    grid_arr.append(B2N(ps.grid_state[1][3], 1, 3))
    grid_arr.append(B2N(ps.grid_state[1][4], 1, 4))  
    #i == 2:
    grid_arr.append(B2N(ps.grid_state[2][0], 2, 0))
    grid_arr.append(B2N(ps.grid_state[2][1], 2, 1))
    grid_arr.append(B2N(ps.grid_state[2][2], 2, 2))
    grid_arr.append(B2N(ps.grid_state[2][3], 2, 3))
    grid_arr.append(B2N(ps.grid_state[2][4], 2, 4))  
    #i == 3:    
    grid_arr.append(B2N(ps.grid_state[3][0], 3, 0))
    grid_arr.append(B2N(ps.grid_state[3][1], 3, 1))
    grid_arr.append(B2N(ps.grid_state[3][2], 3, 2))
    grid_arr.append(B2N(ps.grid_state[3][3], 3, 3))
    grid_arr.append(B2N(ps.grid_state[3][4], 3, 4))  
    #i == 4:
    grid_arr.append(B2N(ps.grid_state[4][0], 4, 0))
    grid_arr.append(B2N(ps.grid_state[4][1], 4, 1))
    grid_arr.append(B2N(ps.grid_state[4][2], 4, 2))
    grid_arr.append(B2N(ps.grid_state[4][3], 4, 3))
    grid_arr.append(B2N(ps.grid_state[4][4], 4, 4))  

    pattern_line_arr.extend(grid_arr)

    return pattern_line_arr
