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
from enum import IntEnum

# There are 5 types of tiles in the game, each differentiated by colour.
class Tile(IntEnum):
    BLUE = 0
    YELLOW = 1
    RED = 2
    BLACK = 3
    WHITE = 4

# There are 2 types of moves a player can perform in the game
class Move(IntEnum):
    TAKE_FROM_FACTORY = 1
    TAKE_FROM_CENTRE = 2

# Bundle together a player's activity in the game for use in
# updating a policy
class PlayerTrace:
    def __init__(self, pid):
        # Player ID
        self.id = pid

        # Round by round move history
        self.moves = []
    
        # Round by round scores
        self.round_scores = []

        # Bonus scores
        self.bonuses = 0

    def StartRound(self):
        self.moves.append(list())
        self.round_scores.append(0)
        

# Structure recording the number, type, and destination of tiles 
# collected by a player. Note that the sum of 'num_to_pattern_line'
# and 'num_to_floor_line' must equal 'number'.
class TileGrab:
    def __init__(self):
        self.tile_type = -1
        self.number = 0
        self.pattern_line_dest = -1
        self.num_to_pattern_line = 0
        self.num_to_floor_line = 0 

def SameTG(tg1, tg2):
    if tg1.tile_type != tg2.tile_type:
        return False

    if tg1.number != tg2.number:
        return False

    if tg1.pattern_line_dest != tg2.pattern_line_dest:
        return False

    if tg1.num_to_pattern_line != tg2.num_to_pattern_line:
        return False

    if tg1.num_to_floor_line != tg2.num_to_floor_line:
        return False

    return True

def ValidMove(c, moves):
    for m in moves:
        if c[0] == m[0] and c[1] == m[1] and SameTG(c[2],m[2]):
            return True
    return False

def TileToString(tile):
    if tile == Tile.RED:
        return "red (R)"
    elif tile == Tile.BLUE:
        return "blue (B)"
    elif tile == Tile.WHITE:
        return "white (W)"
    elif tile == Tile.BLACK:
        return "black (K)"
    elif tile == Tile.YELLOW:
        return "yellow (Y)"
    else:
        return "unknown (U)"

def TileToShortString(tile):
    if tile == Tile.RED:
        return "R"
    elif tile == Tile.BLUE:
        return "B"
    elif tile == Tile.WHITE:
        return "W"
    elif tile == Tile.BLACK:
        return "K"
    elif tile == Tile.YELLOW:
        return "Y"
    else:
        return "U"

def B2S(binary):
    if binary == 0:
        return "_"
    else:
        return "x"

def MoveToString(player_id, move):
    tg = move[2]
    
    if move[0] == Move.TAKE_FROM_FACTORY:
        desc1 = "Player {} takes {} {} tiles from factory {}".format(
            player_id, tg.number, TileToString(tg.tile_type), move[1]+1)

        if tg.num_to_pattern_line > 0:
            desc1 += "\n   {} {} placed in pattern line {}".format(
                tg.num_to_pattern_line, TileToShortString(tg.tile_type),
                tg.pattern_line_dest+1)

        if tg.num_to_floor_line > 0:
            desc1 += "\n   {} {} placed in floor line".format(
                tg.num_to_floor_line,  TileToShortString(tg.tile_type))
        return desc1

    elif move[0] == Move.TAKE_FROM_CENTRE:
        desc1 = "Player {} takes {} {} tiles from centre".format(
            player_id, tg.number, TileToString(tg.tile_type))

        if tg.num_to_pattern_line > 0:
            desc1 += "\n   {} {} placed in pattern line {}".format(
                tg.num_to_pattern_line, TileToShortString(tg.tile_type),
                tg.pattern_line_dest+1)

        if tg.num_to_floor_line > 0:
            desc1 += "\n   {} {} placed in floor line".format(
                tg.num_to_floor_line,  TileToShortString(tg.tile_type))
        return desc1
           
    return "Unknown Move"   


def PlayerToString(player_id, ps):
    desc = "Player {} score {}\n".format(player_id, ps.score)

    # Add pattern lines states to description
    for i in range(ps.GRID_SIZE):
        filled = ""
        if ps.lines_tile[i] != -1:
            tt = ps.lines_tile[i]
            ts = TileToShortString(tt)
            num = ps.lines_number[i]
            filled = ""
            for j in range(num):
                filled += "{} ".format(ts)
            for j in range(num, i+1):
                filled += "_ "

            for j in range(i+1, 5):
                filled += "  "

        else:
            assert ps.lines_number[i] == 0
            for j in range(i+1):
                filled += "_ "
            for j in range(i+1, 5):
                filled += "  "

        # Add corresponding grid line
        if i == 0:
            filled += " {}/B {}/Y {}/R {}/K {}/W\n".format(
                B2S(ps.grid_state[0][0]), B2S(ps.grid_state[0][1]),
                B2S(ps.grid_state[0][2]), B2S(ps.grid_state[0][3]),
                B2S(ps.grid_state[0][4]))
        elif i == 1:
            filled += " {}/W {}/B {}/Y {}/R {}/K\n".format(
                B2S(ps.grid_state[1][0]), B2S(ps.grid_state[1][1]),
                B2S(ps.grid_state[1][2]), B2S(ps.grid_state[1][3]),
                B2S(ps.grid_state[1][4]))
        elif i == 2:
            filled += " {}/K {}/W {}/B {}/Y {}/R\n".format(
                B2S(ps.grid_state[2][0]), B2S(ps.grid_state[2][1]),
                B2S(ps.grid_state[2][2]), B2S(ps.grid_state[2][3]),
                B2S(ps.grid_state[2][4]))
        elif i == 3:
            filled += " {}/R {}/K {}/W {}/B {}/Y\n".format(
                B2S(ps.grid_state[3][0]), B2S(ps.grid_state[3][1]),
                B2S(ps.grid_state[3][2]), B2S(ps.grid_state[3][3]),
                B2S(ps.grid_state[3][4]))
        elif i == 4:
            filled += " {}/Y {}/R {}/K {}/W {}/B\n".format(
                B2S(ps.grid_state[4][0]), B2S(ps.grid_state[4][1]),
                B2S(ps.grid_state[4][2]), B2S(ps.grid_state[4][3]),
                B2S(ps.grid_state[4][4]))

        desc += "    Line {} {}\n".format(i+1, filled)
    desc += "\n"

    # Add floor state to description
    floor = "\nFloor line "
    for i in ps.floor:
        if i == 1:
            floor += "x "
        else:
            floor += "_ " 
    desc += floor
    desc += "\n\n"

    return desc

def TileDisplayToString(td):
    if td.total == 0:
        return "No Tiles"

    res = ""
    for tile in Tile:
        if td.tiles[tile] > 0:
            res += "{}x{} ".format(td.tiles[tile], TileToShortString(tile))

    return res    


def BoardToString(game_state):
    # return description of centre pool and factory tiles
    desc = ""
    i = 1
    for fd in game_state.factories:
        contents = TileDisplayToString(fd)
        desc += "Factory {} has {}\n".format(i, contents)
        i += 1

    desc += "Centre has {}".format(
        TileDisplayToString(game_state.centre_pool)
    )

    if game_state.first_player_taken:
        desc += "\n"
    else:
        desc += " + first player token (-1)\n"
         
    return desc
