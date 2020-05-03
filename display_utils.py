import os
import utils
from tkinter import *
# from PIL import ImageTk,Image

class BoardTile:
    def __init__(self,x,y,index):
        self.empty = True
        self.x = x
        self.y = y
        self.content = 7
        self.index = index

class BoardRow:
    def __init__(self,index):
        self.tiles = []
        if index == 0:
            self.tiles.append(BoardTile(154,3,0))
        elif index == 1:
            self.tiles.append(BoardTile(154,40,0))
            self.tiles.append(BoardTile(116,40,1))
        elif index == 2:
            self.tiles.append(BoardTile(154,78,0))
            self.tiles.append(BoardTile(116,78,1))
            self.tiles.append(BoardTile(78,78,2))
        elif index == 3:
            self.tiles.append(BoardTile(154,116,0))
            self.tiles.append(BoardTile(116,116,1))
            self.tiles.append(BoardTile(78,116,2))
            self.tiles.append(BoardTile(40,116,3))
        elif index == 4:
            self.tiles.append(BoardTile(154,155,0))
            self.tiles.append(BoardTile(116,155,1))
            self.tiles.append(BoardTile(78,155,2))
            self.tiles.append(BoardTile(40,155,3))
            self.tiles.append(BoardTile(2,155,4))
        elif index == 5:
            self.tiles.append(BoardTile(3,220,0))
            self.tiles.append(BoardTile(44,220,0))
            self.tiles.append(BoardTile(85,220,0))
            self.tiles.append(BoardTile(126,220,0))
            self.tiles.append(BoardTile(167,220,0))
            self.tiles.append(BoardTile(208,220,0))
            self.tiles.append(BoardTile(249,220,0))
        else:
            for x in range(5):
                self.tiles.append(BoardTile(211+38*x,38*(index-6)+3,x))
        


class PlayerBoard:
    def __init__(self, player_id, canvas, label):
        # Player ID
        self.player_id = player_id
        self.player_name = ""
        self.display_board = canvas 
        self.playing_board = []
        self.scoring_board = []
        self.naming = label
        
        for x in range(6):
            self.playing_board.append(BoardRow(x))
        
        for x in range(6,11):
            self.scoring_board.append(BoardRow(x))

class BoardFactory:
    def __init__(self,factory_id):
        self.id = factory_id
        self.factory_displayer = None
        self.tile_displayer = []
        self.tile_num = []
        self.tile_num_displayer = []

# root = Tk()
# root.title("AZUL assignment ------ COMP90054 AI Planning for Autononmy")
# root.iconbitmap("resources/azul_bpj_icon.ico")
# root.geometry("1280x800")
# mylabel = Label(root, text="AZUL")

# red_tile_img = PhotoImage(file="resources/red_tile_mini.png")

# player_board_1 = Canvas(root, width=405, height=265)
# player_board_1.grid(row=2, column=1)
# player_board_1_img = PhotoImage(file="resources/player_board_mini.png")
# player_board_1.create_image(0,0, anchor=NW, image=player_board_1_img) 


# player_board_1.create_image(211,3, anchor=NW, image=red_tile_img) 
# player_board_1.create_image(249,3, anchor=NW, image=red_tile_img) 
# player_board_1.create_image(211,79, anchor=NW, image=red_tile_img) 
# player_board_1.create_image(211,79, anchor=NW, image=red_tile_img) 
# player_board_1.create_image(211,79, anchor=NW, image=red_tile_img) 

# canvas = Canvas(root, width = 1024, height = 768)
# canvas.grid(row=0,column=1)      
# img = PhotoImage(file="resources/game_original.png")      
# canvas.create_image(0,0, anchor=NW, image=img)  
# # canvas.create_rectangle(50, 20, 150, 80, fill="#476042")
# f= Frame(root, padx=396, pady=112,bg="grey",borderwidth=4,relief=SUNKEN)#400/116
# mylabel = Label(f, text="AZUL")
# mylabel.pack()
# canvas.create_window(29, 44, anchor=NW, window=f)


# listbox=Listbox(root,name="moves:", height=10, width=30, selectmode="single", borderwidth=4)
# listbox.grid(row=0,column=2,sticky=N+E)
# listbox.insert(END,"move 1")
# listbox.insert(END,'move 2')
# # # pack the window as the minimum window
# move_index=0
# def onselect(evt):
#     # Note here that Tkinter passes an event object to onselect()
#     global move_index
#     w = evt.widget
#     index = int(w.curselection()[0])
#     value = w.get(index)
#     move_index=index+1
#     status = Label(root, text = "Move "+ str(move_index) +" our of "+ str(listbox.size()) +"; from round 5 out of 6   ", bd=1, relief=SUNKEN, anchor=E)
#     status.grid(row=4,column=0,columnspan=3,sticky=W+E)
#     #print 'You selected item %d: "%s"' % (index, value)

# listbox.bind('<<ListboxSelect>>',onselect)
# e = Entry(root,width=50,borderwidth=10)
# e.grid(row=2,column=1)


# def myClick():
#     hello = e.get() + "Hello"
#     myLabel = Label(root, text=hello)
#     myLabel.grid(row=3,column=3)

# # grid() put the label into a grid
# mylabel1 = Label(root, text="AZUL1")
# mylabel1.grid(row=0,column=0)
# mylabel2 = Label(root, text="AZUL2")
# mylabel2.grid(row=1,column=0)

# # myButton = Button(root, text="clickme",state=DISABLED,padx=50,pady=50)
# # myButton.grid(row=1,column=1)
# # fg=font color, bg=background color
# # myButton = Button(root, text="clickme",padx=50,pady=50,command=myClick,fg="blue",bg="red")
# myButton = Button(root, text="clickme",command=lambda: myClick(),fg="blue",bg="red")
# myButton.grid(row=1,column=1,columnspan=3,padx=10,pady=10)#pady will provide space between current item and below item




# root.mainloop()
