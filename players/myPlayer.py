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

class myPlayer(AdvancePlayer):
    def __init__(self, _id):
        super().__init__(_id)

    def SelectMove(self, moves, game_state):
        # Select move that involves placing the most number of tiles
        # in a pattern line. Tie break on number placed in floor line.
        most_to_line = -1
        corr_to_floor = 0

        best_move = None

        for mid,fid,tgrab in moves:
            if most_to_line == -1:
                best_move = (mid,fid,tgrab)
                most_to_line = tgrab.num_to_pattern_line
                corr_to_floor = tgrab.num_to_floor_line
                continue

            if tgrab.num_to_pattern_line > most_to_line:
                best_move = (mid,fid,tgrab)
                most_to_line = tgrab.num_to_pattern_line
                corr_to_floor = tgrab.num_to_floor_line
            elif tgrab.num_to_pattern_line == most_to_line and \
                tgrab.num_to_pattern_line < corr_to_floor:
                best_move = (mid,fid,tgrab)
                most_to_line = tgrab.num_to_pattern_line
                corr_to_floor = tgrab.num_to_floor_line

        return best_move
