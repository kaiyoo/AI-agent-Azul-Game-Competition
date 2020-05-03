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
        
        move = None
        while True:
            move = None
            print("> Select Option ('back' returns to this menu): ")
            print("(1) See available moves")
            print("(2) Take tiles from a factory display")
            print("(3) Take tiles from the centre")

            option = input()

            if option == "back":
                continue

            if not option.isdigit():
                print("> Option not recognised. Repeating request.")
                continue

            ioption = int(option)

            cont = False
            if ioption == 1:
                # Print Moves 
                for mo in moves:
                    print(MoveToString(self.id, mo))
                    print("\n")
                continue

            elif ioption == 2:
                # Ask for factory ID and tile type
                cont = False
                while True:
                    cont = False
                    print("> Factory ID?")
                    fid = input()

                    if fid == "back":
                        cont = True
                        break

                    if not fid.isdigit():
                        print("> Invalid input. Repeating request")
                        continue

                    ifid = int(fid)

                    if ifid < 1 or ifid > len(game_state.factories)+1:
                        print("> Invalid factory id. Repeating request.")
                        continue

                    td = game_state.factories[ifid-1]
                    if td.total == 0:
                        print("> No tiles available in this display")
                        cont = True
                        break

                    tiles_avail = ""
                    for tile in Tile:
                        if td.tiles[tile] > 0:
                            tiles_avail+="{}/".format(TileToShortString(tile))

                    tile_type = Tile.BLUE
                    while True:
                        print("> Tile type ({})?".format(tiles_avail))

                        tt = input()

                        if tt == "back":
                            cont = True
                            break
                           
                        if tt == "R":
                            tile_type = Tile.RED
                        elif tt == "B":
                            tile_type = Tile.BLUE
                        elif tt == "W":
                            tile_type = Tile.WHITE
                        elif tt == "Y":
                            tile_type = Tile.YELLOW
                        elif tt == "K":
                            tile_type = Tile.BLACK
                        else:
                            print("> Invalid tile type. Repeating request")
                            continue

                        if td.tiles[tile_type] == 0:
                            print("> No tiles of that type available")
                            continue

                        break

                    if cont:
                        break

                    number = td.tiles[tile_type]

                    dest = 0
                    # Get destination (only display available destinations)
                    while True:
                        print("> Destination?")
                        dests = " (0) Floor line\n"

                        doptions = [0]

                        for i in range(plr_state.GRID_SIZE):
                            # Does the corresponding grid position already
                            # have a tile on it?
                            col = int(plr_state.grid_scheme[i][tile_type])
                            if plr_state.grid_state[i][col] == 1:
                                # This tile type cannot be placed in this
                                # pattern line
                                continue

                            if (plr_state.lines_tile[i] == -1 or  \
                                plr_state.lines_tile[i] == tile_type) and \
                                plr_state.lines_number[i] < i+1:
                                dests += " ({}) Pattern line {}\n".format(
                                    i+1, i+1)
                                doptions.append(i+1)

                        print(dests) 

                        rdest = input()
                        if rdest == "back":
                            cont = True
                            break

                        if not rdest.isdigit():
                            print("> Invalid input. Repeating request")
                            continue

                        idest = int(rdest)
                        if not (idest in doptions):
                            print("> Invalid input. Repeating request")
                            continue
                            
                        dest = idest
                        break

                    if cont:
                        break

                    # We have all the information we need to define the move
                    tgrab = TileGrab()
                    tgrab.tile_type = tile_type
                    tgrab.number = number

                    if dest == 0:
                        tgrab.num_to_floor_line = number
                    else:
                        # Compute number of tiles that could be placed
                        # in the selected pattern line, rest goes to floor
                        toline = min(dest - plr_state.lines_number[dest-1],
                            number)
                        tgrab.pattern_line_dest = dest - 1
                        tgrab.num_to_pattern_line = toline
                        tgrab.num_to_floor_line = number - toline
                    
                    move = (Move.TAKE_FROM_FACTORY, ifid-1, tgrab)  
                    break   

                if cont:
                    continue
                
            elif ioption == 3:
                cont = False
                # We are taking tiles from the centre pool
                td = game_state.centre_pool
                if td.total == 0:
                    print("> No tiles available in the centre")
                    cont = True
                    break

                tiles_avail = ""
                for tile in Tile:
                    if td.tiles[tile] > 0:
                        tiles_avail+="{}/".format(TileToShortString(tile))

                tile_type = Tile.BLUE
                while True:
                    print("> Tile type ({})?".format(tiles_avail))

                    tt = input()

                    if tt == "back":
                        cont = True
                        break
                           
                    if tt == "R":
                        tile_type = Tile.RED
                    elif tt == "B":
                        tile_type = Tile.BLUE
                    elif tt == "W":
                        tile_type = Tile.WHITE
                    elif tt == "Y":
                        tile_type = Tile.YELLOW
                    elif tt == "K":
                        tile_type = Tile.BLACK
                    else:
                        print("> Invalid tile type. Repeating request")
                        continue

                    if td.tiles[tile_type] == 0:
                        print("> No tiles of that type available")
                        continue
                    break

                if cont:
                    continue

                number = td.tiles[tile_type]

                dest = 0
                # Get destination (only display available destinations)
                while True:
                    print("> Destination?")
                    dests = " (0) Floor line\n"

                    doptions = [0]

                    for i in range(plr_state.GRID_SIZE):
                        # Does the corresponding grid position already
                        # have a tile on it?
                        col = int(plr_state.grid_scheme[i][tile_type])
                        if plr_state.grid_state[i][col] == 1:
                            # This tile type cannot be placed in this
                            # pattern line
                            continue

                        if (plr_state.lines_tile[i] == -1 or 
                            plr_state.lines_tile[i] == tile_type) and \
                            plr_state.lines_number[i] < i+1:
                            dests += " ({}) Pattern line {}\n".format(
                                i+1, i+1)
                            doptions.append(i+1)

                    print(dests) 

                    rdest = input()
                    if rdest == "back":
                        cont = True
                        break

                    if not rdest.isdigit():
                        print("> Invalid input. Repeating request")
                        continue

                    idest = int(rdest)
                    if not (idest in doptions):
                        print("> Invalid input. Repeating request")
                        continue
                            
                    dest = idest
                    break

                if cont:
                    continue

                # We have all the information we need to define the move
                tgrab = TileGrab()
                tgrab.tile_type = tile_type
                tgrab.number = number

                if dest == 0:
                    tgrab.num_to_floor_line = number
                else:
                    # Compute number of tiles that could be placed
                    # in the selected pattern line, rest goes to floor
                    toline = min(dest - plr_state.lines_number[dest-1],
                        number)
                    tgrab.pattern_line_dest = dest - 1
                    tgrab.num_to_pattern_line = toline
                    tgrab.num_to_floor_line = number - toline
                    
                move = (Move.TAKE_FROM_CENTRE, -1, tgrab)
                break     

            else:
                cont = True
                print("Option not recognised. Repeating request.")

            if not cont:
                break

        # Does the move exist in the available set of moves?
        found = False
        for m in moves:
            if m[0]==move[0] and m[1]==move[1] and SameTG(m[2],move[2]):
                found = True
                break

        assert found

        return move
