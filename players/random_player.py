
from advance_model import *
from utils import *

import time
import random

class myPlayer(AdvancePlayer):
    def __init__(self,_id):
        super().__init__(_id)
    
    def SelectMove(self,moves,game_state):
        return random.choice(moves)
