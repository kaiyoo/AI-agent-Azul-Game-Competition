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
import random
import sys
sys.path.append('players/Azul project group 7/')
from featureExtractor import *

class myPlayer(AdvancePlayer):
    def __init__(self, _id):
        super().__init__(_id)

    def SelectMove(self, moves, game_state):
        # Select move that involves placing the most number of tiles
        # in a pattern line. Tie break on number placed in floor line.
        featurizer = FeatureExtractor()
        for move in moves:
            # featurize state action pair
            featurizer.getFeatures(game_state, move, self.id)
            break
        
        options = input()
        
        return random.choice(moves)
