
#- args player_list, list of players
#- args seed, random seed used
#- args time_limit, time limit for each step, None for inf time
#- args warning_limit, timeout warnings 
#- args displayer, TextGameDisplayer, GUIDisplayer or None
#- args players_namelist, name to display
#- return replay, a dict

from model import *

from displayer import *
from func_timeout import func_timeout, FunctionTimedOut
import time

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
        self.seed_list = [random.randint(0,1e10) for _ in range(1000)]
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

    def Run(self):
        player_order = []
        for i in range(self.game_state.first_player, len(self.players)):
            player_order.append(i)

        for i in range(0, self.game_state.first_player):
            player_order.append(i)
 
        game_continuing = True
        round_count = 0
        move_count = 0
        
        for plr in self.game_state.players:
            plr.player_trace.StartRound()

        for i in player_order:
            gs_copy = copy.deepcopy(self.game_state)
            try:
                func_timeout(self.startRound_time_limit,self.players[i].StartRound,args=(gs_copy,))
            except FunctionTimedOut:
                self.warnings[i] += 1
                if self.displayer is not None:
                    self.displayer.TimeOutWarning(self,i)
                self.warning_positions.append((i,round_count,-1))

                if self.warnings[i] == self.warning_limit:
                    player_traces = self._EndGame(player_order,isTimeOut=True,id=i)
                    return player_traces

            except AttributeError:
                pass
                    
        random.seed(self.seed_list[self.seed_idx])
        self.seed_idx += 1

        if self.displayer is not None:
            self.displayer.StartRound(self.game_state)

        while game_continuing:
            for i in player_order:
                plr_state = self.game_state.players[i]
                moves = plr_state.GetAvailableMoves(self.game_state)

                gs_copy = copy.deepcopy(self.game_state)
                moves_copy = copy.deepcopy(moves)
                
                try:
                    selected = func_timeout(self.time_limit,self.players[i].SelectMove,args=(moves_copy, gs_copy))
                    
                except FunctionTimedOut:
                    self.warnings[i] += 1
                    if self.displayer is not None:
                        self.displayer.TimeOutWarning(self,i)
                    self.warning_positions.append((i,round_count,move_count))

                    if self.warnings[i] == self.warning_limit:
                        player_traces = self._EndGame(player_order,isTimeOut=True,id=i)
                        return player_traces
                    
                    selected = random.choice(moves)

                    
                    
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
                for i in range(self.game_state.first_player,len(self.players)):
                    player_order.append(i)

                for i in range(0, self.game_state.first_player):
                    player_order.append(i)

                for i in player_order:
                    gs_copy = copy.deepcopy(self.game_state)
                    try:
                        func_timeout(self.startRound_time_limit,self.players[i].StartRound,args=(gs_copy,))
                    except FunctionTimedOut:
                        self.warnings[i] += 1
                        if self.displayer is not None:
                            self.displayer.TimeOutWarning(self,i)
                        self.warning_positions.append((i,round_count,-1))

                        if self.warnings[i] == self.warning_limit:
                            player_traces = self._EndGame(player_order,isTimeOut=True,id=i)
                            return player_traces
                    except AttributeError:
                        pass
                                    
                random.seed(self.seed_list[self.seed_idx])
                self.seed_idx += 1

                if self.displayer is not None:
                    self.displayer.StartRound(self.game_state)

        # Score player bonuses
        player_traces = self._EndGame(player_order,isTimeOut=False)
            
        # Return scores
        return player_traces
   
 
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
   