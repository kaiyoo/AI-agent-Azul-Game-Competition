
#- args player_list, list of players
#- args seed, random seed used
#- args time_limit, time limit for each step, None for inf time
#- args warning_limit, timeout warnings 
#- args displayer, TextGameDisplayer, GUIDisplayer or None
#- args players_namelist, name to display
#- return replay, a dict

from model import *
from utils import *
from displayer import *
from func_timeout import func_timeout, FunctionTimedOut
import time
from players.reward import Reward
from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten
from keras.optimizers import rmsprop, Adam
from keras.regularizers import l2
from collections import deque
import tensorflow as tf
import numpy as np
import random
import json
from keras.models import model_from_json
#from experience_replay import ER

class AdvancePlayer(Player):
    def __init__(self, _id):
        super().__init__(_id)

    def StartRound(self,game_state):
        return None

    def SelectMove(self, moves, game_state):
        return random.choice(moves)

    
class AdvanceGameRunner:
    def __init__(self, 
                 player_list, 
                 seed=1, 
                 time_limit=1, 
                 startRound_time_limit = 1,
                 warning_limit=3, 
                 displayer = None, 
                 players_namelist = ["Alice","Bob"]):
        
        self.seed = seed
        random.seed(self.seed)
        self.seed_list = [random.randint(0,1e10) for _ in range(1000000)] #1000  random.randint(0,1e10)
        self.seed_idx = 0

        # Make sure we are forming a valid game, and that player
        # id's range from 0 to N-1, where N is the number of players.
        assert(len(player_list) <= 4)
        assert(len(player_list) > 1)

        i = 0
        for plyr in player_list:
            assert(plyr.id == i)    
            i += 1

        self.game_state = GameState(len(player_list))
        self.players = player_list
        self.players_namelist = players_namelist

        self.time_limit = time_limit
        self.startRound_time_limit = startRound_time_limit
        self.warning_limit = warning_limit
        self.warnings = [0]*len(player_list)
        self.warning_positions = []

        self.displayer = displayer
        
        if self.displayer is not None:
            self.displayer.InitDisplayer(self)

    def _EndGame(self,player_order,isTimeOut = True, id = None):
        player_traces = {"seed":self.seed,
                        "player_num":len(player_order),
                        "players_namelist":self.players_namelist,
                        "warning_positions":self.warning_positions,
                        "warning_limit":self.warning_limit}
        
        if isTimeOut:
            player_traces.update({id:[0, plr_state.player_trace] for id,plr_state in enumerate(self.game_state.players)})
            player_traces[id][0] = -1
            self.game_state.players[id].score = -1
        else:
            for i in player_order:
                plr_state = self.game_state.players[i]
                plr_state.EndOfGameScore()
                player_traces[i] = (plr_state.score, plr_state.player_trace)
    
        if self.displayer is not None:
            self.displayer.EndGame(self.game_state)

        return player_traces

    def get_int(self, move):  # Give the intㅇ representation(maping) of the move from the dictionary to give it as input for the deep neural network
        move =  str(TileToShortString(move[2].tile_type)) + '/' \
             + str(move[2].pattern_line_dest) + '/'+ str(move[2].num_to_pattern_line) + '/' + str(move[2].num_to_floor_line)
        # 5557
        try:
            return self.general_moves[move]
        except:
            self.general_moves[move]=len(self.general_moves)
            return self.general_moves[move]

    '''        
    def get_fullfeatures(self, move, state_feature):
        #state_feature_copy = state_feature
        move_idx=self.get_int(move)         
        #state_feature.append(move_idx) 
        state_feature.extend(move_idx) 
        #np_s_features = np.array(state_feature)
        #np_s_features = np_s_features.reshape((1, 48))

        return state_feature, move_idx
    '''
    def get_FactoryCentre(self, game_state):
        factory_list = []
        for i in range(5):             
            factory = game_state.factories[i].tiles
            for j in range(len(factory)):
                factory_list.append(factory[j])            

        for j in range(len(game_state.centre_pool.tiles)):
            factory_list.append(game_state.centre_pool.tiles[j])
        
        return factory_list

    def get_statefeatures(self, game_state, state_feature, round_count):  

        state_feature_copy = copy.deepcopy(state_feature)

        #factory_list = self.get_FactoryCentre(game_state)
        #state_feature_copy.extend(factory_list)

        state_feature_copy.append(round_count)

        return state_feature_copy

    def get_actionfeatures(self, move):      
        move_idx = self.get_int(move) 
        return move_idx

    def get_immediateReward(self, game_state, act_id, move, player_order):    
        my,_ = Reward(game_state, act_id, player_order).estimate(move)
        enemy,_ = Reward(game_state, act_id*-1 + 1, player_order).estimate(move)    
        immediate_reward = my - enemy

        return [my, enemy]

    def step(self, i, game_state, move, player_order, round_num):    

        done = False       
        game_state_copy = copy.deepcopy(game_state)  
        

        #print('ROUND: ', round_num, 'i', i , 'player_order?', player_order_copy)  

        #11
        #immediate_reward = 0
        c_score,_ = Reward(game_state_copy, i, player_order).estimate(move)
        #c_score = c_score

        game_state_copy.ExecuteMove(i, move)
        game_state_copy2 = copy.deepcopy(game_state)
        game_state_copy2.ExecuteEndOfRound()

        
        point = game_state_copy2.players[i].player_trace.round_scores[-1] - game_state_copy2.players[i*-1 + 1].player_trace.round_scores[-1]
        if i == 0:
            self.prev_0_point = point
            point = point - self.prev_0_point
        else:
            self.prev_1_point = point
            point = point - self.prev_1_point

        immediate_reward = (c_score + point)/5
        

        #game_state_copy2 = copy.deepcopy(game_state_copy) 
        #enemy_state = game_state_copy2.players[i*-1 + 1]
        #enemy_next_moves = enemy_state.GetAvailableMoves(game_state_copy2)
        #game_state_copy.ExecuteMove(i*-1 + 1, move)
        
        reward = 0
        enemy_reward = 0
        whole_reward = 0
        enemy_whole_reward = 0
        bonus = 0
        bonus2 = 0

        if not game_state_copy.TilesRemaining():
            round_reward = game_state_copy2.players[i].player_trace.round_scores[-1] - game_state_copy2.players[i*-1 + 1].player_trace.round_scores[-1]
            enemy_round_reward = game_state_copy2.players[i*-1 + 1].player_trace.round_scores[-1] - game_state_copy2.players[i].player_trace.round_scores[-1]   

            #if round_num >=4:
            bonus = game_state_copy2.players[i].EndOfGameScore() - game_state_copy2.players[i*-1 + 1].EndOfGameScore()
            bonus2 = game_state_copy2.players[i*-1 + 1].EndOfGameScore() - game_state_copy2.players[i].EndOfGameScore() 

            reward = (round_reward + bonus*0.5**(4-round_num))
            enemy_reward = (enemy_round_reward + bonus2*0.5**(4-round_num))

            if round_num >=4:
                game_reward = game_state_copy2.players[i].score - game_state_copy2.players[i*-1 + 1].score
                game_reward_enemy = game_state_copy2.players[i*-1 + 1].score - game_state_copy2.players[i].score

                whole_reward = game_reward*5
                enemy_whole_reward = game_reward_enemy*5

                #reward = reward*2
                #enemy_reward = enemy_reward*2
            

            #reward = game_state_copy2.players[i].score
            done = True

        plr_state = game_state_copy.players[i]
        enemy_state = game_state_copy.players[i*-1 + 1]
        next_moves = plr_state.GetAvailableMoves(game_state_copy)


        next_available_actions_list = []
        for available_idx, move in enumerate(next_moves):  
            total_idx = self.get_int(move)
            next_available_actions_list.append(total_idx)

        state_feature = StateToArray(i, plr_state)        
        state_feature_enemy = StateToArray(i*-1 + 1, enemy_state)      
        state_feature.extend(state_feature_enemy)

        next_state = []
        next_game_state = game_state_copy

        s_features = self.get_statefeatures(next_game_state, state_feature, round_num) 
        next_state =s_features

        return next_state, immediate_reward, reward, enemy_reward, whole_reward, enemy_whole_reward, done, next_available_actions_list


    def train_replay(self, flag, replay) :
        #if len(replay)>0:                        
        new_list = list(map(lambda x: x[0], replay))

        X = new_list #np.array(new_list)
        y = []                   
        r = 0                    
        #cnt = 0
        
        #print('after rev', reversed(replay)[0][0])
        #print('====================>>>', flag)
        for s, done, ir, r, wr, _s, _avail, idx in replay: 
            #print('replay enter')
            #cnt+=1            
            #if r>0:
            #    print(' R: ', r)

            if flag == 'long':                
                r = wr

            if not done : #r == 0.0: #update the reward if it's a non terminal step. the reward is 0 for all non terminal steps            
                next_preds = self.frozen_model.predict(np.array([_s]))[0]                                        

                maxval = 0
                for total_idx in _avail:
                    val = next_preds[total_idx]

                    if val > maxval:
                        maxval = val

                r = maxval*0.95 + r # gamma*Q(s', a)                

            #print('IR: ', ir, 'R: ', r)

            b = self.training_model.predict(np.array([s])) #setting the gradient of all the non action values to 0, kinda hacky but works
            #print('r: ',  r, 'IR: ', ir )
            r = r+ ir
            b[0][idx] = r
            y.append(b)       

        y = np.array(y)           

        if len(X) > 0:              
            for idx in range(len(X)):   
                #print('l:', y[idx].shape)                             
                #y_test = np.array(y[idx]) 
                X_train = np.array([X[idx]])
                y_train = y[idx]
                #print('YSHAPE: ',  y_train[0].shape)
                #print('m:', y_test.shape)    
                #y_test= y_test.reshape(150,1)  
                #print('n:', y_test.shape) 
                self.training_model.train_on_batch(X_train, y_train)

    def _run(self):
        self.game_state =  GameState(len(self.players))

        #model = self.model
        player_order = []
        for i in range(self.game_state.first_player, len(self.players)):
            player_order.append(i)

        for i in range(0, self.game_state.first_player):
            player_order.append(i)
            
        game_continuing = True
        round_count = 0
        move_count = 0        
        cnt_0=0
        cnt_1=0
        cnt_long_0=0
        cnt_long_1=0

        #pr 1
        for plr in self.game_state.players:
            plr.player_trace.StartRound()

        #pr 2
        for i in player_order:
            gs_copy = copy.deepcopy(self.game_state)
            #self.game_state = gs_copy
            try:
                func_timeout(self.startRound_time_limit,self.players[i].StartRound,args=(gs_copy,))
            except FunctionTimedOut:
                '''
                self.warnings[i] += 1
                if self.displayer is not None:
                    self.displayer.TimeOutWarning(self,i)
                self.warning_positions.append((i,round_count,-1))

                if self.warnings[i] == self.warning_limit:
                    player_traces = self._EndGame(player_order,isTimeOut=True,id=i)
                    return player_traces
                '''
            except AttributeError:
                pass

        #pr3                    
        random.seed(self.seed_list[self.seed_idx])
        self.seed_idx += 1

        if self.displayer is not None:
            self.displayer.StartRound(self.game_state)

        #pr4 : start play loop
        while game_continuing:
            round_num = (4 - len(self.game_state.bag) // 20)  ##from 0

            for i in player_order:
                plr_state = self.game_state.players[i]
                enemy_state = self.game_state.players[i*-1 + 1]                
                moves = plr_state.GetAvailableMoves(self.game_state)                

                if self.most_len < len(moves):
                    self.most_len = len(moves)

                gs_copy = copy.deepcopy(self.game_state)
                moves_copy = copy.deepcopy(moves)   
                selected = func_timeout(self.time_limit,self.players[i].SelectMove,args=(moves_copy, gs_copy))                

                if i == 0 or i ==1:
                    state_feature = StateToArray(i, plr_state)        
                    state_feature_enemy = StateToArray(i*-1 + 1, enemy_state)      
                    state_feature.extend(state_feature_enemy)

                    state = []
                    state_feature_copy = copy.deepcopy(state_feature)

                    preds= 0
                    move_idx = None

                    if random.random() <= self.epsilon:
                        self.eps +=1
                        #selected = func_timeout(self.time_limit,self.players[i].SelectMove,args=(moves_copy, gs_copy))   
                        #selected = func_timeout(self.time_limit,self.players[i].SelectMove,args=(moves_copy, gs_copy))  
                        
                        move_idx = self.get_int(selected)
                        s_features = self.get_statefeatures(gs_copy, state_feature_copy, round_num)      
                        state = s_features 

                    else:
                        s_features = self.get_statefeatures(gs_copy, state_feature_copy, round_num)  
                        state = s_features 

                        available_actions_list = []
                        for available_idx, move in enumerate(moves_copy):  
                            total_idx = self.get_int(move)
                            available_actions_list.append([total_idx, available_idx])
          

                        inp = np.array([state])     
                        preds = self.training_model.predict(inp)[0]      

                        maxval = 0
                        maxtotalidx = 0
                        maxavailidx = 0
                        for total_idx, available_idx in available_actions_list:
                            val = preds[total_idx]
                            if val > maxval:
                                maxval = val
                                maxtotalidx = total_idx
                                maxavailidx = available_idx

                        move_idx = maxtotalidx

                        #print('ELSE total_idx:  ', move_idx, '/', len(self.general_moves), 'Avail_idx: ', available_idx, '/', len(moves_copy))
                        
                        selected = moves_copy[maxavailidx]                            

                    self.epsilon = max(self.epsilon*0.995, 0.1)    

                    moves_len = len(moves_copy)        
            
                    next_state, immediate_reward, reward, enemy_reward, whole_reward, enemy_whole_reward, done, next_available_actions_list  = self.step(i, gs_copy, selected, player_order, round_num)

                    replay_0 = []
                    replay_1 = []
                    replay_long_0 = []
                    replay_long_1 = []

                    if i == 0:
                        cnt_0 +=1 
                        cnt_long_0 +=1 
                        self.experience_replay.store_0(state, done, immediate_reward, reward, whole_reward, next_state, next_available_actions_list, move_idx)                                               
                    else:
                        cnt_1 +=1
                        cnt_long_1 +=1 
                        self.experience_replay.store_1(state, done, immediate_reward, reward, whole_reward, next_state, next_available_actions_list, move_idx)                        

                    if done:
                        if i == 0:                   
                            cnt_1 +=1    
                            cnt_long_1 +=1 
                            del self.experience_replay.replay_1[-1]
                            del self.experience_replay.replay_long_1[-1]
                            self.experience_replay.store_1(self.prev_state, self.prev_done, self.prev_immediate_reward, enemy_reward, enemy_whole_reward, self.prev_next_state, self.prev_next_available_actions_list, self.prev_move_idx)
                        else:     
                            cnt_0 +=1
                            cnt_long_0 +=1 
                            del self.experience_replay.replay_0[-1] 
                            del self.experience_replay.replay_long_0[-1]                       
                            self.experience_replay.store_0(self.prev_state, self.prev_done, self.prev_immediate_reward, enemy_reward, enemy_whole_reward, self.prev_next_state, self.prev_next_available_actions_list, self.prev_move_idx)
                        
                        replay_0 = self.experience_replay.get_minibatch(0, cnt_0) #of size 5np.argmax(a)b[]   
                        replay_1 = self.experience_replay.get_minibatch(1, cnt_1) #of size 5np.argmax(a)b[]

                        if round_num == 4:
                            replay_long_0 = self.experience_replay.get_longbatch(0, cnt_long_0) #of size 5np.argmax(a)b[]   
                            replay_long_1 = self.experience_replay.get_longbatch(1, cnt_long_1) #of size 5np.argmax(a)b[]

                    else:
                        self.prev_state = state
                        self.prev_done = done
                        self.prev_immediate_reward = immediate_reward
                        #self.prev_reward = reward
                        #self.prev_whole_reward = whole_reward
                        self.prev_next_state = next_state
                        self.prev_next_available_actions_list = next_available_actions_list
                        self.prev_move_idx = move_idx


                    if len(replay_0)>0:
                        self.train_replay('', replay_0)

                    if len(replay_1)>0:
                        self.train_replay('', replay_1)

                    if len(replay_long_0)>0:
                        self.train_replay('long', replay_long_0)

                    if len(replay_long_1)>0:
                        self.train_replay('long', replay_long_1)

                    '''
                    if len(replay)>0:
                        
                        new_list = list(map(lambda x: x[0], replay))

                        #print('xTEST')
                        #print(len(new_list))

                        X = new_list #np.array(new_list)
                        y = []                   
                        r = 0                    
                        cnt = 0
                        for s, ir, r, _s, _avail, idx in replay: 
                            #print('replay enter')
                            cnt+=1
                            #print('before R: ', r)
                            if r == 0 : #r == 0.0: #update the reward if it's a non terminal step. the reward is 0 for all non terminal steps            
                                next_preds = self.frozen_model.predict(np.array([_s]))[0]                                        

                                maxval = 0
                                for total_idx in _avail:
                                    val = next_preds[total_idx]

                                    if val > maxval:
                                        maxval = val

                                #print('TEST TEST : ')
                                #print(maxval)

                                r = maxval*0.95 + r # gamma*Q(s', a)

                            b = self.training_model.predict(np.array([s])) #setting the gradient of all the non action values to 0, kinda hacky but works

                            r = r+ ir
                            b[0][idx] = r
                            y.append(b)       

                        y = np.array(y)           

                        if len(X) > 0:              
                            for idx in range(len(X)):   
                                #print('l:', y[idx].shape)                             
                                #y_test = np.array(y[idx]) 
                                X_train = np.array([X[idx]])
                                y_train = y[idx]
                                #print('YSHAPE: ',  y_train[0].shape)
                                #print('m:', y_test.shape)    
                                #y_test= y_test.reshape(150,1)  
                                #print('n:', y_test.shape) 
                                self.training_model.train_on_batch(X_train, y_train)

                    '''


                assert(ValidMove(selected, moves))
                random.seed(self.seed_list[self.seed_idx])


                self.seed_idx += 1
                self.game_state.ExecuteMove(i, selected)

                if not self.game_state.TilesRemaining():
                    break

            # Have we reached the end of round?
            if self.game_state.TilesRemaining():
                move_count+=1
                continue

            # It is the end of round
            self.game_state.ExecuteEndOfRound()
            if self.displayer is not None:
                self.displayer.EndRound(self.game_state)

            
            # Is it the end of the game? 
            for i in player_order:
                plr_state = self.game_state.players[i]
                completed_rows = plr_state.GetCompletedRows()

                if completed_rows > 0:
                    game_continuing = False
                    break

            if game_continuing:
                round_count+=1  ## round_count+=1 
                move_count=0
                self.game_state.SetupNewRound()

                player_order = []
                cnt_0 = 0
                cnt_1 = 0
                for i in range(self.game_state.first_player,len(self.players)):
                    player_order.append(i)

                for i in range(0, self.game_state.first_player):
                    player_order.append(i)

                for i in player_order:
                    gs_copy = copy.deepcopy(self.game_state)
                    try:
                        func_timeout(self.startRound_time_limit,self.players[i].StartRound,args=(gs_copy,))

                    except FunctionTimedOut:
                        '''
                        self.warnings[i] += 1
                        if self.displayer is not None:
                            self.displayer.TimeOutWarning(self,i)
                        self.warning_positions.append((i,round_count,-1))

                        if self.warnings[i] == self.warning_limit:
                            player_traces = self._EndGame(player_order,isTimeOut=True,id=i)
                            return player_traces
                        '''
                    except AttributeError:
                        pass
                                    
                random.seed(self.seed_list[self.seed_idx])
                self.seed_idx += 1

                if self.displayer is not None:
                    self.displayer.StartRound(self.game_state)



    def Run(self):
        print('OK GAME START!')
        self.displayer = None
        max_len = 100
        self.experience_replay = ER(max_len)
        self.most_len = 0
        self.learning_rate = 0.005
        self.general_moves = {}
        self.prev_0_point = 0
        self.prev_1_point = 0
        # C is the number of timesteps we update the frozen model
        C = 50

        '''
        json_file = open('model.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()        
        loaded_model = model_from_json(loaded_model_json)
        loaded_model.load_weights("model.h5")
        loaded_model.compile(loss='mse', optimizer = 'rmsprop', metrics=['accuracy'])
        loaded_model._make_predict_function()
        self.training_model = loaded_model   


        json_file = open('model.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()        
        loaded_model = model_from_json(loaded_model_json)
        loaded_model.load_weights("model.h5")
        loaded_model.compile(loss='mse', optimizer = 'rmsprop')
        loaded_model._make_predict_function()
        self.frozen_model = loaded_model   
        '''
        #self.base_state = np.zeros(7) #47 7 132 85 (1,85)

        training_model = Sequential()
        training_model.add(Dense(1500,  input_shape=(95, ), activation='relu')) #132 85 85 47 4747 94 30 1 125 78-30 
        training_model.add(Activation('relu'))
        training_model.add(Dense(1000))
        training_model.add(Activation('relu'))
        training_model.add(Dense(875))
        training_model.add(Activation('linear'))
        training_model.compile(loss='mse', optimizer = 'rmsprop', metrics=['accuracy'])
        self.training_model = training_model

        # Q^ or the frozen model
        frozen_model = Sequential()
        frozen_model.add(Dense(1500,  input_shape=(95, ), activation='relu')) #132 85 85 125
        frozen_model.add(Activation('relu'))
        frozen_model.add(Dense(1000))
        frozen_model.add(Activation('relu'))
        frozen_model.add(Dense(875))
        frozen_model.add(Activation('linear'))
        frozen_model.compile(loss='mse', optimizer = 'rmsprop')
        self.frozen_model = frozen_model        


        #ills = 0 #number of illegal moves
        discount = 0.97 #gamme for gamma*Q(s', a') in the loss f'n
        scores= deque(maxlen=100) #just a metric for checking scores

        self.epsilon = 1.0 #% of random moves
        self.eps = 0 #number of random moves played
        moves = 0 #number of non-random moves played

        max_episodes = 1000 #max games
        max_steps = 10  #max length of a game

        for episode in range(max_episodes):
            print('Episode: ', episode)
            training_count = 0
            #frozen model update
            if episode % C == 0:
                self.training_model.save_weights('weights.h5', overwrite=True)
                self.frozen_model.load_weights('weights.h5')
                self.frozen_model.compile(loss='mse', optimizer ='rmsprop')

            #play a game
            for timestep in range(max_steps):                
                print('train : ', timestep, '-th')
                self._run()
                training_count += 1
                #self.epsilon-= decremental_epsilon             

            if episode%10 == 0:     
                with open('generalized_moves.json', 'w') as fp:   # Save the mapping Move/Index to be used on developement
                    json.dump(self.general_moves, fp)

                model_json = self.training_model.to_json()
                with open("model.json", "w") as json_file:
                    json_file.write(model_json)

                graph = tf.get_default_graph()
                with graph.as_default():
                    self.training_model.save_weights("model.h5")

            print('episode ', episode, ' DONE!')


        with open('generalized_moves.json', 'w') as fp:   # Save the mapping Move/Index to be used on developement
            json.dump(self.general_moves, fp)

        model_json = self.training_model.to_json()
        with open("model.json", "w") as json_file:
            json_file.write(model_json)

        graph = tf.get_default_graph()
        with graph.as_default():
            self.training_model.save_weights("model.h5")


class ReplayRunner:
    def __init__(self,replay, displayer = None):
        self.replay = replay
                    
        self.seed = self.replay["seed"]
        random.seed(self.seed)
        self.seed_list = [random.randint(0,1e10) for _ in range(1000)] 
        self.seed_idx = 0

        self.player_num = self.replay["player_num"]
        self.players_namelist = replay["players_namelist"]
        self.warning_limit = replay["warning_limit"]
        self.warnings = [0]*self.player_num
        self.warning_positions = replay["warning_positions"]
        self.game_state = GameState(self.player_num)

        self.displayer = displayer
        if self.displayer is not None:
            self.displayer.InitDisplayer(self)
            
  
    def Run(self):
        player_order = []
        for i in range(self.game_state.first_player, self.player_num):
            player_order.append(i)

        for i in range(0, self.game_state.first_player):
            player_order.append(i)
        
        game_continuing = True
        for plr in self.game_state.players:
            plr.player_trace.StartRound()
            
        round_count = 0
        move_count = 0

        for i in player_order:
            if (i,round_count,-1) in self.warning_positions:
                self.warnings[i]+=1
                if self.displayer is not None:
                    self.displayer.TimeOutWarning(self,i)

                if self.warnings[i] == self.warning_limit:                        
                    self.game_state.players[i].score = -1
                    if self.displayer is not None:
                        self.displayer.EndGame(self.game_state)
                    return self.displayer

        random.seed(self.seed_list[self.seed_idx])
        self.seed_idx += 1

        if self.displayer is not None:
            self.displayer.StartRound(self.game_state)
        
        while game_continuing:
            for i in player_order:

                if (i,round_count,move_count) in self.warning_positions:
                    self.warnings[i]+=1
                    if self.displayer is not None:
                        self.displayer.TimeOutWarning(self,i)
                    
                    if self.warnings[i] == self.warning_limit:                        
                        self.game_state.players[i].score = -1
                        if self.displayer is not None:
                            self.displayer.EndGame(self.game_state)
                        return self.displayer

                plr_state = self.game_state.players[i]
                moves = plr_state.GetAvailableMoves(self.game_state)
                selected = self.replay[i][1].moves[round_count][move_count]
                
                
                assert(ValidMove(selected, moves))
                random.seed(self.seed_list[self.seed_idx])
                self.seed_idx += 1
                self.game_state.ExecuteMove(i, selected)

                if self.displayer is not None:
                    self.displayer.ExcuteMove(i,selected, self.game_state)
                    
                if not self.game_state.TilesRemaining():
                    break

            # Have we reached the end of round?
            if self.game_state.TilesRemaining():
                move_count+=1
                continue

            # It is the end of round
            self.game_state.ExecuteEndOfRound()
            if self.displayer is not None:
                self.displayer.EndRound(self.game_state)

            # Is it the end of the game? 
            for i in player_order:
                plr_state = self.game_state.players[i]
                completed_rows = plr_state.GetCompletedRows()

                if completed_rows > 0:
                    game_continuing = False
                    break

            # Set up the next round
            if game_continuing:
                round_count+=1
                move_count=0
                self.game_state.SetupNewRound()
                player_order = []
                for i in range(self.game_state.first_player,self.player_num):
                    player_order.append(i)

                for i in range(0, self.game_state.first_player):
                    player_order.append(i)        
                    
                for i in player_order:
                    if (i,round_count,-1) in self.warning_positions:
                        self.warnings[i]+=1
                        if self.displayer is not None:
                            self.displayer.TimeOutWarning(self,i)

                        if self.warnings[i] == self.warning_limit:                        
                            self.game_state.players[i].score = -1
                            if self.displayer is not None:
                                self.displayer.EndGame(self.game_state)
                            return self.displayer
                            
                random.seed(self.seed_list[self.seed_idx])
                self.seed_idx += 1

                if self.displayer is not None:
                    self.displayer.StartRound(self.game_state)                
                

        # Score player bonuses
        for i in player_order:
            self.game_state.players[i].EndOfGameScore()
    
        if self.displayer is not None:
            self.displayer.EndGame(self.game_state)
            
        # Return scores
        return self.displayer
      

class ER:
    def __init__(self, max_len=100):
        self.replay_0 = []
        self.replay_1 = []
        self.replay_long_0 = []
        self.replay_long_1 = []

        #self.max_len = 100
        #self.curr_game = []

    def store_0(self, state, done, immediate_reward, reward, whole_reward, next_state, avail, idx):
        #self.curr_game.append((state, immediate_reward, reward, next_state, avail, idx))        
        self.replay_0.append((state, done, immediate_reward, reward, whole_reward, next_state, avail, idx))
        self.replay_long_0.append((state, done, immediate_reward, reward, whole_reward, next_state, avail, idx))

    def store_1(self, state, done, immediate_reward, reward, whole_reward, next_state, avail, idx):
        #self.curr_game.append((state, immediate_reward, reward, next_state, avail, idx))        
        self.replay_1.append((state, done, immediate_reward, reward, whole_reward, next_state, avail, idx))
        self.replay_long_1.append((state, done, immediate_reward, reward, whole_reward, next_state, avail, idx))

        '''
        discount = 0.97
        if reward != 0:
            r_0 = 0
            i = 0
            for s, ir, r, _s, avail, idx in reversed(self.curr_game):
                # r_0 = r + discount*r_0
                self.replay.append((s, ir, r, _s, avail, idx))

            while len(self.replay) > self.max_len:
                self.replay.pop()
            self.curr_game = []
        '''
    def get_minibatch(self, flag, size=30):
        replay = self.replay_0        
        self.replay_0 = []
        if flag == 1:
            replay = self.replay_1
            self.replay_1 = []

        #print('param: ', size, 'replay size: ', len(replay))
        '''
        if len(replay) > size:
            print('param: ', size, 'replay size: ', len(replay))
            copied = copy.deepcopy(replay)
            random.shuffle(copied)
            return copied[:size]
        else:
        '''
        return replay

    def get_longbatch(self, flag, size=500):
        
        replay = self.replay_long_0
        self.replay_long_0 = []
        
        if flag == 1:
            replay = self.replay_long_1
            self.replay_long_1 = []


        #print('LONG:   param: ', size, 'replay size: ', len(replay))
        #if len(replay) > size:
        #    print('param: ', size, 'replay size: ', len(replay))
        #    copied = copy.deepcopy(replay)
        #    random.shuffle(copied)
        #    return copied[:size]
        #else:
        return replay


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

        #elif i == 1:
        grid_arr.append(B2N(ps.grid_state[1][0], 1, 0))
        grid_arr.append(B2N(ps.grid_state[1][1], 1, 1))
        grid_arr.append(B2N(ps.grid_state[1][2], 1, 2))
        grid_arr.append(B2N(ps.grid_state[1][3], 1, 3))
        grid_arr.append(B2N(ps.grid_state[1][4], 1, 4))  
        #elif i == 2:
        grid_arr.append(B2N(ps.grid_state[2][0], 2, 0))
        grid_arr.append(B2N(ps.grid_state[2][1], 2, 1))
        grid_arr.append(B2N(ps.grid_state[2][2], 2, 2))
        grid_arr.append(B2N(ps.grid_state[2][3], 2, 3))
        grid_arr.append(B2N(ps.grid_state[2][4], 2, 4))  
        #elif i == 3:    
        grid_arr.append(B2N(ps.grid_state[3][0], 3, 0))
        grid_arr.append(B2N(ps.grid_state[3][1], 3, 1))
        grid_arr.append(B2N(ps.grid_state[3][2], 3, 2))
        grid_arr.append(B2N(ps.grid_state[3][3], 3, 3))
        grid_arr.append(B2N(ps.grid_state[3][4], 3, 4))  
        #elif i == 4:
        grid_arr.append(B2N(ps.grid_state[4][0], 4, 0))
        grid_arr.append(B2N(ps.grid_state[4][1], 4, 1))
        grid_arr.append(B2N(ps.grid_state[4][2], 4, 2))
        grid_arr.append(B2N(ps.grid_state[4][3], 4, 3))
        grid_arr.append(B2N(ps.grid_state[4][4], 4, 4))  

        pattern_line_arr.extend(grid_arr)

        return pattern_line_arr
