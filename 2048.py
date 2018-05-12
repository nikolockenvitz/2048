#!/usr/bin/python3

# TODO: set grid, get scale in __init__ (fonts), rename and explain resize2

FILENAME_HIGHSCORE = "2048highscore.txt"

KEYS_UP    = ["w", "Up"]
KEYS_RIGHT = ["d", "Right"]
KEYS_DOWN  = ["s", "Down"]
KEYS_LEFT  = ["a", "Left"]

BG             = "#776e65"
BG_END_OF_GAME = "#edc22e"
FONT_FIELD     = ["Consolas", "18", "bold"]
FONT_TEXT      = ["Consolas", "16"]
FONT_2048      = ["Consolas", "64"]
FG_2048        = "#50d1f5"

DEFAULT_DESIGN = [[ 0, "#000000", "#aa9898"], #       -
                  [ 1, "#776e65", "#eee4da"], #       2
                  [ 2, "#776e65", "#ede0c8"], #       4
                  [ 3, "#f9f6f2", "#f2b179"], #       8
                  [ 4, "#f9f6f2", "#f59563"], #      16
                  [ 5, "#f9f6f2", "#f67c5f"], #      32
                  [ 6, "#f9f6f2", "#f65e3b"], #      64
                  [ 7, "#f9f6f2", "#edcf72"], #     128
                  [ 8, "#f9f6f2", "#edcc61"], #     256
                  [ 9, "#f9f6f2", "#edc850"], #     512
                  [10, "#f9f6f2", "#edc53f"], #   1.024
                  [11, "#f9f6f2", "#edc22e"], #   2.048
                  [12, "#ffffff", "#50d1f5"], #   4.096
                  [13, "#ffffff", "#7070ee"], #   8.192
                  [14, "#ffffff", "#4040ee"], #  16.384
                  [15, "#ffffff", "#484e4d"], #  32.768
                  [16, "#ffffff", "#403635"], #  65.536
                  [17, "#ffffff", "#201818"]] # 131.072

DEFAULT_WIDTH_WINDOW = 740

GRID_COLUMNS = 37
GRID_ROWS    = 25
GRID_UNIT    = 20

from tkinter import *
from tkinter import messagebox
from random import randint
from math import log2
import os

class UI:
    def __init__(self):
        # set keys
        self.keys = [KEYS_UP, KEYS_RIGHT,
                     KEYS_DOWN, KEYS_LEFT]

        # set colours for tiles: [ [exponent, fg, bg], ... ]
        self.colours     = DEFAULT_DESIGN

        # colours and fonts
        self.bg          = BG
        self.bgEndOfGame = BG_END_OF_GAME
        self.fontFields  = FONT_FIELD
        self.fontText    = FONT_TEXT
        self.font2048    = FONT_2048
        self.fg2048      = FG_2048

        # create a game instance
        self.game = Game()

        # create window
        self.root = Tk()
        self.root.config(bg=self.bg)
        self.root.title("2048")

        # init grid
        self.unit   = GRID_UNIT
        self.width  = GRID_COLUMNS * self.unit
        self.height = GRID_ROWS    * self.unit

        # get coefficient for fonts (dependency between font size and grid unit)
        self.coefficientFontFields = int(self.fontFields[1]) / self.unit
        self.coefficientFontText   = int(self.fontText[1])   / self.unit
        self.coefficientFont2048   = int(self.font2048[1])   / self.unit

        # initialize window
        self.setWindowSize()
        self.createUIElements()
        self.show()

        # bindings
        self.root.bind("<Enter>",     self.adjustWindowToCurrentWidth)
        self.root.bind("<Configure>", self.adjustWindowToCurrentState)
        self.root.bind("<Key>",       self.keyPressed)

        # call function to close gracefully
        self.root.protocol("WM_DELETE_WINDOW", self.rootDestroy)

        self.root.mainloop()

    def adjustWindowToCurrentState(self, event=None):
        # zoomed to normal
        if((self.unit == self.root.winfo_screenheight()//GRID_ROWS-2 or
            self.unit == self.root.winfo_screenwidth()//GRID_COLUMNS) and
           self.root.state() == "normal"):
            width = DEFAULT_WIDTH_WINDOW
            self.setWindowSize(width)
        # normal to zoomed
        if(not (self.unit == self.root.winfo_screenheight()//GRID_ROWS-2 or
                self.unit == self.root.winfo_screenwidth()//GRID_COLUMNS) and
           self.root.state() == "zoomed"):
            width = self.root.winfo_screenwidth()
            self.setWindowSize(width)

    def adjustWindowToCurrentWidth(self, event=None):
        # adjusts content and window size
        width = self.root.winfo_width()
        self.setWindowSize(width)

    def setWindowSize(self, width=DEFAULT_WIDTH_WINDOW):
        self.unit = min(max(5, width // GRID_COLUMNS),
                        self.root.winfo_screenheight()//GRID_ROWS-2,
                        self.root.winfo_screenwidth()//GRID_COLUMNS)
        width  = GRID_COLUMNS * self.unit
        height = GRID_ROWS    * self.unit

        if(self.unit == self.root.winfo_screenheight()//GRID_ROWS-2 or
           self.unit == self.root.winfo_screenwidth()//GRID_COLUMNS):
            # max value -> full screen / zoomed
            self.root.state("zoomed")
        else:
            self.root.state("normal")
        
        size = str(width) + "x" + str(height)
        self.root.geometry(size)
        if(width != self.width or height != self.height):
            self.width  = width
            self.height = height
            self.hideUIElements()
            self.showUIElements()

    def confirmAction(self, msgboxHeading, msgboxText):
        if(not self.game.isFinished()):
            # game is not finished yet
            answer = messagebox.askyesno(msgboxHeading,
                                         msgboxText)
            return answer

        # return True per default when game is finished
        return True

    def rootDestroy(self):
        if(self.confirmAction("Quit?","Do you really want to quit?")):
            self.game.writeHighScore()
            self.root.destroy()

    def newGame(self, event=None):
        if(self.confirmAction("New Game?",
                              "Do you really want to start a new game?")):
            self.game.writeHighScore()
            self.game = Game()
            self.show()

    def labelField(self):
        return Label(self.root,
                     text   = "",
                     anchor = CENTER,
                     font   = self.fontFields)

    def labelText(self, text=""):
        return Label(self.root,
                     text = text,
                     bg   = self.bg,
                     font = self.fontText,
                     fg   = "#ffffff")

    def updateFontSize(self):
        self.fontFields[1] = int(self.coefficientFontFields * self.unit)
        self.fontText[1]   = int(self.coefficientFontText   * self.unit)
        self.font2048[1]   = int(self.coefficientFont2048   * self.unit)
        
        for label in self.listLabels:
            label.config(font=self.fontText)

        self.label2048.config(font=self.font2048)
        
        for fields in self.field:
            for field in fields:
                field.config(font=self.fontFields)

    def showUIElements(self):
        for i in range(4):
            self.listLabels[i].place(x =      26*self.unit,
                                     y = (6*i+1)*self.unit,
                                     width  =  9*self.unit,
                                     height =  5*self.unit)
                
        for y in range(4):
            for x in range(4):
                self.field[y][x].place(x= 6*self.unit*x+self.unit,
                                       y= 6*self.unit*y+self.unit,
                                       width  = 5*self.unit,
                                       height = 5*self.unit)

        self.updateFontSize()
        self.show()

    def hideUIElements(self):
        for label in self.listLabels:
            label.place_forget()

        for fields in self.field:
            for field in fields:
                field.place_forget()

    def createUIElements(self):
        self.labelScore = self.labelText()
        self.labelHighScore = self.labelText()
        
        self.label2048 = Label(self.root,
                               text = "2048",
                               bg   = self.bg,
                               font = self.font2048,
                               fg   = self.fg2048)

        self.labelNewGame = self.labelText("New Game")
        self.labelNewGame.config(relief=RIDGE)
        self.labelNewGame.bind("<Button-1>", self.newGame)

        self.listLabels = [self.labelScore,
                           self.labelHighScore,
                           self.label2048,
                           self.labelNewGame]
        
        self.field00 = self.labelField()
        self.field01 = self.labelField()
        self.field02 = self.labelField()
        self.field03 = self.labelField()
        
        self.field10 = self.labelField()
        self.field11 = self.labelField()
        self.field12 = self.labelField()
        self.field13 = self.labelField()

        self.field20 = self.labelField()
        self.field21 = self.labelField()
        self.field22 = self.labelField()
        self.field23 = self.labelField()

        self.field30 = self.labelField()
        self.field31 = self.labelField()
        self.field32 = self.labelField()
        self.field33 = self.labelField()

        self.field = [[self.field00, self.field01, self.field02, self.field03],
                      [self.field10, self.field11, self.field12, self.field13],
                      [self.field20, self.field21, self.field22, self.field23],
                      [self.field30, self.field31, self.field32, self.field33]]#
        
        self.showUIElements()

    def keyPressed(self, event):
        for direction in range(4):
            if(event.keysym in self.keys[direction]):
                self.game.move(direction)
                self.show()
                return

        if(event.keysym=="plus"): self.setWindowSize(self.width+GRID_COLUMNS)
        if(event.keysym=="minus"): self.setWindowSize(self.width-GRID_COLUMNS)
        
        # minimize window when any other key is pressed
        #self.root.iconify()

    def getColours(self, number):
        # return [exponent, fg, bg] for number
        if(number <= 0): number=1
        ix = int(log2(number))
        return self.colours[ix]

    def show(self):
        for y in range(4):
            for x in range(4):
                currentNumber = self.game.field[y][x]
                colours       = self.getColours(currentNumber)
                self.field[y][x].config(fg=colours[1], bg=colours[2])
                if(currentNumber):
                    self.field[y][x]["text"] = currentNumber
                else:
                    self.field[y][x]["text"] = ""

        self.labelScore["text"]     =     "Score:\n" + str(self.game.score)
        self.labelHighScore["text"] = "Highscore:\n" + str(self.game.highscore)

        if(self.game.isFinished()):
            for element in [self.root] + self.listLabels:
                element.config(bg = self.bgEndOfGame)
        else:
            for element in [self.root] + self.listLabels:
                element.config(bg = self.bg)

        self.root.update()

class Game:
    def __init__(self):
        self.probability4 = 10

        self.initFileName()
        self.initField()
        self.initValues()

    def initValues(self):
        self.score = 0 # max: 3932164
        self.round = 0
        self.readHighScore()

    def initFileName(self):
        # get directory in which the file is located
        pathDir = os.path.dirname(os.path.abspath(__file__))

        # append specified filename to directory of script
        self.filename = pathDir + "\\" + FILENAME_HIGHSCORE

    def initField(self):
        self.field  = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]

        self.insertRandomNumber()
        self.insertRandomNumber()

    def readHighScore(self):
        try:
            with open(self.filename, "r") as f:
                self.highscore = int(f.readlines()[0].strip())
        except Exception as e:
            print("Can't read highscore from file", FILENAME_HIGHSCORE)
            print("***", e)
            self.highscore = 0

    def writeHighScore(self):
        self.highscore = max(self.highscore, self.score)
        try:
            with open(self.filename, "w") as f:
                f.write(str(self.highscore))
        except Exception as e:
            print("Can't write highscore", self.highscore,
                  "into file", FILENAME_HIGHSCORE)
            print("***", e)

    def move(self, direction):
        # direction has to be 0,1,2,3 (N,E,S,W)
        # return True / False
        new = [self.__move_north,
               self.__move_east,
               self.__move_south,
               self.__move_west][direction]()
        
        if(self.field != new):
            self.field = new
            self.insertRandomNumber()
            self.round += 1
            self.highscore = max(self.score, self.highscore)
            return True
        return False
    
    def __move_north(self):
        new = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        for x in range(0,4):
            # 1. get list without empty fields
            values = []
            for y in range(0,4):
                if(self.field[y][x] != 0): values.append(self.field[y][x])
            # 2. merge
            i = 0
            while(i < len(values)-1):
                if(values[i] == values[i+1]):
                    values[i] *= 2
                    self.score += values[i]
                    del values[i+1]
                i += 1
            # 3. fill numbers in new field
            y = 0
            for number in values:
                new[y][x] = number
                y += 1
        return new

    def __move_west(self):
        new = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        for y in range(0,4):
            # 1. get list without empty fields
            values = []
            for x in range(0,4):
                if(self.field[y][x] != 0): values.append(self.field[y][x])
            # 2. merge
            i = 0
            while(i < len(values)-1):
                if(values[i] == values[i+1]):
                    values[i] *= 2
                    self.score += values[i]
                    del values[i+1]
                i += 1
            # 3. fill numbers in new field
            x = 0
            for number in values:
                new[y][x] = number
                x += 1
        return new

    def __move_south(self):
        new = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        for x in range(0,4):
            # 1. get list without empty fields
            values = []
            for y in range(3,-1,-1):
                if(self.field[y][x] != 0): values.append(self.field[y][x])
            # 2. merge
            i = 0
            while(i < len(values)-1):
                if(values[i] == values[i+1]):
                    values[i] *= 2
                    self.score += values[i]
                    del values[i+1]
                i += 1
            # 3. fill numbers in new field
            y = 3
            for number in values:
                new[y][x] = number
                y -= 1
        return new

    def __move_east(self):
        new = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        for y in range(0,4):
            # 1. get list without empty fields
            values = []
            for x in range(3,-1,-1):
                if(self.field[y][x] != 0): values.append(self.field[y][x])
            # 2. merge
            i = 0
            while(i < len(values)-1):
                if(values[i] == values[i+1]):
                    values[i] *= 2
                    self.score += values[i]
                    del values[i+1]
                i += 1
            # 3. fill numbers in new field
            x = 3
            for number in values:
                new[y][x] = number
                x -= 1
        return new

    def insertRandomNumber(self):
        # insert 2 or 4 at random field (must be free)
        nulls = self.getNumNullValues()
        if(nulls == 0): return False
        r = randint(1, nulls)
        counter0 = 0
        for y in range(4):
            for x in range(4):
                if(self.field[y][x] == 0):
                    counter0 += 1
                    if(r == counter0):
                        if(randint(1,100) <= self.probability4):
                            self.field[y][x] = 4
                        else:
                            self.field[y][x] = 2
                        return (y,x)

    def getNumNullValues(self):
        num = 0
        for row in self.field:
            for number in row:
                if(number == 0): num += 1
        return num

    def isFinished(self):
        if(self.getNumNullValues() == 0):
            # every field is filled, now check for possible merging
            for y in range(0,4):
                for x in range(0,4):
                    if(x != 3):
                        if(self.field[y][x] == self.field[y][x+1]):
                            return False # merging is possible
                    if(y != 3):
                        if(self.field[y][x] == self.field[y+1][x]):
                            return False # merging is possible
            return True
        else:
            # some empty fields
            return False

    def show(self):
        print("Score:", self.score,
              "Round:", self.round,
              "HighScore:", self.highscore,
              self.field)
        # get max number
        maxnum = 0
        for row in self.field:
            for number in row:
                maxnum = max(maxnum, number)
        maxlen = len(str(maxnum))
        # print
        for row in self.field:
            for number in row:
                if(number):
                    print(" "*(maxlen-len(str(number)))+str(number), end=" ")
                else:
                    print(" "*maxlen, end=" ")
            print("")

gui = UI()
